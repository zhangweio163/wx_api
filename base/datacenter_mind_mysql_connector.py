from  conf.setting import datacenter_connect_params
import pymysql
class DataCenterMindMySQLConnector:
    def __init__(self):
        self.connection = None

    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = pymysql.connect(
                host=datacenter_connect_params["host"],
                port=datacenter_connect_params["port"],
                user=datacenter_connect_params["user"],
                password=datacenter_connect_params["password"],
                database=datacenter_connect_params["database"],
                connect_timeout=datacenter_connect_params["connect_timeout"],
                cursorclass=pymysql.cursors.DictCursor  # 使用字典游标
            )
            print("Database connection established.")
        except pymysql.MySQLError as e:
            print(f"Error connecting to database: {e}")
            self.connection = None



    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

    def execute_query(self, query, params=None):
        """执行查询并返回结果"""
        if not self.connection:
            print("No database connection.")
            return None

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
                return result
        except pymysql.MySQLError as e:
            print(f"Error executing query: {e}")
            return None

    def truncate_table(self, table_name):
        """清空指定表的数据"""
        if not self.connection:
            print("No database connection.")
            return False

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE {table_name}")
            self.connection.commit()
            print(f"Table {table_name} truncated successfully.")
            return True
        except pymysql.MySQLError as e:
            print(f"Error truncating table {table_name}: {e}")
            self.connection.rollback()
            return False