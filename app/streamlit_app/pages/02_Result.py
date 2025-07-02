# app/streamlit_app/pages/02_Result.py

import streamlit as st
import os, sys

# ✅ 경로 설정
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# ✅ 모듈 임포트
from backend.db.database import SessionLocal
from backend.db import crud
from backend.core import user_matching
from backend.core.recommender import recommend_ott_platform

# ✅ 페이지 설정
st.set_page_config(page_title="OTT 추천 결과", page_icon="📊")
st.title("📊 OTT 추천 결과 보기")
st.markdown("---")

# 🔑 사용자 ID 입력
user_id = st.text_input("설문 완료 후 발급받은 사용자 ID를 입력하세요:", placeholder="예: 7fa4e7a4-...")

if st.button("추천 결과 확인") and user_id:
    db = SessionLocal()
    try:
        user = crud.get_user(db, user_id=user_id)
        if not user:
            st.error("해당 사용자 ID를 찾을 수 없습니다.")
        else:
            matched_ml_user_id, similarity = user_matching.find_similar_user(db, user_id)
            if not matched_ml_user_id:
                st.warning("유사 사용자를 찾지 못했습니다.")
            else:
                st.success(f"매칭된 MovieLens 사용자: {matched_ml_user_id} (유사도: {similarity:.2%})")

                watched = crud.get_watched_movies_by_ml_user(db, matched_ml_user_id)
                watched = [(mid, float(r)) for mid, r in watched if r >= 4.0]
                watched_ids = [mid for mid, _ in watched]

                recommended_movies = crud.get_recommended_movies_with_ott(db, watched_ids)
                movie_titles = [m.title for m in recommended_movies]

                if not movie_titles:
                    st.error("추천할 영화가 없습니다 (OTT 정보 없음).")
                else:
                    final_ott, movie_ott_map = recommend_ott_platform(db, movie_titles)

                    st.subheader(f"🏆 최적의 OTT 플랫폼: **{final_ott}**")
                    st.markdown("---")

                    st.markdown("### 🎬 추천 영화 및 방영 OTT")
                    for title, otts in movie_ott_map.items():
                        otts_display = ", ".join(otts) if otts else "❌ 없음"
                        st.write(f"- **{title}** → {otts_display}")
    except Exception as e:
        st.error(f"오류 발생: {e}")
    finally:
        db.close()
