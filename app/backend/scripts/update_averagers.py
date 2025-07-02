# app/backend/scripts/update_averages.py
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://proj2:1234@localhost:5433/OTT_rec"
UPDATE_AVG_RATING_SQL = """
UPDATE movie
SET rating_avg = subquery.avg_rating
FROM (
    SELECT movie_id, AVG(rating) as avg_rating
    FROM rating
    GROUP BY movie_id
) AS subquery
WHERE movie.movie_id = subquery.movie_id;
"""

def update_rating_averages():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            print("평균 평점 업데이트 시작...")
            connection.execution_options(isolation_level="AUTOCOMMIT")
            connection.execute(text(UPDATE_AVG_RATING_SQL))
            print("✅ 평균 평점 업데이트 완료!")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    update_rating_averages()