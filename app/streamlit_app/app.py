import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="개인화 영화 추천 시스템",
    page_icon="🎬",
    layout="wide",
)

# 제목
st.title("🎬 개인화 영화 및 OTT 추천 시스템")

# 프로젝트 설명
st.markdown("---")
st.subheader("당신만을 위한 최고의 영화와 OTT 플랫폼을 찾아보세요!")
st.write(
    """
    이 서비스는 간단한 설문을 통해 사용자의 숨겨진 영화 취향을 분석합니다.
    분석된 데이터를 기반으로, 수많은 영화 중 당신이 가장 좋아할 만한 작품들과
    가장 잘 맞는 OTT 서비스를 추천해 드립니다.
    """
)
st.markdown("---")

# 사용 안내
st.info("👈 왼쪽 사이드바에서 **'Survey'** 페이지로 이동하여 추천 서비스를 시작하세요!", icon="ℹ️")