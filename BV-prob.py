#Bernstein-Vaziraniアルゴリズムにおける確率2/3を満たすとき、px,py,pzを独立に動かす場合の許容ノイズ確率をプロットする

import matplotlib.pyplot as plt
import numpy as np

def plot_allowed_noise_by_n():
    # 文字化け対策
    try:
        plt.rcParams['font.family'] = 'Hiragino Sans' 
    except:
        plt.rcParams['font.family'] = 'sans-serif'

    # nの範囲 (1から50ビット)
    n = np.arange(1, 51)
    
    # 共通定数
    target = (2/3)**(1/n)

    # 1. pxのみ (py=0, pz=0)
    px_limit = 1 - target

    # 2. pyのみ (px=0, pz=0) -> (1 + (1-2py)^3)/2 = target
    # 2*target - 1 = (1-2py)^3
    py_limit = (1 - np.power(np.maximum(0, 2*target - 1), 1/3)) / 2

    # 3. pzのみ (px=0, py=0) -> (1 + (1-2pz)^2)/2 = target
    # 2*target - 1 = (1-2pz)^2
    pz_limit = (1 - np.sqrt(np.maximum(0, 2*target - 1))) / 2

    # グラフ描画
    plt.figure(figsize=(10, 6))
    
    plt.plot(n, px_limit * 100, label='$p_x$ のみ ($p_y=p_z=0$)', marker='o', markersize=4)
    plt.plot(n, py_limit * 100, label='$p_y$ のみ ($p_x=p_z=0$)', marker='s', markersize=4)
    plt.plot(n, pz_limit * 100, label='$p_z$ のみ ($p_x=p_y=0$)', marker='^', markersize=4)

    plt.title('正答率 2/3 を維持できる限界ノイズ確率')
    plt.xlabel('ビット数 $n$')
    plt.ylabel('許容される最大ノイズ確率 (%)')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend()
    
    plt.show()

if __name__ == "__main__":
    plot_allowed_noise_by_n()