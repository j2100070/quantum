# qiskit1.0以上のimportに対応
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
# depolarizing_error の代わりに pauli_error をインポート
from qiskit_aer.noise import NoiseModel, pauli_error
from qiskit.visualization import plot_histogram
from matplotlib import font_manager
import math

class PauliNoiseParameters:
    """パウリノイズの確率を格納するデータクラス"""
    def __init__(self, pauli_x_prob: float, pauli_y_prob: float, pauli_z_prob: float):
        self.pauli_x_prob = pauli_x_prob
        self.pauli_y_prob = pauli_y_prob
        self.pauli_z_prob = pauli_z_prob
        
        # 合計エラー確率を計算
        self.total_error_prob = pauli_x_prob + pauli_y_prob + pauli_z_prob
        
        # 合計確率が1.0を超えていないかチェック
        if self.total_error_prob > 1.0:
            raise ValueError(f"パウリエラーの合計確率が1.0を超えています: {self.total_error_prob}")

    def __str__(self):
        """パラメータを分かりやすく表示するためのメソッド"""
        return (f"PauliNoiseParameters(X={self.pauli_x_prob*100:.2f}%, "
                f"Y={self.pauli_y_prob*100:.2f}%, "
                f"Z={self.pauli_z_prob*100:.2f}%, "
                f"Total={self.total_error_prob*100:.2f}%)")


def create_noise_model(params: PauliNoiseParameters) -> NoiseModel:
    """
    指定されたPauliNoiseParametersに基づいてノイズモデルを作成する。
    """
    print("--- 1. ノイズモデルを構築中... ---")
    print(f"使用するノイズパラメータ: {params}")
    noise_model = NoiseModel()
    
    # エラーが起きない (Identity) 確率を計算
    p_identity = 1.0 - params.total_error_prob
    
    # 全ての確率 (X, Y, Z, I) をリストで渡す
    gate_error = pauli_error([
        ('X', params.pauli_x_prob), 
        ('Y', params.pauli_y_prob), 
        ('Z', params.pauli_z_prob),
        ('I', p_identity)  
    ])
    
    # 'h', 'id', 'z' ゲートにエラーを追加
    noise_model.add_all_qubit_quantum_error(gate_error, ['h', 'id', 'z'])
    
    print(f"作成したノイズモデル:\n{noise_model}\n")
    return noise_model

def build_bernstein_vazirani_circuit(s: str) -> QuantumCircuit:
    """
    秘密のビット列sに対するBernstein-Vaziraniアルゴリズムの量子回路を構築する。
    """
    print("--- 2. Bernstein-Vazirani回路を構築中... ---")
    n = len(s)
    qc = QuantumCircuit(n , n)

    # --- Oracleの定義 ---
    def oracle(qc):
        for i, bit in enumerate(reversed(s)):
            if bit == '1':
                qc.z(i)
            else:
                qc.id(i)    

    # --- アルゴリズム本体 ---
    for i in range(n):
        qc.h(i)
    oracle(qc)
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
    """
    print(f"--- 3. シミュレーションを実行中 (shots={shots})... ---")
    simulator = AerSimulator(noise_model=noise_model)
    job = simulator.run(qc, shots=shots)
    result = job.result()
    counts = result.get_counts(qc)
    print("シミュレーションが完了しました。\n")
    return counts

def theorical_ratio(SECRET_STRING: str, params: PauliNoiseParameters):
    """
    理論的な結果の比率を表示する。
    """
    SECRET_STRING_LENGTH = len(SECRET_STRING)
    answer_one = (1 +((1-2*params.pauli_y_prob -2*params.pauli_z_prob)**2) * (1-2*params.pauli_x_prob -2*params.pauli_y_prob) )/2 
    answer = pow(answer_one, SECRET_STRING_LENGTH) 
    print(f"理論的な正答確率（参考値）: {answer}")

def main():
    """
    スクリプト全体の実行フローを管理する。
    """
    # --- パラメータ設定 ---
    SECRET_STRING = '1011'
    
    noise_params = PauliNoiseParameters(
        pauli_x_prob=0.01,
        pauli_y_prob=0.01,
        pauli_z_prob=0.01,
    )

    SHOTS = 10000000
    
    print(f"秘密のビット列 (s): {SECRET_STRING}")

    # 1. ノイズモデルを作成
    noise = create_noise_model(noise_params)

    # 2. 量子回路を構築
    circuit = build_bernstein_vazirani_circuit(SECRET_STRING)

    # 3. シミュレーションを実行
    counts = run_simulation(circuit, noise, SHOTS)
    # print("ノイズありの実行結果:", counts) # 全件表示すると多すぎる場合はコメントアウト推奨
    
    # --- 修正箇所: ここで確率計算を行う ---
    # カウントを確率に正規化
    normalized_counts = {k: v / SHOTS for k, v in counts.items()}
    
    # 正解のビット列 (SECRET_STRING) の確率を取得
    # .get() を使うことで、万が一観測されなかった場合でもエラーにならず 0 を返す
    measured_prob = normalized_counts.get(SECRET_STRING, 0.0)
    
    print("-" * 30)
    print(f"★ 実測された正解 '{SECRET_STRING}' の確率: {measured_prob}")
    print("-" * 30)
    
    # 5.理論値の表示
    theorical_ratio(SECRET_STRING, noise_params)
    
    # 6. 結果をヒストグラムで描画・表示
    print("\n--- 実行結果のヒストグラム ---")
            
    try:
        # フォント設定
        plt.rcParams['font.family'] = 'Hiragino Sans' 

        plot_histogram(normalized_counts, title='ノイズモデルありの実行結果')
        plt.ylabel("確率")
        plt.show()
    except ImportError as e:
        print(f"ヒストグラムの描画に失敗しました (matplotlibが必要): {e}")
    except Exception as e:
        print(f"ヒストグラム描画中にエラーが発生しました: {e}")
        # フォントエラー時でも英語で描画を試みる
        plt.rcParams['font.family'] = 'sans-serif'
        plot_histogram(normalized_counts, title='Execution Result with Noise Model')
        plt.ylabel("Probability")
        plt.show()

    print("--------------------------")

if __name__ == "__main__":
    main()