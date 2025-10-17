from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister, execute, BasicAer

# 求めたい秘密のビット列 (nビット)
s = '101'
n = len(s)

# オラクル関数: s = '101' をエンコード
def oracle(qc):
    # sのビットが'1'の位置に対応する入力量子ビットからCXをかける
    # s = '101' なので、0番目と2番目のビットが'1'
    qc.cx(q[0], q[n])
    qc.cx(q[2], q[n])

def Bernstein_Vazirani(qc):
    # --- 初期化 ---
    # 1. 補助ビットを |-> 状態にする
    qc.x(q[n])
    qc.h(q[n])
    
    # 2. 入力ビット(0からn-1)にHゲートを適用
    for i in range(n):
        qc.h(q[i])
        
    qc.barrier() # 回路の見た目を分かりやすくするための線

    # --- オラクルを適用 ---
    oracle(qc)
    
    qc.barrier()

    # --- 出力 ---
    # 入力ビット(0からn-1)にHゲートを適用
    for i in range(n):
        qc.h(q[i])


if __name__ == "__main__":
    # n+1 量子ビット（n: 入力用, 1: 補助用）
    q = QuantumRegister(n+1, "q")
    # n 古典ビット（入力ビットの測定結果を格納）
    c = ClassicalRegister(n, "c")
    
    qc = QuantumCircuit(q, c)
    
    Bernstein_Vazirani(qc)
    
    # --- 測定 ---
    # 入力ビット(0からn-1)のみを測定する
    for i in range(n):
        qc.measure(q[i], c[i])

    # --- 量子回路の実行と結果表示 ---
    backend = BasicAer.get_backend('qasm_simulator')
    job = execute(qc, backend, shots=1) # このアルゴリズムは1ショットで答えが確定する
    result = job.result()
    counts = result.get_counts(qc)
    
    print("実行結果:", counts)
    # 実行結果: {'101': 1} と表示されるはず
      
    
    
