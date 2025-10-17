def staged_power(n: int) -> str:
    """
    指定された整数 N に対して、X^N の計算を行う関数の文字列を生成する。
    """
    if not isinstance(n, int) or n < 0:
        raise ValueError("指数 N は0以上の整数である必要があります。")

    function_name = f"power_{n}"
    
    if n == 1:
        # X^1 = X
        return_expression = "x"
    else:
        # X^N = x * x * ... * x (N回)
        return_expression = " * ".join(["x"] * n)
        
    # Pythonの関数定義文字列を組み立てる
    # インデントや改行も文字列の一部として含める
    function_string = f"""\
def {function_name}(x: int) -> int:
    return {return_expression}
"""
    return function_string

# テスト実行
if __name__ == "__main__":
    # N = 3 の場合
    power_3_string = staged_power(3)
    print("\" N = 3 \"")
    print(power_3_string)
    # N = 1 の場合
    print("\" N = 1 \"")
    power_1_string = staged_power(1)
    print(power_1_string)

    