import numpy as np 
from sklearn.decomposition.nmf import non_negative_factorization

num_users = 10000
num_items = 100

# 0と1からなるの行列
X = np.random.randint(0, 1, size = [num_users, num_items], dtype = 'int')


n_components = 3 # 特徴量の数（自分で決める）
W, H, n_iter = non_negative_factorization(X, n_components=n_components)

X_predict = np.dot(W,H)

num_new_users = 100
X_new = np.random.randint(1, 2, size = [num_new_users, num_items], dtype = 'int')

W_new, H, n_iter = non_negative_factorization(X_new,
                                              H=H,
                                              update_H=False,
                                              n_components=n_components)

X_new_predict = np.dot(W_new, H)

print(W_new, H, n_iter, X_new_predict)