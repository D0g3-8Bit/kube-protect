from datetime import datetime, timezone, timedelta

# 假设 current_beijing_time 是已经转换时区的datetime对象
current_beijing_time = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8)))

# 将时间格式化为字符串
# 例如: "2024-03-28 01:37:53"
time_str = current_beijing_time.strftime("%Y-%m-%d %H:%M:%S")

print("Formatted Beijing Time for Database:", time_str)