import hashlib
import os
import subprocess

def get_md5(container_id, file_path):
    # 通过 Docker inspect 获取容器的存储层目录
    def get_container_layer_path(container_id):
        cmd = ['docker', 'inspect', '--format={{.GraphDriver.Data.MergedDir}}', container_id]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise Exception(f"Error getting container layer path: {result.stderr}")
        return result.stdout.strip()

    # 获取存储层路径
    container_layer_path = get_container_layer_path(container_id)

    # 计算绝对路径
    absolute_file_path = os.path.join(container_layer_path, file_path.lstrip('/'))

    # 确保文件存在
    if not os.path.exists(absolute_file_path):
        raise FileNotFoundError(f"File {absolute_file_path} not found")

    # 计算 MD5 哈希值
    hash_md5 = hashlib.md5()
    with open(absolute_file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

