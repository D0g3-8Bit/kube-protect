import mysql.connector
from db_connect import connect_db


def checkmd5(md5_value):
    # 建立数据库连接
    cnx = connect_db()
    cursor = cnx.cursor()

    # 构建查询语句
    query = "SELECT md5_value FROM file_md5 WHERE md5_value = %s"

    try:
        # 执行查询
        cursor.execute(query, (md5_value,))
        result = cursor.fetchone()

        # 检查结果是否存在
        if result:
            # 找到了对应的 md5 值
            return "true"
        else:
            # 未找到匹配的 md5 值
            return "404"
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return "Error occurred"
    finally:
        # 关闭游标和数据库连接
        cursor.close()
        cnx.close()

# 示例调用：
# md5_to_search = 'the_md5_value_to_search'
# print(find_md5_in_database(md5_to_search))
