# app/streamlit_app/pages/01_Survey.py

import streamlit as st
import sys
import os

# --- 경로 추가 (가장 위) ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.db.database import SessionLocal
from backend.db import crud
from backend.core import user_matching # 유사 사용자 매칭 함수 임포트

# --- 페이지 로드 시 한 번만 영화 목록 가져오기 ---
@st.cache_data
def load_movies():
    db = SessionLocal()
    try:
        movies = crud.get_movies_for_survey(db, limit=100)
        movies.sort(key=lambda x: x.title)
        return movies
    finally:
        db.close()

# --- 페이지 상태 관리를 위한 session_state 초기화 ---
if 'selected_movies' not in st.session_state:
    st.session_state.selected_movies = {}

# --- 앱 UI 구성 ---
movie_options = load_movies()

st.title("🙋‍♂️ 당신만을 위한 OTT 추천 설문")
st.info("정확한 추천을 위해 아래 설문에 상세히 답변해주시면 감사하겠습니다. 답변 내용은 추천 외 다른 목적으로 사용되지 않습니다.")

with st.form("user_survey_form"):
    # --- 섹션 1: 기본 정보 ---
    st.subheader("1. 기본 정보를 알려주세요.")
    c1, c2 = st.columns(2)
    with c1:
        gender = st.radio("성별", ("남성", "여성"), horizontal=True)
        level_of_edu = st.selectbox("최종 학력", ("고등학교 졸업 이하", "전문학사", "학사 재학", "학사 졸업", "석사 이상"))
    with c2:
        age = st.number_input("나이 (만)", min_value=10, max_value=100, step=1)
        income = st.selectbox("연소득 (세전)", ("2,000만원 미만", "2,000만원 - 4,000만원 미만", "4,000만원 - 6,000만원 미만", "6,000만원 - 8,000만원 미만", "1억원 이상"))
    
    st.divider()

    # --- 섹션 2: OTT 이용 행태 ---
    st.subheader("2. 평소 OTT를 어떻게 이용하시나요?")
    current_otts = st.multiselect("현재 구독 중인 OTT를 모두 선택해주세요. (없으면 선택 안함)",
                                 ["넷플릭스", "티빙", "쿠팡플레이", "웨이브", "디즈니+", "왓챠", "Apple TV+"])
    watch_time = st.radio("주로 언제 콘텐츠를 시청하시나요?",
                         ("출/퇴근 및 이동 중에", "잠들기 전에", "주말이나 휴일에 몰아서", "일상적으로 항상"), horizontal=True)
    watch_with = st.radio("주로 누구와 함께 시청하시나요?",
                         ("혼자", "친구/연인과 함께", "가족과 함께 (자녀 포함)"), horizontal=True)
    
    st.divider()

    # --- ✨ 섹션 3: 콘텐츠 취향 (수정된 부분) ✨ ---
    st.subheader("3. 어떤 콘텐츠를 즐겨보시나요?")

    # 선호 영화 장르
    preferred_movie_genres = st.multiselect(
        "선호하는 '영화' 장르를 모두 선택해주세요.",
        ["액션", "코미디", "로맨스", "스릴러/미스터리", "SF/판타지", "드라마", "공포", "애니메이션"]
    )

    # 선호 TV 프로그램 장르
    preferred_tv_genres = st.multiselect(
        "선호하는 'TV 프로그램' 장르를 모두 선택해주세요.",
        ["한국 드라마", "미국/영국 드라마", "일본/기타 국가 드라마", "시트콤/코미디", "리얼리티/서바이벌", "다큐멘터리", "예능"]
    )
    
    st.markdown("##### 좋아하는 영화를 5개 이상 선택해주세요.")
    cols_per_row = 5
    cols = st.columns(cols_per_row)
    for i, movie in enumerate(movie_options):
        with cols[i % cols_per_row]:
            with st.container(border=True):
                title = movie.title
                if len(title) > 30: title = title[:28] + "..."
                st.caption(title)
                st.write("")
                st.session_state.selected_movies[movie.movie_id] = st.checkbox("선택", key=f"movie_{movie.movie_id}")

    st.divider()

    # --- 섹션 4: OTT 선택 기준 ---
    st.subheader("4. OTT 서비스를 선택할 때 무엇을 중요하게 생각하시나요?")
    important_values = st.multiselect("가장 중요하게 생각하는 가치를 2가지 선택해주세요.",
                                      ["저렴한 구독료", "독점 오리지널 콘텐츠", "최신 영화/드라마 업데이트 속도", "다양한 콘텐츠 라이브러리", "4K/고화질 지원", "사용하기 편리한 앱"])

    # --- 제출 버튼 ---
    submitted = st.form_submit_button("나에게 맞는 OTT 추천받기")

# --- 제출 후 로직 처리 ---
if submitted:
    # 데이터 유효성 검사
    pref_movie_list = [movie.title for movie in movie_options if st.session_state.selected_movies.get(movie.movie_id)]
    
    # ✨ 유효성 검사 로직 수정 ✨
    if len(pref_movie_list) < 5:
        st.error("좋아하는 영화를 5개 이상 선택해주세요!")
    elif len(preferred_movie_genres) < 1 or len(preferred_tv_genres) < 1:
        st.error("영화와 TV 프로그램 장르를 각각 1개 이상 선택해주세요!")
    elif len(important_values) != 2:
        st.error("중요하게 생각하는 가치를 정확히 2개 선택해주세요!")
    else:
        # ✨ DB에 저장할 데이터 구성 수정 ✨
        user_data = {
            "gender": "Male" if gender == "남성" else "Female",
            "age": age, "level_of_edu": level_of_edu, "income": income,
            "ott_consume_freq": watch_time, "pref_movie_list": pref_movie_list,
            "current_otts": current_otts, "watch_with": watch_with,
            "preferred_movie_genres": preferred_movie_genres, # 수정된 필드
            "preferred_tv_genres": preferred_tv_genres,       # 수정된 필드
            "important_values": important_values,
        }
        
        db = SessionLocal()
        try:
            # 1. 설문 데이터 DB에 저장
            new_user = crud.create_user(db, user_data=user_data)
            st.success(f"설문이 성공적으로 제출되었습니다! (사용자 ID: {new_user.user_id})")
            st.balloons()

            # 2. 유사 사용자 매칭 시작
            with st.spinner('취향이 비슷한 사용자를 찾고 있습니다...'):
                matched_user_id, similarity_score = user_matching.find_similar_user(
                    db=db, new_user_id=str(new_user.user_id)
                )
            
            # 3. 매칭 결과 출력
            if matched_user_id:
                st.success(f"매칭 완료! 당신과 가장 비슷한 사용자는 ID {matched_user_id} 입니다. (유사도: {similarity_score:.2%})")
                st.info("매칭 결과는 서버의 app/data/sim_user_id_and_meta.jsonl 파일에 저장되었습니다.")
            else:
                st.warning("아쉽지만 비슷한 사용자를 찾지 못했습니다.")
        except Exception as e:
            st.error(f"데이터 처리 중 오류가 발생했습니다: {e}")
        finally:
            db.close()