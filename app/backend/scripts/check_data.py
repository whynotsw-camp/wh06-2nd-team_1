# app/backend/scripts/check_data.py
import pandas as pd

USER_CSV_PATH = 'backend/data/users.csv'

def check_for_duplicates():
    """
    users.csv 파일에 중복된 user_id가 있는지 확인합니다.
    """
    try:
        print(f"'{USER_CSV_PATH}' 파일을 읽고 중복 데이터를 확인합니다...")
        users_df = pd.read_csv(USER_CSV_PATH)
        
        # 'user_id' 컬럼 기준으로 중복된 모든 행을 찾습니다.
        duplicates = users_df[users_df.duplicated(subset=['user_id'], keep=False)]
        
        if not duplicates.empty:
            print(f"❌ 문제 발견: users.csv 파일에 {len(duplicates)}개의 중복된 행이 존재합니다.")
            print("이것이 UniqueViolation 오류의 원인입니다.")
            print("중복 데이터 미리보기:")
            print(duplicates.head())
        else:
            print("✅ 확인 완료: users.csv 파일에 중복된 user_id가 없습니다.")

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    check_for_duplicates()