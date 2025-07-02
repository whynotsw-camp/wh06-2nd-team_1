# OTT-Navi: 당신을 위한 영화 및 OTT 플랫폼 추천 시스템

## 1. 프로젝트 개요

OTT-Navi는 넘쳐나는 콘텐츠 속에서 사용자가 자신의 취향에 맞는 영화와 최적의 OTT 플랫폼을 쉽게 찾을 수 있도록 돕는 개인화 추천 시스템입니다. 사용자로부터 직접 설문을 통해 취향 데이터를 수집하고, 이를 MovieLens 데이터셋과 연계하여 정교한 추천을 제공합니다.

본 프로젝트는 딥러닝 평점 예측 모델을 활용하여 추천의 정확도를 높이고, 인구통계학적 데이터를 적용하여 추천 성능을 비교 분석하는 PoC(Proof of Concept)를 포함합니다.

## 2. 주요 기능

- **개인화 설문**: 사용자의 인구통계 정보, 영화 선호도, OTT 이용 패턴 등을 수집하는 사용자 친화적 설문 인터페이스 (Streamlit)
    
- **영화 추천**: 딥러닝 협업 필터링 모델을 통해 사용자가 아직 보지 않은 영화의 평점을 예측하고, 평점 순으로 영화 목록을 추천
    
- **OTT 플랫폼 추천**: 추천된 영화 목록을 가장 많이 보유한 OTT 플랫폼을 분석하고, 사용자 데이터에 기반한 가중치를 적용하여 최적의 플랫폼을 추천
    
- **실시간 OTT 정보**: Google 검색 API를 활용하여 영화의 최신 OTT 서비스 여부를 확인하고 데이터베이스에 반영
    

## 3. 시스템 아키텍처

_(실제 아키텍처 다이어그램 이미지 링크를 여기에 추가하세요)_

1. **데이터 수집**: Streamlit으로 구현된 설문 페이지에서 사용자의 프로필과 영화 취향 데이터를 수집합니다.
    
2. **데이터 저장**: 수집된 데이터와 MovieLens 데이터, 모델 예측 결과 등을 PostgreSQL 데이터베이스에 저장합니다.
    
3. **유사 사용자 매칭**: 신규 사용자의 설문 결과를 기반으로, 기존 MovieLens 사용자와의 Jaccard 유사도를 계산하여 가장 비슷한 사용자를 매칭합니다.
    
4. **추천 생성**: 매칭된 사용자의 영화 평점 예측 데이터를 활용하여, 신규 사용자가 좋아할 만한 영화 50편과 최적의 OTT 플랫폼을 추천합니다.
    
5. **결과 시각화**: 추천된 영화 목록과 OTT 플랫폼을 Streamlit 대시보드에 시각적으로 표현하여 사용자에게 제공합니다.
    

## 4. 기술 스택

- **Frontend**: Streamlit
    
- **Backend**: Python, SQLAlchemy
    
- **Database**: PostgreSQL
    
- **ML/Data**: Scikit-learn, Pandas, NumPy
    
- **API**: Google Custom Search API
    
- **Infra**: Docker
    

## 5. 프로젝트 설치 및 실행

### 사전 요구사항

- Python (3.9 이상)
    
- Docker 및 Docker Compose
    
- Google API Key 및 Programmable Search Engine(PSE) ID
    

### 설치 가이드

1. **프로젝트 클론**
    
    Bash
    
    ```
    git clone https://your-repository-url.git
    cd your-project-directory
    ```
    
2. **파이썬 가상환경 생성 및 패키지 설치**
    
    Bash
    
    ```
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
    
3. **Google API 인증 정보 설정** `app/env/credentials.json` 파일을 생성하고 아래 형식에 맞게 내용을 채워주세요.
    
    JSON
    
    ```
    {
      "api_key": "YOUR_GOOGLE_API_KEY",
      "cse_id": "YOUR_PSE_ID"
    }
    ```
    
4. **데이터베이스 실행** 프로젝트 루트 디렉터리에서 Docker Compose를 사용하여 PostgreSQL 데이터베이스를 실행합니다.
    
    Bash
    
    ```
    docker-compose up -d
    ```
    

### 실행 가이드

1. **기본 OTT 목록 등록** `ott_table`에 분석 대상이 될 OTT 플랫폼 목록을 등록합니다.
    
    Bash
    
    ```
    python -m app.backend.scripts.register_otts
    ```
    
2. **(선택) 전체 영화 OTT 정보 업데이트** DB에 저장된 모든 영화에 대해 OTT 서비스 여부를 미리 업데이트합니다. (API 호출이 많으므로 시간이 오래 걸릴 수 있습니다.)
    
    Bash
    
    ```
    python -m app.backend.scripts.update_ott_info
    ```
    
3. **Streamlit 애플리케이션 실행** 메인 애플리케이션을 실행합니다.
    
    Bash
    
    ```
    streamlit run app/frontend/app.py
    ```
    
    실행 후 터미널에 나타나는 URL(예: `http://localhost:8501`)에 접속하여 서비스를 이용할 수 있습니다.
    

## 6. 데이터베이스 스키마

주요 테이블은 다음과 같습니다.

- **user**: 설문을 통해 수집된 신규 사용자 정보
    
- **movie**: 영화 정보 및 OTT 서비스 현황 (`ott_list` JSONB)
    
- **rating**: MovieLens 사용자의 평점 및 모델의 예측 평점
    
- **similarity**: 신규 사용자와 MovieLens 사용자 간의 유사도 매칭 결과
    
- **ott_table**: OTT 플랫폼 정보 및 추천 횟수 통계
    

## 7. 기대 효과 및 한계점

### 기대 효과

- 개인화된 추천을 통해 사용자의 콘텐츠 탐색 시간을 단축하고 만족도를 향상시킬 수 있습니다.
    
- 데이터 기반의 정량적 분석을 통해 효과적인 OTT 플랫폼 구독을 유도할 수 있습니다.
    

### 한계점 및 개선 방향

- **콜드 스타트 문제**: 신규 사용자에 대한 데이터가 설문 결과로 제한되어 있어, 초기 추천의 정확도에 한계가 있습니다.
    
- **데이터 희소성**: MovieLens 데이터셋에 존재하지 않는 최신 영화나 비주류 영화에 대한 추천이 어렵습니다.
    
- **향후 개선**: 실시간 데이터 스트림을 연동하고, 강화학습 등의 고도화된 알고리즘을 적용하여 추천 모델을 개선할 수 있습니다.