# Json2RDB
save json to relational database


## 何ができるか
jsonデータを列にバラして保存したリレーショナルデータベースに対し、更新内容をjson形式で与えることで差分を更新するプログラム


## 事前準備

- python実行環境
- sqlite3の実行環境

## 使用方法

1. dbディレクトリにてtest.dbを作成する

```
[db]sqlite3 test.db
```

2. dbディレクトリにてinit.sqlを実行
```
[db]sqlite3 test.db < init.sql
```

3. update.jsonを編集し更新内容をjsonとして掲載

4. DiffJson.jsonを実行

## 実行結果の例

```
before update data: {'id': 1, 'key1': 'value1', 'key2': 'value2', 'key3': 3}
new json data: {'id': 1, 'key1': 'diff_value1', 'key2': 'value2', 'key3': 30}
diff data: {'id': 1, 'key1': 'diff_value1', 'key3': 30}
after update data: {'id': 1, 'key1': 'diff_value1', 'key2': 'value2', 'key3': 30}
処理時間: 2.1761319999999973 ミリ秒
```

最初のデータをdbから取得し, 新しく投入するjsonと比較する.diff dataが差分情報.
差分データのみUPDATEして, 結果を出力している.
