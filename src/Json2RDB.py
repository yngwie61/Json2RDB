import pymysql
import numpy as np
import json
import timeit
import os
import sys

class Json2RDB(pymysql.Connection):
    def __init__(self, *args, **kwargs):
        self.unique_key = kwargs.pop('unique_key', None)
        self.db_table_name = kwargs.pop('db_table_name', None)
        self.connection = pymysql.connect(*args, **kwargs, cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.connection.cursor()

    def close_connection(self):
        self.cursor.close()
        self.connection.close()

    def get_table_info(self):
        query = "SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_DEFAULT, EXTRA " \
                "FROM INFORMATION_SCHEMA.COLUMNS " \
                f"WHERE TABLE_NAME = '{self.db_table_name}'"
        self.cursor.execute(query)
        table_info = self.cursor.fetchall()
        schema_array = []
        for row in table_info:
            column_name = row['COLUMN_NAME']
            data_type = row['DATA_TYPE']
            is_nullable = row['IS_NULLABLE']
            key = row['COLUMN_KEY']
            default_value = row['COLUMN_DEFAULT']
            extra = row['EXTRA']
            schema = {
                'column_name': column_name,
                'data_type': data_type,
                'is_nullable': is_nullable,
                'key': key,
                'default_value': default_value,
                'extra': extra
            }
            schema_array.append(schema)
        return schema_array

    def get_json_from_rdb(self, id):
        select_query = f"SELECT * FROM {self.db_table_name} WHERE {self.unique_key} = %s"
        self.cursor.execute(select_query, (int(id),))
        results = self.cursor.fetchall()

        if not results:
            return {}

        if len(results) > 1:
            raise Exception("DB Unique Key Error")

        result = results[0]
        result_json = {}
        for column_name, column_value in result.items():
            result_json[column_name] = column_value

        return result_json

    def update_db_from_json(self, diff_json):
        if not diff_json:
            return True

        id = int(diff_json[self.unique_key])
        update_fields = []
        update_values = []
        for key, value in diff_json.items():
            if key != self.unique_key:
                update_fields.append(f"`{key}` = %s")
                update_values.append(value)

        if not update_fields:
            return False

        update_query = f"UPDATE {self.db_table_name} SET {', '.join(update_fields)} WHERE {self.unique_key} = %s"
        update_values.append(id)  # idを追加
        self.cursor.execute(update_query, tuple(update_values))

        return True

    def get_diff_from_json(self, current_json_data, new_json_data):
        if current_json_data[self.unique_key] == new_json_data[self.unique_key]:
            if self._validate_json(current_json_data, new_json_data):
                id = current_json_data[self.unique_key]
                diff_json = {self.unique_key: id}
                for key in list(current_json_data.keys()):
                    if current_json_data[key] != new_json_data[key]:
                        diff_json[key] = new_json_data[key]
                return diff_json
            else:
                raise Exception("Json Schema Error")

    def _validate_json(self, current_json_data, new_json_data):
        list1 = list(current_json_data.keys())
        list2 = list(new_json_data.keys())
        key_diff = np.setdiff1d(list1, list2)
        if len(key_diff) == 0:
            return True
        else:
            # もしkey diffがあったら処理は中断
            return False


def main():
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
    current_json = j2db.get_json_from_rdb(1)
    print(current_json)
    update_json = {
        "id": 1,
        "key1": "diff_value1",
        "key2": "value2",
        "key3": 30
    }
    diff_json = j2db.get_diff_from_json(current_json, update_json)
    print(diff_json)
    j2db.update_db_from_json(diff_json)
    result_json = j2db.get_json_from_rdb(1)
    print(result_json)
    j2db.close_connection()

if __name__ == '__main__':
    main()