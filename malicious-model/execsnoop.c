#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
#include <net/sock.h>
#include <bcc/proto.h>

#define ARGSIZE 64
#define TOTAL_MAX_ARGS 5
#define FULL_MAX_ARGS_ARR (TOTAL_MAX_ARGS * ARGSIZE)
#define LAST_ARG (FULL_MAX_ARGS_ARR - ARGSIZE)
// 这里定义 eBPF 程序需要输出的数据结构
struct data_t {
    u32 pid;  // 进程 ID
    char comm[TASK_COMM_LEN]; // 进程名
    char cgroup_path[128];    // 假设 cgroup 路径不超过 128 字节
    char argv[FULL_MAX_ARGS_ARR];
    unsigned int args_size;
};
// 同之前的程序定义
BPF_PERF_OUTPUT(events);

// 辅助函数用于从用户空间读取字符串
static int __bpf_read_arg_str(struct data_t *data, const char *ptr) {
    if (data->args_size >= LAST_ARG) {
        return -1;
    }

    // 读取参数到 data->argv 数组中，但留一个字符的空间用于空格
    int ret = bpf_probe_read_user_str(&data->argv[data->args_size], ARGSIZE - 1, (void *)ptr);
    if (ret <= 0 || ret >= ARGSIZE) {
        // 字符串长度超过了 ARSIZE-1 或读取出错
        return -1;
    }

    // 调整 args_size 为实际读取的长度，不包括末尾的 '\0'
    data->args_size += ret - 1;

    // 在此处添加空格，确保不会覆盖预留的空间以及 data->argv 的最后一个元素
    if (data->args_size < LAST_ARG) {
        data->argv[data->args_size] = ' ';
        data->args_size++;
    }

    return 0;
}

// execve 系统调用触发时会调用此函数
static __always_inline int get_cgroup_info(struct pt_regs *ctx, const char __user *const __user *argv) {
    struct data_t data = {};
    struct css_set *cgroups;
    struct cgroup_subsys_state *css;
    u64 id;
    data.args_size = 0;  // 初始化参数大小

    // 循环通过 __bpf_read_arg_str 读取命令行参数
    #pragma unroll
    for (int i = 0; i < TOTAL_MAX_ARGS; i++) {
        // 如果 argp 为空，则跳出循环
        if (argv[i] == NULL) {
            break;
        }
        // 调用__bpf_read_arg_str函数来读取字符串
        if (__bpf_read_arg_str(&data, argv[i]) != 0) {
            break; // 读取失败或完成
        }
    }

    // 获取当前进程的 task_struct
    struct task_struct *task = (struct task_struct *)bpf_get_current_task();

    // 获取进程 ID 和线程组 ID
    data.pid = bpf_get_current_pid_tgid() >> 32;

    // 获取进程命令名
    bpf_get_current_comm(&data.comm, sizeof(data.comm));

    cgroups = task->cgroups;
    if (!cgroups) {
        return 0;
    }

    // 关注的是第一个 cgroup subsystem
    css = cgroups->subsys[0];
    if (!css) {
        return 0;
    }

    bpf_probe_read_str(&data.cgroup_path, sizeof(data.cgroup_path), css->cgroup->kn->name);

    // 输出数据到用户空间
    events.perf_submit(ctx, &data, sizeof(data));

    return 0;
}

// 附加到 execve syscall 的 enter 钩子
TRACEPOINT_PROBE(syscalls, sys_enter_execve) {
    // 获取 argv 值
    const char __user *const __user *argv = (const char __user *const __user *)args->argv;
    return get_cgroup_info(args, argv);
}
