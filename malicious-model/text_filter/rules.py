# rules.py

import re

# text = "/var/run/docker.sock"
docker_cgroup = [
    re.compile(r"--cap-add=SYS_ADMIN", re.IGNORECASE),
    re.compile(r"mount\s+-t\s+cgroup\s+-o\s+.*\s+cgroup\s+.*", re.IGNORECASE),
    re.compile(r"mount\s+-o\s+.*\s+cgroup\s+.*\s+-t\s+cgroup", re.IGNORECASE),
    re.compile(r"echo\s+1\s+>\s+.*\s+/notify_on_release", re.IGNORECASE),
    re.compile(r"echo\s+.*/cmd", re.IGNORECASE),
    re.compile(r"chmod\s+a+x\s+/cmd", re.IGNORECASE),
    re.compile(r'sh\s+-c\s+"echo\s+.*/cgroup.procs"', re.IGNORECASE),
]

privileged = [
    re.compile(r"privileged", re.IGNORECASE),
    re.compile(r"cat\s+/proc/self/status\s+.*\s+grep\s+.*", re.IGNORECASE),
    re.compile(r"cat\s+.*/shadow", re.IGNORECASE),
]

docker_sock = [
    re.compile(r"docker.sock", re.IGNORECASE),
]


sensitive_documents = [
    re.compile(r"httpd.conf", re.IGNORECASE),
    re.compile(r"php.ini", re.IGNORECASE),
    re.compile(r"ssh_config", re.IGNORECASE),
    re.compile(r"termcap", re.IGNORECASE),
    re.compile(r"xinetd.d", re.IGNORECASE),
    re.compile(r"vsftpd.conf", re.IGNORECASE),
    re.compile(r"xinetd.conf", re.IGNORECASE),
    re.compile(r"protocols", re.IGNORECASE),
    re.compile(r"logrotate.conf", re.IGNORECASE),
    re.compile(r"ld.so.conf", re.IGNORECASE),
    re.compile(r"shadow", re.IGNORECASE),
    re.compile(r"resolv.conf", re.IGNORECASE),
    re.compile(r"sendmail.cw", re.IGNORECASE),
    re.compile(r"(cat)?\s+passwd", re.IGNORECASE),
    re.compile(r"(cat)?\s+shadow", re.IGNORECASE),
    re.compile(r"inputrc", re.IGNORECASE),
    re.compile(r"/issue/net", re.IGNORECASE),
    re.compile(r"rc.local", re.IGNORECASE),
    re.compile(r"hosts.deny", re.IGNORECASE),
    re.compile(r"/etc/bashrc", re.IGNORECASE),
    re.compile(r"000-default.conf", re.IGNORECASE),
    re.compile(r"apache2.conf", re.IGNORECASE),
    re.compile(r"nginx.conf", re.IGNORECASE),
    re.compile(r"authorized_keys", re.IGNORECASE),
    re.compile(r"id_rsa", re.IGNORECASE),
    re.compile(r"id_rsa.keystore", re.IGNORECASE),
    re.compile(r"id_rsa.pub", re.IGNORECASE),
    re.compile(r"known_hosts", re.IGNORECASE),
    re.compile(r".bash_history", re.IGNORECASE),
    re.compile(r".mysql_history", re.IGNORECASE),
    re.compile(r"MetaBase.xml", re.IGNORECASE),
    re.compile(r"boot.ini", re.IGNORECASE),
    re.compile(r"sudoers", re.IGNORECASE),
]
check_make_file = [
    re.compile(r'\b(?:touch|add|copy|vim)(\S+)', re.IGNORECASE),
]

check_new_shell = [
    re.compile(r'bash\s+',re.IGNORECASE),
    re.compile(r'sh\s+',re.IGNORECASE),
    re.compile(r'powershell\s+',re.IGNORECASE),
]
def check_sensitive_content(text):
    for pattern in docker_cgroup:
        if pattern.search(text):
            return 1
    for pattern in privileged:
        if pattern.search(text):
            return 2
    for pattern in docker_sock:
        if pattern.search(text):
            return 3
    for pattern in sensitive_documents:
        if pattern.search(text):
            return 4
    for pattern in check_new_shell:
        if pattern.search(text):
            return 5
    for pattern in check_make_file:
        if pattern.search(text):
            return 6
    return 0
