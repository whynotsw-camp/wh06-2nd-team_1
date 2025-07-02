# app/backend/core/user_matching.py

import pandas as pd
from sqlalchemy.orm import Session
from backend.db import crud
import json
import os
from datetime import datetime

# ... (파일 상단 jaccard_similarity, OUTPUT_FILE_PATH 등은 그대로) ...
OUTPUT_FILE_PATH = "app/data/sim_user_id_and_meta.jsonl"

def jaccard_similarity(set1, set2):
    """두 세트 간의 자카드 유사도를 계산하는 함수."""
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0


def find_similar_user(db: Session, new_user_id: str):
    """
    신규 사용자와 가장 유사한 MovieLens 사용자를 찾아 매칭합니다.
    """
    print("\n--- 🕵️ 유사 사용자 찾기 프로세스 시작 🕵️ ---")
    
    # 1. 데이터 로드
    new_user = crud.get_user(db, user_id=new_user_id)
    if not new_user:
        print("❌ 오류: DB에서 신규 사용자를 찾을 수 없습니다.")
        return None, 0
    print(f"✅ 신규 사용자 정보: 나이={new_user.age}, 성별='{new_user.gender}'")

    all_ml_users = crud.get_all_ml_users(db)
    all_ratings = crud.get_all_ratings(db)

    ml_users_df = pd.DataFrame([u.__dict__ for u in all_ml_users])
    ratings_df = pd.DataFrame([r.__dict__ for r in all_ratings])
    
    # --- ✨ 2. 1차 필터링 (성별 데이터 형식 통일) ✨ ---
    age_min, age_max = new_user.age - 5, new_user.age + 5
    
    # 신규 사용자의 성별을 'M' 또는 'F'로 변환합니다.
    gender_to_match = 'M' if new_user.gender == 'Male' else 'F'
    print(f"   -> 매칭을 위해 성별을 '{gender_to_match}'로 변환합니다.")

    candidates_df = ml_users_df[
        (ml_users_df['age'].between(age_min, age_max)) &
        (ml_users_df['gender'] == gender_to_match) # 변환된 값으로 비교
    ]
    candidate_ids = candidates_df['ml_user_id'].tolist()
    print(f"✅ 1차 필터링(나이/성별): {len(candidate_ids)}명의 후보를 찾았습니다.")
    # --- ✨ 여기까지 수정 --- ✨

    if not candidate_ids:
        print("결과: 1차 필터링 후 후보자가 없어 매칭을 종료합니다.")
        return None, 0

    # ... (이하 로직은 동일) ...
    new_user_movie_ids = {crud.get_movie_id_by_title(db, title) for title in new_user.pref_movie_list if crud.get_movie_id_by_title(db, title)}
    print(f"✅ 신규 사용자의 선호 영화 ID 개수: {len(new_user_movie_ids)}개")

    candidate_ratings = ratings_df[ratings_df['ml_user_id'].isin(candidate_ids)]
    user_movie_groups = candidate_ratings.groupby('ml_user_id')['movie_id'].apply(set)
    print(f"✅ 평점 기록이 있는 후보자 수: {len(user_movie_groups)}명")

    if user_movie_groups.empty:
        print("결과: 1차 필터링된 후보들의 평점 기록이 샘플에 없어 매칭을 종료합니다.")
        return None, 0
    
    best_match_user_id, max_similarity = -1, -1
    
    print("⏳ 2차 필터링(자카드 유사도) 계산 시작...")
    for i, (ml_user_id, watched_movie_ids) in enumerate(user_movie_groups.items()):
        similarity = jaccard_similarity(new_user_movie_ids, watched_movie_ids)
        if i < 5:
            print(f"  - 후보 {ml_user_id} 와의 유사도: {similarity:.4f}")
        if similarity > max_similarity:
            max_similarity = similarity
            best_match_user_id = ml_user_id

    if best_match_user_id != -1:
        print(f"🎉 매칭 성공! 가장 유사한 사용자: {best_match_user_id} (유사도: {max_similarity:.4f})")
        save_match_to_jsonl(db, new_user, best_match_user_id, max_similarity)
        return best_match_user_id, max_similarity
    else:
        print("결과: 유사도 계산 후에도 매칭된 사용자가 없습니다.")
        return None, 0
# ... (파일 하단 save_match_to_jsonl 함수는 그대로) ...
def save_match_to_jsonl(db: Session, new_user, ml_user_id, similarity):
    """매칭 결과를 상세 정보와 함께 jsonl 파일에 저장합니다."""
    
    ml_user = crud.get_ml_user(db, ml_user_id=ml_user_id)
    watched_movies = crud.get_watched_movies_by_ml_user(db, ml_user_id=ml_user_id)
    watched_movies_dict = {movie_id: float(rating) for movie_id, rating in watched_movies} # rating을 float으로 변환

    result_data = {
        "timestamp": datetime.now().isoformat(),
        "new_user_info": {
            "user_id": str(new_user.user_id),
            "gender": new_user.gender,
            "age": new_user.age,
            "pref_movie_list": new_user.pref_movie_list
        },
        "matched_ml_user_info": {
            "ml_user_id": ml_user.ml_user_id,
            "gender": ml_user.gender,
            "age": ml_user.age,
            "watched_movies": watched_movies_dict
        },
        "similarity_score": similarity
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE_PATH), exist_ok=True)
    
    with open(OUTPUT_FILE_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(result_data, ensure_ascii=False) + '\n')
        
    print(f"✅ 매칭 결과를 '{OUTPUT_FILE_PATH}' 파일에 저장했습니다.")