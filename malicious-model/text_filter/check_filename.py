from db_connect import connect_db, close_db

def check_string_contains_table_content(test_string):
    # 数据库连接配置
    db_conn = connect_db()
    if db_conn is None:
        print("数据库连接失败")
        return "404"
    try:
        with db_conn.cursor() as cursor:
            # 执行 SQL 查询，获取所有的 file_path
            cursor.execute("SELECT file_path FROM file_path_configuration")
            records = cursor.fetchall()

            # 检查传入的字符串是否包含任何一个 file_path
            for record in records:
                if record[0] in test_string:
                    return 4  # 返回一个整数值，示例中使用 1
            # 如果没有找到任何匹配项，也可以选择返回一个不同的整数或者 None
            return "404"  # 未找到任何匹配项
    finally:
        close_db(db_conn)

# 示例调用函数
result = check_string_contains_table_content("some string that may contain a file_path")
print(result)  # 输出函数的返回值
