# app/backend/scripts/update_view_counts.py
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://proj2:1234@localhost:5433/OTT_rec"
UPDATE_VIEW_COUNT_SQL = """
UPDATE movie
SET view_count = subquery.count
FROM (
    SELECT movie_id, COUNT(*) as count
    FROM rating
    GROUP BY movie_id
) AS subquery
WHERE movie.movie_id = subquery.movie_id;
"""

def update_movie_view_counts():
    """DB에 저장된 평점 정보를 바탕으로 영화별 시청 횟수를 계산하여 업데이트합니다."""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            print("영화별 시청 횟수 업데이트 시작...")
            connection.execution_options(isolation_level="AUTOCOMMIT")
            connection.execute(text(UPDATE_VIEW_COUNT_SQL))
            print("✅ 시청 횟수 업데이트 완료!")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    update_movie_view_counts()