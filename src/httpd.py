import threading
import random
import string
from flask import Flask, request, make_response
import redis
import json
import hashlib
from urllib.parse import urlparse
import sqlite3
from Json2RDB import Json2RDB
import os


app = Flask(__name__)
redis_client = redis.Redis(host='redis', port=6379)  # Redisクライアントを作成
j2db = Json2RDB(
    unique_key = "id",
    db_table_name = os.environ.get("MYSQL_DATABASE_TABLE_NAME"),
    db = os.environ.get("MYSQL_DATABASE"),
    host="mysql",
    password=os.environ.get("MYSQL_PASSWORD"),
    port=3306,
    user=os.environ.get("MYSQL_USER"),
    charset="utf8mb4",
    connect_timeout=60,
    read_timeout=60,
    write_timeout=30,
)

def clear_redis_cache():
    # キャッシュ一覧のキーを取得
    cache_keys = redis_client.keys('*')
    # キャッシュを削除
    for cache_key in cache_keys:
        redis_client.delete(cache_key)


def calculate_sha256_hash(data):
    # バイト列に変換
    data_bytes = data.encode('utf-8')
    # SHA-256ハッシュオブジェクトを作成
    sha256_hash = hashlib.sha256()
    # ハッシュを計算
    sha256_hash.update(data_bytes)
    # ハッシュ値を取得（16進数文字列）
    hash_value = sha256_hash.hexdigest()

    return hash_value


# ランダムな文字列を生成するヘルパー関数
def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))


# APIの定期的な更新処理
def update_example_api():
    content = generate_random_string(5)
    # データ生成. 実際には　SQLなどを実行する.
    new_json_data = {
        "id": 1,
        "key1": content,
        "key2": "value2",
        "key3": 300
    }

    # SQLiteデータベースに接続
    current_json_data = j2db.get_json_from_rdb(1)
    diff_json = j2db.get_diff_from_json(current_json_data, new_json_data)
    print(diff_json)
    j2db.update_db_from_json(diff_json)
    # キャッシュの削除, コミットと接続のクローズ
    clear_redis_cache()
    print("------------------UPDATE DB------------------")
    # 次の更新をスケジュール
    threading.Timer(15, update_example_api).start()  # 10秒後に更新


# ETagの取得
def get_etag(uri):
    return redis_client.get(uri)


@app.route('/example', methods=['GET'])
def example():
    uri = urlparse(request.url).path
    etag = request.headers.get('If-None-Match')
    id = request.args.get('id')
    key_uri = f"{uri}?id={id}"
    current_etag = get_etag(key_uri)
    if current_etag is not None:
        current_etag = current_etag.decode('utf-8')

    else:
        current_etag = ""

    if etag == current_etag:
        response = make_response('', 304)
        response.headers['ETag'] = current_etag

    else:
        print("------------------DBアクセスが発生します------------------")
        # SQLiteデータベースに接続
        response_json = j2db.get_json_from_rdb(id)
        response_string = json.dumps(response_json, indent=4)
        # SHA-256ハッシュを計算しetagとして設定
        new_etag = calculate_sha256_hash(response_string)
        # RedisにETagを保存
        redis_client.set(key_uri, new_etag)
        # レスポンス生成
        response = make_response(response_string, 200)
        response.headers['Contesnt-Type'] = 'application/json'
        response.headers['ETag'] = new_etag

    return response


if __name__ == '__main__':
    # 初回のDB更新をスケジュール
    update_example_api()
    app.run(host='0.0.0.0', port=5000)
