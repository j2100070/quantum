import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, pauli_error
from qiskit.visualization import plot_histogram
import math

class PauliNoiseParameters:
    """パウリノイズの確率を格納するデータクラス"""
    def __init__(self, pauli_x_prob: float, pauli_y_prob: float, pauli_z_prob: float):
        self.pauli_x_prob = pauli_x_prob
        self.pauli_y_prob = pauli_y_prob
        self.pauli_z_prob = pauli_z_prob
        self.total_error_prob = pauli_x_prob + pauli_y_prob + pauli_z_prob
        
        if self.total_error_prob > 1.0:
            raise ValueError(f"パウリエラーの合計確率が1.0を超えています: {self.total_error_prob}")

def get_theoretical_prob(secret_string: str, params: PauliNoiseParameters) -> float:
    """
    提供された理論式に基づいて正答確率を計算する。
    1ビットあたりの正解確率を求め、ビット長(n)乗する。
    """
    n = len(secret_string)
    px, py, pz = params.pauli_x_prob, params.pauli_y_prob, params.pauli_z_prob
    
    # ご提示の理論式: 1ビットが正しく測定される確率
    # answer_one = (1 + ((1-2py-2pz)^2) * (1-2px-2py)) / 2
    answer_one = (1 + ((1 - 2*py - 2*pz)**2) * (1 - 2*px - 2*py)) / 2 
    return pow(answer_one, n)

def create_noise_model(params: PauliNoiseParameters) -> NoiseModel:
    """指定されたパラメータでNoiseModelを作成"""
    noise_model = NoiseModel()
    p_identity = 1.0 - params.total_error_prob
    gate_error = pauli_error([
        ('X', params.pauli_x_prob), 
        ('Y', params.pauli_y_prob), 
        ('Z', params.pauli_z_prob),
        ('I', p_identity)  
    ])
    # 全てのビットに対してH, ID, Zゲート実行時にエラーを付加
    noise_model.add_all_qubit_quantum_error(gate_error, ['h', 'id', 'z'])
    return noise_model

def build_bernstein_vazirani_circuit(s: str) -> QuantumCircuit:
    """Bernstein-Vazirani回路を構築"""
    n = len(s)
    qc = QuantumCircuit(n, n)
    for i in range(n):
        qc.h(i)
    # Oracle
    for i, bit in enumerate(reversed(s)):
        if bit == '1':
            qc.z(i)
        else:
            qc.id(i)    
    for i in range(n):
        qc.h(i)
    for i in range(n):
        qc.measure(i, i)
    return qc

def plot_noise_impact_comparison(secret_string: str, shots: int):
    """
    シミュレーション結果と理論値を比較してプロット。
    文字化け対策を含む。
    """
    print(f"--- 分析開始 (秘密の文字列: {secret_string}, ショット数: {shots}) ---")
    
    # 文字化け対策（フォント設定）
    try:
        plt.rcParams['font.family'] = 'Hiragino Sans' 
    except:
        plt.rcParams['font.family'] = 'sans-serif'
        print("指定の日本語フォントが見つかりませんでした。")

    prob_steps = [i * 0.01 for i in range(11)] # 0%から10%まで
    noise_types = ['X', 'Y', 'Z']
    
    sim_data = {t: [] for t in noise_types}
    theory_data = {t: [] for t in noise_types}

    circuit = build_bernstein_vazirani_circuit(secret_string)
    simulator = AerSimulator()

    for p in prob_steps:
        # 各パウリノイズが個別に発生した場合のデータを作成
        configs = [
            ('X', PauliNoiseParameters(p, 0, 0)),
            ('Y', PauliNoiseParameters(0, p, 0)),
            ('Z', PauliNoiseParameters(0, 0, p))
        ]
        
        for label, params in configs:
            # シミュレーション実行
            nm = create_noise_model(params)
            result = simulator.run(circuit, noise_model=nm, shots=shots).result()
            counts = result.get_counts()
            sim_data[label].append(counts.get(secret_string, 0) / shots)
            
            # 理論値の算出
            theory_data[label].append(get_theoretical_prob(secret_string, params))

    # --- グラフの描画 ---
    plt.figure(figsize=(10, 6))
    colors = {'X': '#1f77b4', 'Y': '#2ca02c', 'Z': '#d62728'}
    markers = {'X': 'o', 'Y': 's', 'Z': '^'}
    
    prob_pct = [p * 100 for p in prob_steps]

    for t in noise_types:
        # シミュレーション結果（点）
        plt.scatter(prob_pct, sim_data[t], color=colors[t], marker=markers[t], 
                    label=f'{t}ノイズ (Sim)', zorder=3)
        # 理論値（破線）
        plt.plot(prob_pct, theory_data[t], color=colors[t], linestyle='--', 
                 alpha=0.6, label=f'{t}ノイズ (理論)', zorder=2)

    plt.title(f'パウリノイズによる正答率の変化 (n={len(secret_string)})')
    plt.xlabel('ノイズ確率 (%)')
    plt.ylabel('正答率')
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.legend()
    plt.ylim(-0.05, 1.05)
    plt.show()

if __name__ == "__main__":
    # 実行
    plot_noise_impact_comparison('0000000000000000000000001010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101000000010101010100101', 5000)