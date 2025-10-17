#このコードの計算量はO(Q×(log M+K)), ただしKは[l,r]の中にあるaの個数
#9行目のbisect.bisect_left(a, l)はO(log M)で、whileループの中でaの要素を1つずつ確認するため、最悪の場合はK回の比較が必要。
import bisect

import bisect

def find_min_missing(l, r, a):
    # ソート済みリストaに対して、値lを挿入する際に順序が保たれる最小インデックスを二分探索で求める（O(log M））
    idx = bisect.bisect_left(a, l)

    current = l

    # idxからリストaの終わりまで、かつa[idx]がr以下の間、探索を進める
    while idx < len(a) and a[idx] <= r:
        # currentがa[idx] より小さい場合、その値は未出現なのでそのまま返す
        if current < a[idx]:
            return current
        # a[idx] が存在する場合、次の値を確認するためcurrentをa[idx]+1に更新、aインデックスを次の要素へ進める
        current = a[idx] + 1
        idx += 1

    # ループを抜けた後、current がまだ r 以下ならそれが未出現の最小値なので返す
    if current <= r:
        return current
    else:
        # 範囲内に未出現の数がない場合は -1 を返す
        return -1

if __name__ == '__main__':
    N, M = map(int, input().split())
    a = list(map(int, input().split()))
    Q = int(input())
    queries = [tuple(map(int, input().split())) for _ in range(Q)]

    for l, r in queries:
        print(find_min_missing(l, r, a))