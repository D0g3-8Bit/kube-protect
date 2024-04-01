# db_connect.py
import os
import mysql.connector
from mysql.connector import Error


def create_table_if_not_exists(connection):
    cursor = connection.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS kernel_calls (
        id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp DATETIME,
        node_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
        container_id VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
        pid INT,
        args TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
        result_label VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
    ) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    try:
        cursor.execute(create_table_query)
        connection.commit()
    except Error as e:
        print("创建表时出错：", e)


def connect_db():
    db_host = os.getenv('DB_HOST')
    db_name = 'k8s'
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASSWORD')

    try:
        connection = mysql.connector.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_pass
        )
        create_table_if_not_exists(connection)
        return connection
    except Error as e:
        print("连接数据库时出错：", e)
        return None


def close_db(connection):
    if connection and connection.is_connected():
        connection.close()