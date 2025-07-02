import sys
import os
import asyncio
from dotenv import load_dotenv
from time import sleep

# --- 경로 설정 ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# --- 환경 변수 로드 ---
load_dotenv(dotenv_path=os.path.join(project_root, "app", "env", ".env"))

# --- 내부 모듈 import ---
from app.backend.db.database import SessionLocal
from app.backend.db import crud
from app.backend.services.ott_search import OTTSearcher


class OTTUpdater:
    def __init__(self, api_key, cse_id, target_ott, concurrency=5, timeout=15, batch_size=30, pause_sec=3):
        self.searcher = OTTSearcher(api_key=api_key, cse_id=cse_id)
        self.target_ott = target_ott
        self.sem = asyncio.Semaphore(concurrency)
        self.timeout = timeout
        self.batch_size = batch_size
        self.pause_sec = pause_sec
        self.ott_name_map = {}

    def load_ott_map(self):
        db = SessionLocal()
        try:
            ott_rows = crud.get_all_ott_platforms(db)
            self.ott_name_map = {row.ott_name: str(row.ott_id) for row in ott_rows}
        finally:
            db.close()

    async def timeout_wrapper(self, coro):
        try:
            return await asyncio.wait_for(coro, timeout=self.timeout)
        except asyncio.TimeoutError:
            return f"⏱️ Timeout after {self.timeout}s"

    async def update_single_movie(self, movie):
        async with self.sem:
            db = SessionLocal()
            try:
                if movie.ott_list:
                    return  # 이미 저장된 경우 skip

                print(f"🔍 '{movie.title}' 검색 중...")
                result = await self.timeout_wrapper(
                    asyncio.to_thread(self.searcher.find, movie.title, self.target_ott)
                )

                if isinstance(result, str):
                    print(f"🚨 타임아웃 - {movie.title}: {result}")
                    return

                uuid_result = {
                    self.ott_name_map[ott]: val
                    for ott, val in result.items()
                    if ott in self.ott_name_map
                }

                await asyncio.to_thread(crud.update_movie_ott_list, db, movie.movie_id, uuid_result)
                print(f"✅ 완료: {movie.title} → {uuid_result}")

            except Exception as e:
                print(f"🚨 기타 오류 - {movie.title}: {type(e).__name__} - {e}")
            finally:
                db.close()

    async def run(self):
        print("🎬 병렬 OTT 정보 업데이트 시작")
        self.load_ott_map()

        db = SessionLocal()
        try:
            movies = crud.get_all_movies(db)
        finally:
            db.close()

        filtered = [m for m in movies if not m.ott_list]
        print(f"🎯 처리 대상 영화 수: {len(filtered)}")

        for i in range(0, len(filtered), self.batch_size):
            batch = filtered[i:i + self.batch_size]
            print(f"🚀 [{i+1} ~ {i+len(batch)}]번 영화 처리 중...")

            tasks = [self.update_single_movie(m) for m in batch]
            await asyncio.gather(*tasks, return_exceptions=True)

            if i + self.batch_size < len(filtered):
                print(f"⏸️ {self.pause_sec}초 대기 중 (rate limit 회피)...")
                await asyncio.sleep(self.pause_sec)

        print("✅ 전체 완료")


if __name__ == "__main__":
    api_key = os.getenv("GEMINI_API_KEY")
    cse_id = os.getenv("CSE_ID")

    if not api_key or not cse_id:
        print("❌ API 키 또는 CSE ID 누락")
        sys.exit(1)

    updater = OTTUpdater(
        api_key=api_key,
        cse_id=cse_id,
        target_ott=["Netflix", "Disney+", "Tving", "Wavve", "Coupang Play", "Watcha"],
        concurrency=3,     # 병렬 요청 개수
        timeout=15,        # 단일 요청 최대 대기 시간
        batch_size=12,     # 30개 단위로 처리
        pause_sec=2,       # 3초 휴식
    )

    asyncio.run(updater.run())
