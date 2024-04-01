import re

pattern = re.compile(r"\b(/etc/)?sendmail.cw\b")

text1 = "/etc/sendmail.cw"  # 这是包含 /etc 的路径
text2 = "/sendmail.cw"      # 这是不包含 /etc 的路径

match1 = pattern.search(text1)
match2 = pattern.search(text2)

if match1:
    print("Match found for '/etc/sendmail.cw'.")
else:
    print("Match for '/etc/sendmail.cw' does not exist.")

if match2:
    print("Match found for '/sendmail.cw'.")
else:
    print("Match for '/sendmail.cw' does not exist.")