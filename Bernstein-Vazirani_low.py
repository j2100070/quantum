# qiskit1.0以上のimportに対応
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from matplotlib import font_manager
import numpy as np # P_VALUES生成のために追加
import math # 理論値計算のために追加

def create_noise_model(error_prob: float) -> NoiseModel:
    """
    指定された確率で単一量子ビットの脱分極エラーを持つノイズモデルを作成する。
    
    Args:
        error_prob: ゲートエラーが発生する確率。
    
    Returns:
        設定済みのNoiseModelオブジェクト。
    """
    noise_model = NoiseModel()
    gate_error = depolarizing_error(error_prob, 1)
    # BVアルゴリズムで使用するゲートにノイズを追加
    noise_model.add_all_qubit_quantum_error(gate_error, ['h', 'id', 'z'])
    return noise_model

def build_bernstein_vazirani_circuit(s: str) -> QuantumCircuit:
    """
    秘密のビット列sに対するBernstein-Vaziraniアルゴリズムの量子回路を構築する。
    
    Args:
        s: 秘密のビット列。
        
    Returns:
        構築済みのQuantumCircuitオブジェクト。
    """
    n = len(s)
    qc = QuantumCircuit(n , n)

    # --- Oracleの定義 ---
    def oracle(qc):
        for i, bit in enumerate(reversed(s)):
            if bit == '1':
                qc.z(i)
            else:
                qc.id(i)    # '0'の場合は恒等ゲート

    # --- アルゴリズム本体 ---
    for i in range(n):
        qc.h(i)
    oracle(qc)
    for i in range(n):
        qc.h(i)
    
    # --- 測定 ---
    for i in range(n):
        qc.measure(i, i)
        
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
    # ノイズモデルに対応し、大規模なStabilizer回路も扱えるAerSimulatorを使用
    simulator = AerSimulator(noise_model=noise_model)
    job = simulator.run(qc, shots=shots)
    result = job.result()
    counts = result.get_counts(qc)
    return counts

def calculate_theoretical_prob(n: int, p: float) -> float:
    """
    与えられた n (桁数) と p (エラー確率) に基づいて、
    Bernstein-Vazirani アルゴリズムの理論的な成功確率を計算する。
    (ユーザー提供の式に基づく)
    
    Args:
        n: 秘密のビット列の桁数。
        p: ゲートエラーが発生する確率。
        
    Returns:
        理論的な成功確率。
    """
    if p == 0.0:
        return 1.0
    
    # ユーザー提供の式に基づいて計算
    alpha = math.pow((1.0 - p), 3.0)
    beta = (p * (p**2.0 - 3.0*p + 3.0)) / 2.0
    
    # 1量子ビットあたりの成功確率
    prob_one_qubit = alpha + beta
    
    # n量子ビット全てが成功する確率
    answer = math.pow(prob_one_qubit, n)
    
    return answer

def main():
    """
    スクリプト全体の実行フローを管理する。
    パラメータをスイープしてシミュレーションを実行し、理論値と比較するグラフをプロットする。
    """
    
    # --- パラメータ設定 (ユーザーの要求に基づき変更) ---
    N_VALUES = [1, 10, 100]
    # 0.0005 から 0.0100 まで 0.0005 刻み (終点 0.0101 を指定)
    P_VALUES = [round(p, 4) for p in np.arange(0.0005, 0.0101, 0.0005)]
    SHOTS = 10000
    
    # --- 出力ファイル名 (ユーザーの要求に基づき追加) ---
    OUTPUT_FILENAME = "bernstein_vazirani_success_prob.png"
    
    # --- 日本語フォント設定 ---
    try:
        plt.rcParams['font.family'] = 'Hiragino Sans' # Mac
    except:
        try:
            plt.rcParams['font.family'] = 'Meiryo' # Windows
        except:
            try:
                # Google Colab/Linuxなどで利用可能なフォントパスの例
                font_path = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
                font_manager.fontManager.addfont(font_path)
                plt.rcParams['font.family'] = 'Liberation Sans'
            except:
                print("日本語フォントが見つかりません。グラフの文字化けが発生する可能性があります。")
                plt.rcParams['font.family'] = 'sans-serif'  

    # --- シミュレーション実行 ---
    print("シミュレーションを開始します...")
    print(f"  桁数 (n): {N_VALUES}")
    print(f"  エラー確率 (p): {len(P_VALUES)} ステップ ({P_VALUES[0]} から {P_VALUES[-1]} まで)")
    print(f"  ショット数 (shots): {SHOTS}")
    print("-" * 30)

    # 結果を格納する辞書  
    # {n: {"sim": [(p, sim_prob), ...], "theory": [(p, theory_prob), ...]}, ...}
    all_results = {}

    for n in N_VALUES:
        print(f"\n=== 桁数 n = {n} でシミュレーション中 ===")
        
        sim_results_for_n = []
        theory_results_for_n = [] # 理論値用リスト
        
        # 秘密の文字列sは常に '11...1' と仮定
        secret_string = '1' * n
        
        # n=1000など大規模な回路は構築に少し時間がかかる場合がある
        print(f"  n={n}: 回路を構築中...")
        circuit = build_bernstein_vazirani_circuit(secret_string)
        print(f"  n={n}: 回路構築完了。")
        
        for i, p in enumerate(P_VALUES):
            # 1. ノイズモデル作成
            noise = create_noise_model(p)
            
            # 2. シミュレーション実行
            #    n=1000, SHOTS=1M の場合、ここが最も時間がかかる
            counts = run_simulation(circuit, noise, SHOTS)
            
            # 3. シミュレーション成功確率の計算
            success_count = counts.get(secret_string, 0)
            sim_prob = success_count / SHOTS
            sim_results_for_n.append((p, sim_prob))
            
            # 4. 理論成功確率の計算
            theory_prob = calculate_theoretical_prob(n, p)
            theory_results_for_n.append((p, theory_prob))
            
            # 進捗表示 (例: 20%ごと)
            if (i + 1) % (len(P_VALUES) // 5) == 0 or (i + 1) == len(P_VALUES):
                 print(f"    p = {p:.4f} ({(i+1)}/{len(P_VALUES)}) 完了.")


        # 辞書に格納
        all_results[n] = {
            "sim": sim_results_for_n,
            "theory": theory_results_for_n
        }
        
        # 桁数を揃えて表示 (n=1000に対応)
        print(f"  n={n:<4} 完了. (例: p={P_VALUES[0]}時 Sim={all_results[n]['sim'][0][1]:.4f} / Theory={all_results[n]['theory'][0][1]:.4f})")

    print("\n" + "=" * 30)
    print("シミュレーションがすべて完了しました。")

    # --- グラフのプロット (理論値とシミュレーションの比較) ---
    print("グラフを描画し、ファイルに保存します...")
    plt.figure(figsize=(16, 10)) # サイズを少し調整
    
    # n ごとに色を区別するためのカラーマップ (N_VALUESの数だけ色を取得)
    colors = plt.cm.get_cmap('tab10', len(N_VALUES))

    for i, (n, results_dict) in enumerate(all_results.items()):
        
        color = colors(i) # n ごとに色を固定
        
        # --- シミュレーション結果のプロット (実線 + マーカー) ---
        sim_results = results_dict["sim"]
        p_list_sim = [r[0] for r in sim_results]    
        prob_list_sim = [r[1] for r in sim_results] 
        
        plt.plot(p_list_sim, prob_list_sim, 
                 marker='o', markersize=4, linestyle='-', 
                 label=f"n = {n} (シミュレーション)", 
                 color=color)

        # --- 理論値のプロット (破線) ---
        theory_results = results_dict["theory"]
        p_list_theory = [r[0] for r in theory_results]    
        prob_list_theory = [r[1] for r in theory_results] 
        
        plt.plot(p_list_theory, prob_list_theory, 
                 marker=None, linestyle='--', 
                 label=f"n = {n} (理論値)", 
                 color=color) # シミュレーションと同じ色

    # --- グラフの装飾 ---
    plt.title(f'Bernstein-Vazirani 成功確率 (理論値 vs シミュレーション, Shots={SHOTS})', fontsize=16)
    plt.xlabel('エラー確率 (p)', fontsize=12)  
    plt.ylabel('成功確率', fontsize=12)
    
    # X軸の目盛りをP_VALUESに設定し、90度回転
    plt.xticks(P_VALUES, rotation=90)  
    plt.yticks(np.arange(0, 1.1, 0.1))
    
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # 凡例をグラフの外（右側）に配置
    plt.legend(title="桁数 (n) と種類", bbox_to_anchor=(1.04, 1), loc='upper left', borderaxespad=0.) 
    
    # 凡例が収まるようにレイアウトを調整
    plt.tight_layout(rect=[0, 0, 0.83, 1]) # rectの右側を少し調整
    
    # --- グラフの保存 (ユーザーの要求に基づき変更) ---
    try:
        plt.savefig(OUTPUT_FILENAME, dpi=300)
        print(f"グラフを '{OUTPUT_FILENAME}' として保存しました。")
    except Exception as e:
        print(f"グラフの保存中にエラーが発生しました: {e}")

    # plt.show() # 表示が不要な場合はコメントアウト
    
    print("--------------------------")


if __name__ == "__main__":
    main()