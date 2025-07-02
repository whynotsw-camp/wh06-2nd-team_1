# app/backend/db/crud.py

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
# ✨ sqlalchemy에서 String과 cast 함수를 함께 import 합니다.
from sqlalchemy import cast, String
from sqlalchemy.dialects.postgresql import JSONB
from . import models

# --- 사용자 설문 관련 함수 ---
def create_user(db: Session, user_data: dict):
    """확장된 사용자 설문 데이터를 받아 DB의 user 테이블에 저장합니다."""
    db_user = models.User(
        gender=user_data["gender"],
        age=user_data["age"],
        level_of_edu=user_data["level_of_edu"],
        income=user_data["income"],
        ott_consume_freq=user_data["ott_consume_freq"],
        pref_movie_list=user_data["pref_movie_list"],
        current_otts=user_data["current_otts"],
        watch_with=user_data["watch_with"],
        preferred_movie_genres=user_data["preferred_movie_genres"],
        preferred_tv_genres=user_data["preferred_tv_genres"],
        important_values=user_data["important_values"]
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_movies_for_survey(db: Session, limit: int = 100):
    """
    설문조사용 영화 목록을 DB에서 가져옵니다.
    시청 횟수 상위 30% 중, 평점 상위 200개 영화에서 무작위로 100개를 선택합니다.
    """
    total_rated_movies = db.query(models.Movie).filter(models.Movie.view_count > 0).count()
    top_30_percent_limit = int(total_rated_movies * 0.3)
    if top_30_percent_limit < 200: # 최소 200개는 확보
        top_30_percent_limit = 200

    top_viewed_subquery = db.query(models.Movie.movie_id)\
                            .filter(models.Movie.view_count > 0)\
                            .order_by(models.Movie.view_count.desc())\
                            .limit(top_30_percent_limit)\
                            .subquery()

    popular_and_high_rated_subquery = db.query(models.Movie.movie_id)\
                                        .join(top_viewed_subquery, models.Movie.movie_id == top_viewed_subquery.c.movie_id)\
                                        .filter(models.Movie.rating_avg.isnot(None))\
                                        .order_by(models.Movie.rating_avg.desc())\
                                        .limit(200)\
                                        .subquery()

    return db.query(models.Movie)\
             .join(popular_and_high_rated_subquery, models.Movie.movie_id == popular_and_high_rated_subquery.c.movie_id)\
             .order_by(func.random())\
             .limit(limit)\
             .all()

# --- 유사 사용자 매칭에 필요한 함수들 ---
def get_user(db: Session, user_id: str):
    """ID로 특정 신규 사용자의 정보를 조회합니다."""
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_all_ml_users(db: Session):
    """모든 MovieLens 사용자 정보를 조회합니다."""
    return db.query(models.MovieLensUser).all()

def get_all_ratings(db: Session):
    """모든 평점 정보를 조회합니다."""
    return db.query(models.Rating).all()

def get_movie_id_by_title(db: Session, title: str):
    """영화 제목으로 영화 ID를 조회합니다."""
    movie = db.query(models.Movie).filter(models.Movie.title == title).first()
    return movie.movie_id if movie else None

def get_ml_user(db: Session, ml_user_id: int):
    """ID로 특정 MovieLens 사용자의 정보를 조회합니다."""
    return db.query(models.MovieLensUser).filter(models.MovieLensUser.ml_user_id == ml_user_id).first()

def get_watched_movies_by_ml_user(db: Session, ml_user_id: int):
    """특정 MovieLens 사용자가 시청(평가)한 영화 목록을 조회합니다."""
    return db.query(models.Rating.movie_id, models.Rating.rating).filter(models.Rating.ml_user_id == ml_user_id).all()

def create_similarity(db: Session, user_id: str, ml_user_id: int, overlapped_movies: list):
    """유사도 매칭 결과를 similarity 테이블에 저장합니다."""
    db_similarity = models.Similarity(
        user_id=user_id,
        ml_user_id=ml_user_id,
        overlapped_movies=overlapped_movies
    )
    db.add(db_similarity)
    db.commit()
    db.refresh(db_similarity)
    return db_similarity


# --- ✨ OTT 추천 및 데이터 관리를 위한 새로운 함수들 ✨ ---

def get_all_movies(db: Session):
    """DB에 있는 모든 영화 정보를 가져옵니다. (OTT 정보 업데이트용)"""
    return db.query(models.Movie).all()

def update_movie_ott_list(db: Session, movie_id: int, ott_data: dict):
    """
    특정 영화의 ott_list (JSONB) 컬럼을 업데이트합니다.
    Google 검색 API 결과를 이 함수를 통해 DB에 저장할 수 있습니다.
    """
    db.query(models.Movie).filter(models.Movie.movie_id == movie_id).update({"ott_list": ott_data})
    db.commit()

def get_recommended_movies_with_ott(db: Session, movie_ids: list[int]):
    """
    추천된 영화 ID 목록을 받아, ott_list가 비어있지 않은 영화만 반환합니다.
    JSONB 컬럼의 값이 NULL이 아니고, 빈 JSON '{}'이 아닌 영화를 필터링합니다.
    """
    return db.query(models.Movie)\
             .filter(models.Movie.movie_id.in_(movie_ids))\
             .filter(models.Movie.ott_list.isnot(None))\
             .filter(cast(models.Movie.ott_list, String) != '{}')\
             .all()

def get_or_create_ott(db: Session, ott_name: str):
    """
    주어진 이름의 OTT가 DB에 있으면 가져오고, 없으면 새로 생성합니다.
    - 객체를 생성했는지 여부(True/False)를 함께 반환합니다.
    - DB 최종 저장은 이 함수를 호출한 쪽에서 처리합니다.
    """
    created = False
    db_ott = db.query(models.OttTable).filter(models.OttTable.ott_name == ott_name).first()

    if not db_ott:
        created = True
        db_ott = models.OttTable(ott_name=ott_name)
        db.add(db_ott)
        # flush()를 통해 DB에 INSERT 쿼리를 보내고,
        # 서버에서 생성된 UUID를 db_ott 객체에 반영합니다.
        db.flush()

    return db_ott, created

def increment_ott_recommendation_count(db: Session, ott_name: str):
    """
    특정 OTT 플랫폼의 추천 횟수(recommendation_count)를 1 증가시킵니다.
    """
    db_ott = db.query(models.OttTable).filter(models.OttTable.ott_name == ott_name).first()
    if db_ott:
        db_ott.recommendation_count += 1
        db.commit()
        
def get_all_ott_platforms(db: Session):
    """
    ott_table에 있는 모든 OTT 이름과 UUID를 가져옵니다.
    """
    return db.query(models.OttTable).all()