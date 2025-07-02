-- 데이터베이스 초기화를 위한 SQL 스크립트

-- UUID 함수를 사용하기 위해 uuid-ossp 확장 모듈을 활성화합니다.
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. user 테이블: Streamlit 설문을 통해 수집된 신규 사용자 정보
CREATE TABLE "user" (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    gender VARCHAR(10),
    age INTEGER,
    level_of_edu VARCHAR(50),
    income VARCHAR(50),
    ott_consume_freq VARCHAR(50),
    pref_movie_list TEXT[],
    -- 새로운 설문 항목들
    current_otts TEXT[],
    watch_with VARCHAR(50),
    preferred_movie_genres TEXT[],
    preferred_tv_genres TEXT[],
    important_values TEXT[]
);
COMMENT ON TABLE "user" IS 'Streamlit 설문을 통해 수집된 신규 사용자 정보';


-- 2. movie_lens_data 테이블: 기존 MovieLens 사용자 데이터
CREATE TABLE movie_lens_data (
    ml_user_id SERIAL PRIMARY KEY,
    gender VARCHAR(10),
    age INTEGER
);
COMMENT ON TABLE movie_lens_data IS '기존 MovieLens 사용자 데이터';


-- 3. movie 테이블: 영화 정보 및 OTT 플랫폼 정보
CREATE TABLE movie (
    movie_id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    rating_avg NUMERIC(3, 2),
    view_count INTEGER DEFAULT 0,
    ott_list JSONB -- OTT 플랫폼 정보를 JSONB 타입으로 저장
);
COMMENT ON TABLE movie IS '영화 정보 및 상영 플랫폼 정보 (JSONB)';


-- 4. rating 테이블: 모델이 예측한 사용자별 영화 평점
CREATE TABLE rating (
    rating_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ml_user_id INTEGER REFERENCES movie_lens_data(ml_user_id),
    movie_id INTEGER REFERENCES movie(movie_id),
    -- 평점은 0.0에서 5.0 사이의 값만 허용
    rating NUMERIC(3, 2) CHECK (rating >= 0.0 AND rating <= 5.0)
);
COMMENT ON TABLE rating IS '모델이 예측한 사용자별 영화 평점';


-- 5. similarity 테이블: 신규 사용자와 가장 유사한 MovieLens 사용자 매칭 결과
CREATE TABLE similarity (
    user_id UUID PRIMARY KEY REFERENCES "user"(user_id),
    ml_user_id INTEGER REFERENCES movie_lens_data(ml_user_id),
    overlapped_movies TEXT[]
);
COMMENT ON TABLE similarity IS '신규 사용자와 가장 유사한 MovieLens 사용자 매칭 결과';


-- 6. ott_table 테이블: OTT 플랫폼 정보 및 추천 통계
CREATE TABLE ott_table (
    ott_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), -- 기본 키를 UUID로 변경
    ott_name VARCHAR(50) UNIQUE NOT NULL,
    recommendation_count INTEGER DEFAULT 0
);
COMMENT ON TABLE ott_table IS 'OTT 플랫폼별 정보 및 추천 횟수 통계';