import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, pauli_error, depolarizing_error
import math

def build_bernstein_vazirani_circuit(s: str) -> QuantumCircuit:
    """Bernstein-Vazirani回路を構築"""
    n = len(s)
    qc = QuantumCircuit(n, n)
    for i in range(n):
        qc.h(i)
    # Oracle (ZゲートとIDゲートによる実装)
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

def get_depolarizing_noise_model(p: float) -> NoiseModel:
    """Qiskit標準の脱分極ノイズモデル"""
    noise_model = NoiseModel()
    error = depolarizing_error(p, 1)
    noise_model.add_all_qubit_quantum_error(error, ['h', 'id', 'z'])
    return noise_model

def get_pauli_equivalent_noise_model(p: float) -> NoiseModel:
    """
    脱分極ノイズと等価なパウリノイズモデル
    各軸のエラー確率を p/4 に設定 (残りの 1-3p/4 が Identity)
    """
    noise_model = NoiseModel()
    px = py = pz = p / 4
    p_identity = 1.0 - (px + py + pz)
    error = pauli_error([
        ('X', px), ('Y', py), ('Z', pz), ('I', p_identity)
    ])
    noise_model.add_all_qubit_quantum_error(error, ['h', 'id', 'z'])
    return noise_model

def get_theoretical_prob(n: int, p: float) -> float:
    """
    理論式による正答確率の計算
    脱分極ノイズ1ゲートあたりの生存確率は 1 - 3p/4
    回路構成（H -> Oracle -> H）において、各ビットにつき3回のゲート操作に
    ノイズが乗る想定での計算式
    """
    # 1ビットあたり: (1 - 3p/4)^3 + (エラーが相殺されて正解になる微小確率) の近似
    # ご提示の式 alpha + beta に基づく
    alpha = math.pow((1 - p), 3) # 回路全体の簡略化モデル
    beta = (p * (p**2 - 3*p + 3)) / 2
    return pow(alpha + beta, n)

def compare_noises(secret_string: str, shots: int):
    n = len(secret_string)
    prob_steps = np.linspace(0, 0.2, 11) # エラー率 0% から 20%
    
    depol_sim_results = []
    pauli_sim_results = []
    theory_results = []

    circuit = build_bernstein_vazirani_circuit(secret_string)
    simulator = AerSimulator()

    print(f"シミュレーション開始: n={n}, shots={shots}")

    for p in prob_steps:
        # 1. 脱分極ノイズのシミュレーション
        nm_depol = get_depolarizing_noise_model(p)
        counts_depol = simulator.run(circuit, noise_model=nm_depol, shots=shots).result().get_counts()
        depol_sim_results.append(counts_depol.get(secret_string, 0) / shots)

        # 2. 等価パウリノイズのシミュレーション (px=py=pz=p/4)
        nm_pauli = get_pauli_equivalent_noise_model(p)
        counts_pauli = simulator.run(circuit, noise_model=nm_pauli, shots=shots).result().get_counts()
        pauli_sim_results.append(counts_pauli.get(secret_string, 0) / shots)

        # 3. 理論値
        theory_results.append(get_theoretical_prob(n, p))
        print(f"p={p:.2f} 完了")

    # --- グラフ描画 ---
    plt.figure(figsize=(10, 6))
    
    # 文字化け対策
    try:
        plt.rcParams['font.family'] = 'Hiragino Sans' 
    except:
        plt.rcParams['font.family'] = 'sans-serif'

    plt.plot(prob_steps * 100, depol_sim_results, 'o-', label='脱分極ノイズ (Sim)')
    plt.plot(prob_steps * 100, pauli_sim_results, 'x--', label='パウリノイズ (px=py=pz=p/4 Sim)')
    plt.plot(prob_steps * 100, theory_results, 's:', label='理論値', alpha=0.7)

    plt.title(f'脱分極ノイズとパウリノイズの比較 (n={n})')
    plt.xlabel('エラー確率 p (%)')
    plt.ylabel('正答率')
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.legend()
    plt.ylim(-0.05, 1.05)
    plt.show()

if __name__ == "__main__":
    # 秘密の文字列 '1011' で実行
    compare_noises('1011', 10000)