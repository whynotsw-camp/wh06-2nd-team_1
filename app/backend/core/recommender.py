# app/backend/core/recommender.py

from collections import Counter
from sqlalchemy.orm import Session
from backend.db import crud
import json

def recommend_ott_platform(db: Session, movie_title_list: list[str]) -> tuple[str, dict]:
    """
    DB의 ott_list 컬럼을 기반으로, 가장 많이 언급된 OTT 플랫폼을 추천하고,
    영화별 OTT 리스트를 함께 반환합니다.
    """
    print("\n--- 🎬 OTT 플랫폼 추천 로직 (DB 기반) 시작 🎬 ---")

    movie_ott_map = {}
    all_otts = []

    for title in movie_title_list:
        movie = db.query(crud.models.Movie).filter(crud.models.Movie.title == title).first()
        if not movie or not movie.ott_list:
            continue

        ott_uuids = [uuid for uuid, flag in movie.ott_list.items() if flag]
        movie_ott_map[title] = ott_uuids
        all_otts.extend(ott_uuids)

    if not all_otts:
        print("❌ OTT 정보 없음")
        return "추천 OTT 없음", movie_ott_map

    # 가장 많이 언급된 OTT UUID 추출
    ott_counter = Counter(all_otts)
    top_ott_uuid, _ = ott_counter.most_common(1)[0]

    # UUID → 이름 매핑
    all_ott_objs = crud.get_all_ott_platforms(db)
    uuid_to_name = {str(o.ott_id): o.ott_name for o in all_ott_objs}
    top_ott_name = uuid_to_name.get(top_ott_uuid, "알 수 없음")

    # 이름으로 변환된 결과 생성
    movie_ott_name_map = {
        title: [uuid_to_name.get(uid, "Unknown") for uid in otts]
        for title, otts in movie_ott_map.items()
    }

    print(json.dumps(movie_ott_name_map, indent=2, ensure_ascii=False))
    print(f"🎯 최종 추천 OTT: {top_ott_name}")

    return top_ott_name, movie_ott_name_map
