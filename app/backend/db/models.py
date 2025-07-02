# app/backend/db/models.py

from sqlalchemy import (
    Column, Integer, String, ARRAY, TEXT, NUMERIC, 
    ForeignKey, func, CheckConstraint
)
# 필요한 타입들을 추가로 import 합니다.
from sqlalchemy.dialects.postgresql import UUID, JSONB 
from .database import Base

class User(Base):
    """
    Streamlit 설문을 통해 수집된 신규 사용자 정보 모델
    - 새로운 설문 항목들을 포함합니다.
    """
    __tablename__ = "user"

    user_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    gender = Column(String(10))
    age = Column(Integer)
    level_of_edu = Column(String(50))
    income = Column(String(50))
    ott_consume_freq = Column(String(50))
    pref_movie_list = Column(ARRAY(TEXT))
    
    # 새로운 설문 항목 컬럼
    current_otts = Column(ARRAY(TEXT))
    watch_with = Column(String(50))
    preferred_movie_genres = Column(ARRAY(TEXT))
    preferred_tv_genres = Column(ARRAY(TEXT))
    important_values = Column(ARRAY(TEXT))

class MovieLensUser(Base):
    """기존 MovieLens 사용자 데이터 모델"""
    __tablename__ = "movie_lens_data"
    
    ml_user_id = Column(Integer, primary_key=True)
    gender = Column(String(10))
    age = Column(Integer)

class Movie(Base):
    """영화 정보 및 OTT 플랫폼 정보 모델"""
    __tablename__ = "movie"
    
    movie_id = Column(Integer, primary_key=True)
    title = Column(String(255))
    rating_avg = Column(NUMERIC(3, 2))
    view_count = Column(Integer, default=0)
    # platform 컬럼을 제거하고 ott_list를 JSONB 타입으로 지정합니다.
    ott_list = Column(JSONB)

class Rating(Base):
    """모델이 예측한 사용자별 영화 평점 모델"""
    __tablename__ = "rating"
    
    rating_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    ml_user_id = Column(Integer, ForeignKey("movie_lens_data.ml_user_id"))
    movie_id = Column(Integer, ForeignKey("movie.movie_id"))
    rating = Column(NUMERIC(3, 2), CheckConstraint('rating >= 0.0 AND rating <= 5.0', name='rating_check'))

class Similarity(Base):
    """신규 사용자와 MovieLens 사용자 매칭 결과 모델"""
    __tablename__ = "similarity"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.user_id"), primary_key=True)
    ml_user_id = Column(Integer, ForeignKey("movie_lens_data.ml_user_id"))
    overlapped_movies = Column(ARRAY(TEXT))

class OttTable(Base):
    """OTT 플랫폼 정보 및 추천 통계 모델"""
    __tablename__ = "ott_table"
    
    # ott_id를 UUID로 변경하고 서버 기본값을 설정합니다.
    ott_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    ott_name = Column(String(50), unique=True)
    recommendation_count = Column(Integer, default=0)