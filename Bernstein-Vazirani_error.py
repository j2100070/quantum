import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit.visualization import plot_histogram

def create_noise_model(error_prob: float) -> NoiseModel:
    """
    指定された確率で単一量子ビットの脱分極エラーを持つノイズモデルを作成する。
    
    Args:
        error_prob: ゲートエラーが発生する確率。
    
    Returns:
        設定済みのNoiseModelオブジェクト。
    """
    print("--- 1. ノイズモデルを構築中... ---")
    noise_model = NoiseModel()
    # 1量子ビットの脱分極エラーを定義
    gate_error = depolarizing_error(error_prob, 1)
    
    # 'h' と 'id' ゲートにエラーを追加
    noise_model.add_all_qubit_quantum_error(gate_error, ['h', 'id'])
    
    print(f"作成したノイズモデル:\n{noise_model}\n")
    return noise_model

def build_bernstein_vazirani_circuit(s: str) -> QuantumCircuit:
    """
    秘密のビット列sに対するBernstein-Vaziraniアルゴリズムの量子回路を構築する。
    
    Args:
        s: 秘密のビット列。
        
    Returns:
        構築済みのQuantumCircuitオブジェクト。
    """
    print("--- 2. Bernstein-Vazirani回路を構築中... ---")
    n = len(s)
    qc = QuantumCircuit(n + 1, n)

    # --- Oracleの定義 ---
    def oracle(qc):
        for i, bit in enumerate(reversed(s)):
            if bit == '1':
                qc.z(i)
            else:
                qc.id(i)    

    # --- アルゴリズム本体 ---
    qc.x(n)
    qc.h(n)
    for i in range(n):
        qc.h(i)
    qc.barrier()
    oracle(qc)
    qc.barrier()
    for i in range(n):
        qc.h(i)
    
    # --- 測定 ---
    for i in range(n):
        qc.measure(i, i)
        
    print("回路の構築が完了しました。\n")
    return qc

def run_simulation(qc: QuantumCircuit, noise_model: NoiseModel, shots: int) -> dict:
    """
    指定された量子回路とノイズモデルを使ってシミュレーションを実行する。
    
    Args:
        qc: 実行するQuantumCircuitオブジェクト。
        noise_model: シミュレーションに使用するNoiseModelオブジェクト。
        shots: シミュレーションの試行回数。
        
    Returns:
        測定結果のカウント（辞書型）。
    """
    print(f"--- 3. シミュレーションを実行中 (shots={shots})... ---")
    simulator = AerSimulator(noise_model=noise_model)
    job = simulator.run(qc, shots=shots)
    result = job.result()
    counts = result.get_counts(qc)
    print("シミュレーションが完了しました。\n")
    return counts

def main():
    """
    スクリプト全体の実行フローを管理する。
    """
    # --- パラメータ設定 ---
    SECRET_STRING = '1011'

    ERROR_PROBABILITY = 0.05
    SHOTS = 10000000
    
    print(f"秘密のビット列 (s): {SECRET_STRING}")
    print(f"エラー確率: {ERROR_PROBABILITY*100}%\n")

    # 1. ノイズモデルを作成
    noise = create_noise_model(ERROR_PROBABILITY)

    # 2. 量子回路を構築
    circuit = build_bernstein_vazirani_circuit(SECRET_STRING)

    # 3. 回路図を描画・表示 (コンソール環境などでは表示されない場合があります)
    print("--- 量子回路図 ---")
    try:
        circuit.draw('mpl')
        plt.show()
    except ImportError as e:
        print(f"回路図の描画に失敗しました (matplotlibが必要): {e}")
        print(circuit.draw('text')) # テキストベースで回路図を出力
    print("------------------\n")
    
    # 4. シミュレーションを実行
    counts = run_simulation(circuit, noise, SHOTS)
    print("ノイズありの実行結果:", counts)

    # 5. 結果をヒストグラムで描画・表示 (コンソール環境などでは表示されない場合があります)
    print("\n--- 実行結果のヒストグラム ---")
    try:
        plot_histogram(counts, title='ノイズモデルありの実行結果')
        plt.show()
    except ImportError as e:
         print(f"ヒストグラムの描画に失敗しました (matplotlibが必要): {e}")
    print("--------------------------")


if __name__ == "__main__":
    main()