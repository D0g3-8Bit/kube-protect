import mysql.connector
from bcc import BPF
from datetime import datetime, timezone, timedelta
import os
import ctypes as ct
from kubernetes import client, config
from text_filter.rules import check_sensitive_content
from db_connect import connect_db, close_db
from text_filter.extract_file_path import extract_filename
from text_filter.check_filename import check_string_contains_table_content
from text_filter.check_ssh_out import match_string_with_db

# 加载 Kubernetes 配置
config.load_incluster_config()
v1 = client.CoreV1Api()

# 获取当前的节点信息
node_name = os.getenv("NODE_NAME")

# 加载 eBPF 程序
b = BPF(src_file="execsnoop.c")


# BPF 程序中定义的输出数据结构
class Data(ct.Structure):
    _fields_ = [
        ("pid", ct.c_uint),
        ("comm", ct.c_char * 16),  # TASK_COMM_LEN 通常为 16
        ("cgroup_path", ct.c_char * 128),
        ("argv", ct.c_char * (5 * 64)),  # TOTAL_MAX_ARGS * ARGSIZE
    ]


# 监听事件打印函数
def print_event(cpu, data, size):
    event = ct.cast(data, ct.POINTER(Data)).contents
    args = event.argv.decode(errors='replace').split('\0')
    current_beijing_time = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8)))
    time_str = current_beijing_time.strftime("%Y-%m-%d %H:%M:%S")
    text_to_predict = ' '.join(filter(None, args))
    result_int_label = check_sensitive_content(text_to_predict)
    result_label = "null"
    if result_int_label == 6:
        result = extract_filename(event.cgroup_path, text_to_predict)
        if result != "404":
            result_label = "恶意文件:" + result
    elif result_int_label == 1:
        result_label = "cgroup逃逸"
    elif result_int_label == 2:
        result_label = "容器特权启动"
    elif result_int_label == 3:
        result_label = "容器挂载sock"
    elif result_int_label == 4:
        result_label = "敏感文件访问"
    elif result_int_label == 5:
        result_label = "新的进程或容器启动"
    elif result_int_label == 0:
        result = check_string_contains_table_content(text_to_predict)
        if result == 4:
            result_label = "配置文件访问"
        else:
            result = match_string_with_db(text_to_predict)
            if result == 7:
                result_label = "ssh外连"
            else:
                result_label = "404"
    else:
        result_label = "404"
    db_conn = connect_db()  # 假设该函数正确实现且返回数据库连接
    if db_conn is not None and result_label != '404':
        try:
            with db_conn.cursor() as cursor:
                insert_statement = """
                INSERT INTO kernel_calls (timestamp, node_name, container_id, pid, args ,result_label)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_statement,
                               (time_str, node_name, event.cgroup_path.decode().strip(), event.pid, text_to_predict,
                                result_label))
                db_conn.commit()
        except mysql.connector.Error as e:
            print(f"数据插入失败：{e}")
        finally:
            close_db(db_conn)


# 绑定性能事件
b["events"].open_perf_buffer(print_event)
try:
    while True:
        b.perf_buffer_poll()
except KeyboardInterrupt:
    pass