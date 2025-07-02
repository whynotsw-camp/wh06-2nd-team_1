# app/backend/scripts/test_user_load.py
import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://proj2:1234@localhost:5433/OTT_rec"

def test_single_load():
    """
    오직 users.csv 파일만 읽어서 movie_lens_data 테이블에 넣는 테스트.
    """
    try:
        engine = create_engine(DATABASE_URL)
        
        # 1. 테스트 전 관련 테이블을 깨끗하게 비웁니다.
        with engine.connect() as connection:
            print("테스트를 위해 관련 테이블의 데이터를 삭제합니다...")
            # rating, similarity 테이블이 movie_lens_data를 참조하므로 CASCADE 옵션으로 함께 비움
            connection.execution_options(isolation_level="AUTOCOMMIT")
            connection.execute(text('TRUNCATE TABLE movie_lens_data RESTART IDENTITY CASCADE;'))
            print("✅ 테이블 초기화 완료.")

        # 2. users.csv 파일을 읽고 중복을 제거합니다.
        print("\nusers.csv 파일을 읽습니다...")
        users_df = pd.read_csv('backend/data/users.csv').rename(columns={'user_id': 'ml_user_id'})
        
        rows_before = len(users_df)
        users_df.drop_duplicates(subset=['ml_user_id'], keep='first', inplace=True)
        rows_after = len(users_df)
        
        if rows_before > rows_after:
             print(f"-> 파일 내 중복 데이터 {rows_before - rows_after}건을 제거했습니다.")
        
        print(f"✅ 총 {rows_after}명의 고유한 사용자 데이터를 준비했습니다.")

        # 3. 데이터베이스에 업로드합니다.
        print("\nmovie_lens_data 테이블에 데이터 업로드를 시도합니다...")
        users_df[['ml_user_id', 'gender', 'age']].to_sql(
            'movie_lens_data', 
            engine, 
            if_exists='append', 
            index=False,
            chunksize=10000  # 데이터를 10000개씩 나눠서 전송
        )
        print("🎉 테스트 성공: 사용자 데이터가 오류 없이 업로드되었습니다.")

    except Exception as e:
        print(f"\n❌ 테스트 실패: 오류가 발생했습니다.")
        print(e)

if __name__ == "__main__":
    test_single_load()