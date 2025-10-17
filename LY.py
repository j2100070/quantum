import math

#入力値の最大クエリ数
INPUT_DATA_LINE = 2000
MAX_USER_AMOUNT = 1000

DEBUG = False


# ストレージの情報(type: ストレージタイプ, save_rate: 保存次課金係数, uodate_rate: 更新時課金係数, is_free_plan: 無料プランで利用可能か)
# ストレージのファイルリスト(files: ファイル名とサイズのリスト, save_file_size: 保存ファイルの合計サイズ, monthly_save_max_size: 月間保存最大サイズ, monthly_update_size: 月間更新サイズ, storage_fee: 保存料金, update_fee: 更新料金)
STORAGE_DATA = {
    'storage_A1': {
        'type': 'A',
        'save_rate': 0.01,
        'update_rate': 0.0005,
        'is_free_plan': True,
        'files': [],
        'save_file_size': 0,
        'monthly_save_max_size':0,
        'monthly_update_size': 0,
        'storage_fee': 0,
        'update_fee': 0,
    },
    'storage_A2': {
        'type': 'A',
        'save_rate': 0.001,
        'update_rate': 0.01,
        'is_free_plan': True,
        'files': [],
        'save_file_size': 0,
        'monthly_save_max_size':0,
        'monthly_update_size': 0,
        'storage_fee': 0,
        'update_fee': 0,
    }
}


output_log = [] # 出力ログを格納するリスト

def get_all_file_size(storage_name): # あるストレージに含まれている全てのファイルのサイズを取得する関数
    file_size = 0
    files = STORAGE_DATA[storage_name]['files']
    for f in files:
        file_size += int(f['size'])
    return file_size 

def calc_total_fees(): # 各ストレージの保存料金、更新料金の合計を計算する関数
    total_storage_fee = 0
    total_update_fee = 0
    for storage in STORAGE_DATA.values():
        total_storage_fee += storage['storage_fee']
        total_update_fee += storage['update_fee']
    return total_storage_fee, total_update_fee

def init_storage_data(): # 月間ストレージデータの初期化関数
    for storage_name in STORAGE_DATA:
        STORAGE_DATA[storage_name]['update_fee'] = 0
        STORAGE_DATA[storage_name]['monthly_save_max_size'] = get_all_file_size(storage_name)
        STORAGE_DATA[storage_name]['save_file_size'] = get_all_file_size(storage_name)
        STORAGE_DATA[storage_name]['storage_fee'] = math.ceil((STORAGE_DATA[storage_name]['save_rate']) * math.ceil(STORAGE_DATA[storage_name]['save_file_size']/1000))
        STORAGE_DATA[storage_name]['monthly_update_size'] = 0
        



def input_data():
    query = [[''] * 5 for _ in range(INPUT_DATA_LINE)]  # 2次元リストの初期化
    i = 0
    while True:
        try:
            line = input()
            if line == "":
                break
        except EOFError:
            break

        parts = line.split()
        query[i][0] = parts[0]            # 日時
        query[i][1] = parts[1]            # 操作

        if parts[1] == 'CALC':
            pass
        elif parts[1] == 'DELETE':
            query[i][2] = parts[2]        # ストレージ
            query[i][3] = parts[3]        # ファイル名
        else:
            # UPLOADやUPDATEなど
            query[i][2] = parts[2]        # ストレージ
            query[i][3] = parts[3]        # ファイル名
            query[i][4] = parts[4]        # サイズ
        i += 1

    return query[:i]  # 実入力分のみ返却

def get_file_size(storage_name, filename): # ストレージに含まれているファイルのサイズを取得する関数
    files = STORAGE_DATA[storage_name]['files']
    for f in files:
        if f['name'] == filename:
            return f['size']
    return None  # 見つからない場合

 

def calc_storage_usage(): # 各ストレージの容量計算部分の実装
    storage_usage = {}
    for storage_name in STORAGE_DATA:
        total_size = sum(int(f['size']) for f in STORAGE_DATA[storage_name]['files'])
        storage_usage[storage_name] = total_size
    return storage_usage

def is_upload_over(storage_name, file_size): # 無料枠を超えるか確認する関数(False: 超えない, True: 超える)
    storage = STORAGE_DATA[storage_name]
    save_rate = storage['save_rate']
    update_rate = storage['update_rate']
    file_size = int(file_size)

    # --- 変更前の値を保存 ---
    old_save = storage['save_file_size']
    old_max = storage['monthly_save_max_size']
    old_storage_fee = storage['storage_fee']
    old_update = storage['monthly_update_size']
    old_update_fee = storage['update_fee']

    storage['save_file_size'] += file_size
    if storage['save_file_size'] > storage['monthly_save_max_size']:
        storage['monthly_save_max_size'] = storage['save_file_size']
    storage['storage_fee'] = math.ceil(math.ceil(storage['monthly_save_max_size']/1000) * save_rate )
    storage['monthly_update_size'] += file_size
    storage['update_fee'] = math.ceil(math.ceil(storage['monthly_update_size']/1000) * update_rate )
    
    storage_fees, update_fees = calc_total_fees()
    
    # --- 判定条件
    if storage_fees + update_fees <= MAX_USER_AMOUNT:
        return False
    else:
        # --- 元に戻す ---
        storage['save_file_size'] = old_save
        storage['monthly_save_max_size'] = old_max
        storage['storage_fee'] = old_storage_fee
        storage['monthly_update_size'] = old_update
        storage['update_fee'] = old_update_fee
        return True     
    
def is_delete_over(storage_name, file_size): # 無料枠を超えるか確認する関数(False: 超えない, True: 超える)
    storage = STORAGE_DATA[storage_name]
    update_rate = storage['update_rate']
    file_size = int(file_size)

    # --- 変更前の値を保存 ---
    old_update = storage['monthly_update_size']
    old_update_fee = storage['update_fee']

    storage['monthly_update_size'] += file_size
    storage['update_fee'] = math.ceil(math.ceil(storage['monthly_update_size']/1000) * update_rate )
    
    storage_fees, update_fees = calc_total_fees()

    # --- 判定条件を <= に変更 ---
    if storage_fees + update_fees <= MAX_USER_AMOUNT:
        storage['save_file_size'] -= file_size
        return False
    else:
        # --- 元に戻す ---
        storage['monthly_update_size'] = old_update
        storage['update_fee'] = old_update_fee
        return True
    
def is_update_over(storage_name, file_name, after_file_size):# 無料枠を超えるか確認する関数(False: 超えない, True: 超える)
    storage = STORAGE_DATA[storage_name]
    save_rate = storage['save_rate'] # <-- save_rate を取得
    update_rate = storage['update_rate']
    after_file_size = int(after_file_size)
    before_file_size = int(get_file_size(storage_name, file_name))

    # --- 変更前の値を保存 ---
    old_save = storage['save_file_size']
    old_max = storage['monthly_save_max_size']
    old_storage_fee = storage['storage_fee']
    old_update = storage['monthly_update_size']
    old_update_fee = storage['update_fee']

    storage['monthly_update_size'] += before_file_size + after_file_size
    storage['update_fee'] = math.ceil(math.ceil(storage['monthly_update_size']/1000) * update_rate )
    
    storage['save_file_size'] += (after_file_size - before_file_size) # 差分で計算
    if storage['save_file_size'] > storage['monthly_save_max_size']:
        storage['monthly_save_max_size'] = storage['save_file_size']
    # --- storage_fee も更新 ---
    storage['storage_fee'] = math.ceil(math.ceil(storage['monthly_save_max_size']/1000) * save_rate )

    storage_fees, update_fees = calc_total_fees()

    # --- 判定条件を <= に変更 ---
    if storage_fees + update_fees <= MAX_USER_AMOUNT:
        return False
    else:
        # --- 元に戻す ---
        storage['save_file_size'] = old_save
        storage['monthly_save_max_size'] = old_max
        storage['storage_fee'] = old_storage_fee
        storage['monthly_update_size'] = old_update
        storage['update_fee'] = old_update_fee
        return True    
    
def process_CALC(i, query):
    global storage_fee, update_fee, usage_fee
    """
    CALC操作を処理する関数
    """
    # 使用量の取得（存在しない場合は0扱い）
    storage_usage = calc_storage_usage()
    storage_A1_used = storage_usage.get('storage_A1', 0)
    storage_A2_used = storage_usage.get('storage_A2', 0)
    storage_B1_used = storage_usage.get('storage_B1', 0)
    storage_B2_used = storage_usage.get('storage_B2', 0)
    storage_fee, update_fee = calc_total_fees()
    
    output_log.append(
        f"CALC: [{storage_A1_used} {storage_A2_used} {storage_B1_used} {storage_B2_used}] {storage_fee} {update_fee} {0}"
    )
    
    init_storage_data()
    
    return
    

    
def process_UPLOAD(i, query):
    """
    UPLOAD操作を処理する関数
    """
    storage_name = query[2]
    file_name = query[3]
    file_size = query[4]
    if storage_name not in STORAGE_DATA:
        output_log.append("UPLOAD: this storage location is not available on the free plan")
        return
    
    # 対象ストレージのファイルリストを取得
    files = STORAGE_DATA[storage_name]['files']

    # 同名ファイルの存在チェック
    if any(f['name'] == file_name for f in files):
        output_log.append("UPLOAD: file already exists")
        return
    
    
    # 無料枠を超えるか確認
    if is_upload_over(storage_name, file_size):          
        output_log.append("UPLOAD: free plan fee limit exceeded")
        return
    
    files.append({'name': file_name, 'size': file_size})# ファイル情報とサイズ情報を追加
    storage_fee, update_fee = calc_total_fees()
    output_log.append(f"UPLOAD: {storage_fee} {update_fee} {0}") 
    return 
    
def process_DELETE(i, query):
    """
    DELETE操作を処理する関数
    """
    storage_name = query[2]
    filename = query[3]
    if storage_name not in STORAGE_DATA:
        output_log.append("DELETE: this storage location is not available on the free plan")
        return
    files = STORAGE_DATA[storage_name]['files']
    if not any(f['name'] == filename for f in files):
        output_log.append("DELETE: file does not exist") # <-- メッセージ確認
        return
    file_size = get_file_size(storage_name, filename)
    
    if is_delete_over(storage_name, file_size):  
        output_log.append("DELETE: free plan fee limit exceeded")
        return
    files[:] = [f for f in files if f['name'] != filename]
    storage_fee, update_fee = calc_total_fees()
    output_log.append(f"DELETE: {storage_fee} {update_fee} {0}")

    return
    
def process_UPDATE(i, query):
    """
    UPDATE操作を処理する関数
    """
    storage_name = query[2]
    file_name = query[3]
    file_size = query[4]
    
    if storage_name not in STORAGE_DATA:
        output_log.append("UPDATE: this storage location is not available on the free plan")
        return
    
    files = STORAGE_DATA[storage_name]['files']

    if not any(f['name'] == file_name for f in files):
        output_log.append("UPDATE: file does not exist")
        return
    
    if is_update_over(storage_name, file_name, file_size):  
        output_log.append("UPDATE: free plan fee limit exceeded") 
        return
    
    file_obj = next((f for f in files if f['name'] == file_name), None)
    file_obj['size'] = file_size # ファイルサイズを更新
    
    storage_fee, update_fee = calc_total_fees()
    
    output_log.append(f"UPDATE: {storage_fee} {update_fee} {0}")
    return

def process_queries(input_data_list):

    for i, query in enumerate(input_data_list):
        if query[1] == 'CALC':
            process_CALC(i, query)
        elif query[1] == 'DELETE':
            process_DELETE(i, query)
        elif query[1] == 'UPLOAD':
            process_UPLOAD(i, query)     
        elif query[1] == 'UPDATE':
            process_UPDATE(i, query)
        if DEBUG: # デバッグ用にストレージデータを出力
            print(STORAGE_DATA)    
    return output_log        

def output_results(output_log):
    for line in output_log:
        print(line)                 

if __name__ == '__main__':
    input_data_list = input_data()
    result = process_queries(input_data_list)
    output_results(result)
    