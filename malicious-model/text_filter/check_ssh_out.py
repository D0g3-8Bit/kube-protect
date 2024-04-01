from db_connect import connect_db

def match_string_with_db(string_to_check):

    # 建立数据库连接
    conn = connect_db()
    cursor = conn.cursor()

    # 执行查询语句，获取数据库中的数据
    cursor.execute("SELECT address FROM connection_address")

    # 获取查询结果
    rows = cursor.fetchall()

    # 关闭游标和数据库连接
    cursor.close()
    conn.close()

    # 检查字符串是否包含数据库中的任何条目
    for row in rows:
        if row[0] in string_to_check:
            # 如果匹配到了，返回整数7
            return 7

    # 如果没有匹配到任何内容，返回字符串"404"
    return "404"
