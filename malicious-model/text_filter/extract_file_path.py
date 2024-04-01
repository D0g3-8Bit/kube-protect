import re
import os
from db_connect import connect_db
from text_filter.getmd5 import get_md5
from text_filter.make_short_dockerid import remove_prefix_suffix_and_slice
from text_filter.checkmd5 import checkmd5


# 从数据库中获取基础路径并计算文件的完整路径及其MD5
def process_filename(container_id, file_name):
    # 连接数据库
    db_conn = connect_db()
    try:
        with db_conn.cursor() as cursor:
            # 查询基础路径
            cursor.execute("SELECT file_path FROM file_ahead_path")
            file_paths = cursor.fetchall()

            # 对于查询结果中的每个基础路径
            for path in file_paths:
                full_path = os.path.join(path[0], file_name)
                # 如果该组合路径指向一个文件
                if os.path.isfile(full_path):
                    # 计算MD5并返回
                    md5_value = get_md5(container_id, full_path)
                    result = checkmd5(md5_value)
                    if result == "true":
                        return full_path
                    else:
                        return "404"

            # 如果文件没有找到，则返回'404'
            return '404'
    except Exception as e:
        # 发生异常，输出异常信息并返回错误
        print(f"Error occurred: {e}")
        return 'Error occurred'
    finally:
        db_conn.close()


# 提取文件名，判断是否为绝对路径，不是的话查找其完整路径并进行处理
def extract_filename(cgroup_path, text):
    match = re.search(r'\b(?:touch|add|copy|vim)\s+(\S+)', text)
    container_id = remove_prefix_suffix_and_slice(cgroup_path)
    if match:
        file_name = match.group(1)
        if os.path.isabs(file_name):
            md5_value = get_md5(container_id, file_name)
            result = checkmd5(md5_value)
            if result == "true":
                return file_name
        else:
            # 如果不是绝对路径，调用之前的函数来处理
            process_filename(container_id, file_name)
    else:
        return "404"
