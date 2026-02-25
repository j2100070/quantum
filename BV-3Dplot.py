import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def plot_combined_noise_boundary(n=4):
    # 文字化け対策
    try:
        plt.rcParams['font.family'] = 'Hiragino Sans' 
    except:
        plt.rcParams['font.family'] = 'sans-serif'

    # パラメータ設定
    res = 50
    p_range = np.linspace(0, 0.1, res)
    px, py, pz = np.meshgrid(p_range, p_range, p_range)

    # 理論式の計算
    # p_bit = (1 + (1-2py-2pz)^2 * (1-2px-2py)) / 2
    p_bit = (1 + ((1 - 2*py - 2*pz)**2) * (1 - 2*px - 2*py)) / 2
    success_rate = np.power(p_bit, n)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # 正答率が 2/3 (約0.667) になる境界を抽出
    # 3次元散布図で境界付近の点のみをプロットして面を表現
    mask = np.abs(success_rate - 2/3) < 0.002
    
    img = ax.scatter(px[mask]*100, py[mask]*100, pz[mask]*100, 
                     c=success_rate[mask], cmap='viridis', s=5, alpha=0.3)

    ax.set_title(f'正答率 2/3 の境界曲面 (n={n})')
    ax.set_xlabel('px (Xノイズ) [%]')
    ax.set_ylabel('py (Yノイズ) [%]')
    ax.set_zlabel('pz (Zノイズ) [%]')
    
    # 視認性を上げるために軸範囲を制限
    limit = 8
    ax.set_xlim(0, limit)
    ax.set_ylim(0, limit)
    ax.set_zlim(0, limit)
    
    plt.show()

plot_combined_noise_boundary(n=5)