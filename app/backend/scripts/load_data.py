# app/backend/scripts/load_data.py
import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://proj2:1234@localhost:5433/OTT_rec"
CLEAR_TABLES_SQL = """
TRUNCATE "user", movie_lens_data, movie, rating, similarity, ott_table RESTART IDENTITY CASCADE;
"""

def final_load_data():
    try:
        engine = create_engine(DATABASE_URL)

        with engine.connect() as connection:
            print("테스트에서 검증된 방식으로 모든 테이블 데이터를 삭제합니다...")
            connection.execution_options(isolation_level="AUTOCOMMIT")
            connection.execute(text(CLEAR_TABLES_SQL))
            print("✅ 모든 테이블 초기화 완료.")

        print("\n모든 CSV 파일을 메모리로 읽어옵니다...")
        users_df = pd.read_csv('backend/data/users.csv').rename(columns={'user_id': 'ml_user_id'})
        movies_df = pd.read_csv('backend/data/movies.csv').rename(columns={'movieId': 'movie_id'})
        ratings_df = pd.read_csv('backend/data/ratings.csv').rename(columns={'userId': 'ml_user_id', 'movieId': 'movie_id'})
        print("✅ 파일 읽기 완료.")
        
        users_df.drop_duplicates(subset=['ml_user_id'], keep='first', inplace=True)
        print(f"✅ users.csv 파일에서 중복 사용자를 제거했습니다.")

        # --- ✨ 이 부분을 추가했습니다 ✨ ---
        print("\n평점 데이터 유효성 검사를 시작합니다...")
        original_ratings_count = len(ratings_df)
        # 평점이 1.0 미만이거나 5.0을 초과하는 데이터를 제거합니다.
        ratings_df = ratings_df[(ratings_df['rating'] >= 1.0) & (ratings_df['rating'] <= 5.0)]
        validated_ratings_count = len(ratings_df)
        print(f"✅ 유효하지 않은 평점 데이터 {original_ratings_count - validated_ratings_count}건을 제거했습니다.")
        # --- ✨ 여기까지 --- ✨

        print("\n데이터 정제를 시작합니다...")
        valid_user_ids = set(users_df['ml_user_id'])
        valid_movie_ids = set(movies_df['movie_id'])
        ratings_df = ratings_df[
            ratings_df['ml_user_id'].isin(valid_user_ids) & 
            ratings_df['movie_id'].isin(valid_movie_ids)
        ]
        print("✅ 짝이 맞지 않는 평점 데이터 제거 완료.")

        print("\n평점 데이터 10% 샘플링을 시작합니다...")
        ratings_sample_df = ratings_df.sample(frac=0.1, random_state=42)
        print(f"✅ {len(ratings_sample_df)}건 샘플링 완료.")

        final_valid_user_ids = set(ratings_sample_df['ml_user_id'])
        final_valid_movie_ids = set(ratings_sample_df['movie_id'])
        
        users_final_df = users_df[users_df['ml_user_id'].isin(final_valid_user_ids)]
        movies_final_df = movies_df[movies_df['movie_id'].isin(final_valid_movie_ids)]
        print("✅ 최종 사용자 및 영화 데이터 필터링 완료.")

        print("\n최종 데이터 업로드를 시작합니다...")
        users_final_df[['ml_user_id', 'gender', 'age']].to_sql('movie_lens_data', engine, if_exists='append', index=False)
        print("✅ 사용자 데이터 업로드 완료.")
        
        movies_final_df[['movie_id', 'title']].to_sql('movie', engine, if_exists='append', index=False)
        print("✅ 영화 데이터 업로드 완료.")

        ratings_sample_df[['ml_user_id', 'movie_id', 'rating']].to_sql('rating', engine, if_exists='append', index=False)
        print("✅ 평점 데이터 업로드 완료.")

        print("\n🎉 모든 데이터가 성공적으로 업로드되었습니다.")

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    final_load_data()