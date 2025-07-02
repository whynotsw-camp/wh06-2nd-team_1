import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model

# 1. 모델 불러오기
model = load_model("ncf_model_light.keras")

# 2. 데이터 불러오기 및 매핑 생성
df = pd.read_csv("ratings.csv")
df = df.sample(frac=0.1, random_state=42)

user_ids = df['userId'].unique()
movie_ids = df['movieId'].unique()

user_to_index = {uid: idx for idx, uid in enumerate(user_ids)}
movie_to_index = {mid: idx for idx, mid in enumerate(movie_ids)}

# 3. 테스트할 사용자와 영화 ID 지정 (데이터셋에 있어야 함)
test_user_id = user_ids[0]  # 또는 0, 1, 2 처럼 실제 존재하는 ID로 바꾸기
test_movie_id = movie_ids[10]

# 4. 인덱스 변환
user_idx = user_to_index[test_user_id]
movie_idx = movie_to_index[test_movie_id]

# 5. 예측
pred = model.predict([np.array([user_idx]), np.array([movie_idx])])
print(f"🎯 예측된 평점: {pred[0][0]:.2f}")