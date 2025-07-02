import pandas as pd
import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, Flatten, Concatenate, Dense
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split

# CSV 데이터 로딩 및 경량화 샘플링
df = pd.read_csv("ratings.csv")
df = df.sample(frac=0.1, random_state=42)  # 데이터 10%만 사용

# 인덱스 매핑
user_ids = df['userId'].unique()
movie_ids = df['movieId'].unique()

user_to_index = {uid: idx for idx, uid in enumerate(user_ids)}
movie_to_index = {mid: idx for idx, mid in enumerate(movie_ids)}

df['user_idx'] = df['userId'].map(user_to_index)
df['movie_idx'] = df['movieId'].map(movie_to_index)

# 훈련/테스트 분할
X = df[['user_idx', 'movie_idx']].values
y = df['rating'].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 하이퍼파라미터
n_users = len(user_to_index)
n_movies = len(movie_to_index)
embedding_dim = 16  # 줄임

# 모델 구성
user_input = Input(shape=(1,))
movie_input = Input(shape=(1,))

user_emb = Embedding(input_dim=n_users, output_dim=embedding_dim)(user_input)
movie_emb = Embedding(input_dim=n_movies, output_dim=embedding_dim)(movie_input)

user_vec = Flatten()(user_emb)
movie_vec = Flatten()(movie_emb)

merged = Concatenate()([user_vec, movie_vec])
x = Dense(32, activation='relu')(merged)
x = Dense(16, activation='relu')(x)
output = Dense(1)(x)

model = Model(inputs=[user_input, movie_input], outputs=output)
model.compile(loss='mse', optimizer=Adam(learning_rate=0.001), metrics=['mae'])

# 모델 훈련 (epoch 수 줄임)
model.fit([X_train[:, 0], X_train[:, 1]], y_train, epochs=2, batch_size=256, validation_split=0.1)

# 모델 저장
model.save("ncf_model_light.keras")