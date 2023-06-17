import sqlite3
import numpy as np
import json
import timeit


def getTableInfo(table_name, cursor):
    query = f"PRAGMA table_info({table_name})"
    cursor.execute(query)
    table_info = cursor.fetchall()
    schema_array = []
    for row in table_info:
        schema_array.append(row)
    return schema_array


def getJsonFronRDB(id, cursor):
    # JSONデータをデータベースに挿入
    assumed_key_array = getTableInfo("dummy", cursor)
    select_query = f"SELECT * FROM dummy WHERE id = ?"
    cursor.execute(select_query, (id,))
    results = cursor.fetchall()
    result_json = {}
    if len(results) == 0:
        # 結果がない
        return result_json

    elif len(results) > 1:
        raise Exception("Unique Key Error")

    else:
        for result, key in zip(results[0], assumed_key_array):
            result_json[key[1]] = result

        return result_json


def updateDBFromJson(diff_json, cursor):
    key_query_array = []
    value_array = []
    id = diff_json["id"]
    for key in list(diff_json.keys()):
        if key != "id":
            key_query_array.append(f"{key} = ?")
            value_array.append(diff_json[key])
    if len(key_query_array) == 0:
        return False

    else:
        key_query = ', '.join(key_query_array)
        value_tuple = tuple(value_array)
        # JSONデータをデータベースに挿入
        update_query = f"UPDATE dummy SET {key_query} WHERE id = {id}"
        cursor.execute(update_query, value_tuple)

        return True


def validateJson(current_json_data, new_json_data):
    list1 = list(current_json_data.keys())
    list2 = list(new_json_data.keys())
    key_diff = np.setdiff1d(list1, list2)
    if len(key_diff) == 0:
        return True
    else:
        ### もしkey diffがあったら処理は中断
        return False


def getDiffFronJson(current_json_data, new_json_data):
    if (current_json_data["id"] == new_json_data["id"]):
        if validateJson(current_json_data, new_json_data):
            id = current_json_data["id"]
            diff_json = {"id": id}
            for key in list(current_json_data.keys()):
                if current_json_data[key] != new_json_data[key]:
                    # diff_json[key] = {"old": current_json_data[key], "new": new_json_data[key]}
                    diff_json[key] = new_json_data[key]
            # 差分をSQLでUPDATEしたら良い
            return diff_json
        else:
            raise Exception("Json Schema Error")


def main(id_key, json_path):
    # SQLiteデータベースに接続
    connection = sqlite3.connect('db/test.db')
    cursor = connection.cursor()

    # DBからの読み込み
    with open(json_path) as f:
        new_json_data = json.load(f)
        current_json_data = getJsonFronRDB(new_json_data[id_key], cursor)
        diff_json = getDiffFronJson(current_json_data, new_json_data)
        print(diff_json)
        updateDBFromJson(diff_json, cursor)

    # コミットと接続のクローズ
    connection.commit()
    connection.close()


if __name__ == '__main__':
    # 実行時間を計測
    id_key = "id"
    json_path = 'update.json'
    execution_time = timeit.timeit(lambda: main(id_key, json_path), number=1) * 1000 # msec変換
    print(f"処理時間: {execution_time} ミリ秒")
