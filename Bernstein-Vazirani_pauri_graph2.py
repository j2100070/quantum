import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, pauli_error
import numpy as np

class PauliNoiseParameters:
    def __init__(self, pauli_x_prob: float, pauli_y_prob: float, pauli_z_prob: float):
        self.pauli_x_prob = pauli_x_prob
        self.pauli_y_prob = pauli_y_prob
        self.pauli_z_prob = pauli_z_prob
        self.total_error_prob = pauli_x_prob + pauli_y_prob + pauli_z_prob

def get_theoretical_prob(secret_string: str, params: PauliNoiseParameters) -> float:
    n = len(secret_string)
    px, py, pz = params.pauli_x_prob, params.pauli_y_prob, params.pauli_z_prob
    # 理論式
    answer_one = (1 + ((1 - 2*py - 2*pz)**2) * (1 - 2*px - 2*py)) / 2 
    return pow(answer_one, n)

def plot_3d_noise_impact(secret_string: str):
    """X, Y, Zノイズを同時に動かし、理論的な正答率を3Dで可視化する"""
    
    # 文字化け対策
    try:
        plt.rcParams['font.family'] = 'Hiragino Sans' 
    except:
        plt.rcParams['font.family'] = 'sans-serif'

    # パラメータの生成 (0%から5%までの範囲でサンプリング)
    steps = 6
    probs = np.linspace(0, 0.00005, steps)
    
    px_list, py_list, pz_list, score_list = [], [], [], []

    for x in probs:
        for y in probs:
            for z in probs:
                params = PauliNoiseParameters(x, y, z)
                if params.total_error_prob <= 1.0:
                    score = get_theoretical_prob(secret_string, params)
                    px_list.append(x * 100) # %表記
                    py_list.append(y * 100)
                    pz_list.append(z * 100)
                    score_list.append(score)

    # --- 3Dプロット ---
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    # 正答率を色の濃淡（Cmap）で表現
    scatter = ax.scatter(px_list, py_list, pz_list, c=score_list, cmap='RdYlGn', s=100, alpha=0.8)
    
    # カラーバーの追加
    cbar = fig.colorbar(scatter, ax=ax, shrink=0.5, aspect=10)
    cbar.set_label('理論的な正答率', rotation=270, labelpad=15)

    ax.set_xlabel('Xノイズ確率 (%)')
    ax.set_ylabel('Yノイズ確率 (%)')
    ax.set_zlabel('Zノイズ確率 (%)')
    ax.set_title(f'3変数パウリノイズによる正答率の変化 (n={len(secret_string)})')

    plt.show()

if __name__ == "__main__":
    plot_3d_noise_impact('000000000000000000000000101010101010101010')