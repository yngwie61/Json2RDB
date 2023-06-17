# Json2RDB

## 何ができるか

1. Json2RDB.py

jsonデータを列にバラして保存したリレーショナルデータベースに対し、更新内容をjson形式で与えることで差分を更新するプログラム

2. httpd.py
FlaskをもちいてRDBからAPIレスポンスを生成する簡易HTTPサーバ。 etag検証の実行が可能
データの更新、参照は Json2RDB.py を使用

## 事前準備

- python実行環境
- sqlite3の実行環境
- redisの実行環境 (httpd.py中のetagのキャッシュ用)

```
brew install redis
redis-server
```

## Json2RDB.py

1. dbディレクトリにてtest.dbを作成する

```
[db]sqlite3 test.db
```

2. dbディレクトリにてinit.sqlを実行
```
[db]sqlite3 test.db < init.sql
```

3. update.jsonを編集し更新内容をjsonとして掲載

4. Json2RDB.py を実行

## 実行結果の例

```
before update data: {'id': 1、 'key1': 'value1', 'key2': 'value2', 'key3': 3}
new json data: {'id': 1, 'key1': 'diff_value1', 'key2': 'value2', 'key3': 30}
diff data: {'id': 1, 'key1': 'diff_value1', 'key3': 30}
after update data: {'id': 1, 'key1': 'diff_value1', 'key2': 'value2', 'key3': 30}
処理時間: 2.1761319999999973 ミリ秒
```

最初のデータをdbから取得し、 新しく投入するjsonと比較する。diff dataが差分情報。
差分データのみUPDATEして、 結果を出力している。


## httpd.py
Json2RDB.py を用いた簡易httpdサーバです。データの更新はjson形式のデータを元にJson2RDBの関数を用いて行われます。プログラム中ではid=1のデータに対して定期的に更新するように処理されています。
**(redisサーバをローカル環境に立ち上げてから使用するようにしてください。)**

### データの定期的な更新処理

update_example_api()関数は、Json2RDBの関数を用いて定期的にデータを更新します。

1. generate_random_string()関数を使用してランダムな文字列を生成し、新しいデータとして設定します。
2. SQLiteデータベースに接続し、現在のデータと新しいデータの差分を計算します。
3. clear_redis_cache()関数を呼び出してRedisのキャッシュを削除します。
4. データベースの変更をコミットし、接続を閉じます。
5. 更新処理を指定された間隔（15秒）でスケジュールします。

### APIエンドポイントの処理

/exampleエンドポイントにGETリクエストが送信された場合に処理が行われます。
1. リクエストのURLからURIを取得し、get_etag()関数を使用してETagを取得します。
2. リクエストヘッダーから送信されたETagと現在のETagを比較します。
3. ETagが一致する場合、ステータスコード304（Not Modified）を返し、レスポンスヘッダーに現在のETagを設定します。
4. ETagが一致しない場合、SQLiteデータベースに接続し、指定されたIDのデータを取得します。
5. レスポンスデータをJSON形式に変換し、ETagを計算して設定します。
6. sRedisにETagを保存し、レスポンスデータと共に200（OK）のステータスコードを返します。

### プログラムの実行

__name__が__main__となっている部分がプログラムのエントリーポイントです。
1. update_example_api()関数を呼び出して、初回のデータ更新をスケジュールします。
2. app.run()を実行することで、Flaskアプリケーションが起動し、APIエンドポイントが提供されます。
