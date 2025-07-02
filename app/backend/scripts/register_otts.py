# app/backend/scripts/register_otts.py 파일 전체를 아래 코드로 교체하세요.

import sys
import os

# ▼▼▼▼▼▼▼▼▼▼ 이 부분은 삭제하거나 그대로 두셔도 괜찮습니다. ▼▼▼▼▼▼▼▼▼▼
# (-m 옵션으로 실행할 것이므로 사실상 필요 없습니다.)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)
# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

from app.backend.db.database import SessionLocal
from app.backend.db import crud

# --- DB에 등록할 OTT 플랫폼 목록 ---
OTT_PLATFORMS = [
    "Netflix",
    "Disney+",
    "Tving",
    "Wavve",
    "Coupang Play",
    "Watcha",
]

def register_initial_otts():
    """
    미리 정의된 OTT 플랫폼 목록을 데이터베이스의 ott_table에 등록합니다.
    세션과 트랜잭션을 직접 관리하여 안정적으로 처리합니다.
    """
    print("--- OTT 플랫폼 등록 스크립트 시작 ---")
    db = SessionLocal()
    
    try:
        total_registered = 0
        for ott_name in OTT_PLATFORMS:
            # crud 함수는 이제 (객체, 생성여부)를 반환합니다.
            ott, created = crud.get_or_create_ott(db, ott_name)
            
            if created:
                print(f"✅ '{ott_name}'이(가) 새롭게 등록될 예정입니다. (ID: {ott.ott_id})")
                total_registered += 1
            else:
                print(f"☑️ '{ott_name}'은(는) 이미 등록되어 있습니다.")
        
        # 모든 작업이 끝난 후, 마지막에 한 번만 commit 합니다.
        print("\n최종 변경사항을 데이터베이스에 저장합니다...")
        db.commit()
        print("저장 완료!")

        print("\n--- 스크립트 완료 ---")
        print(f"총 {total_registered}개의 신규 OTT 플랫폼이 처리되었습니다.")

    except Exception as e:
        # 오류 발생 시, 모든 변경사항을 되돌립니다.
        print(f"\n🚨 오류가 발생하여 작업을 롤백합니다: {e}")
        db.rollback()
    finally:
        # 작업이 성공하든 실패하든, 세션을 항상 닫아줍니다.
        db.close()


if __name__ == "__main__":
    register_initial_otts()