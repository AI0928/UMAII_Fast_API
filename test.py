from sklearn.decomposition import NMF
import numpy as np

# 0の部分は未知
R = np.array([
        [0.5, 0.1, 0, 0.4],
        [0.5, 0, 0, 0.5],
        [0.1, 0.8, 0, 0.1],
        [0.2, 0.2, 0, 0.6],
        [0, 0.1, 0.7, 0.2],
        ]
    )

# 特徴の次元kを1から3まで変えてみる
for k in range(1,4):
    model = NMF(n_components=k, init='random', random_state=0)
    P = model.fit_transform(R)
    Q = model.components_
    print("****************************")
    print("k:",k)
    print("Pは")
    print(P)
    print("Q^Tは")
    print(Q)
    print("P×Q^Tは")
    print(np.dot(P,Q))
    print("R-P×Q^Tは")
    print(model.reconstruction_err_ )