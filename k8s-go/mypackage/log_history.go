package mypackage

import (
	"bufio"
	"context"
	"fmt"
	log "github.com/sirupsen/logrus"
	v1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"os"
)

const logFilePath = "/root/k8s-scanner/logfile.json"

func init() {
	// 删除现有的日志文件以便新的运行不会追加到旧的日志中
	err := os.Remove(logFilePath)
	if err != nil && !os.IsNotExist(err) { // 如果文件不存在则忽略错误
		log.Errorf("Unable to remove existing log file: %v", err)
	} else {
		log.Info("Existing log file removed.")
	}

	// 这里我们可以设置日志的标准配置，这样就不需要在 processLog 中每次都设置
	log.SetFormatter(&log.JSONFormatter{})
	log.SetLevel(log.InfoLevel)
	log.SetOutput(os.Stderr) // 默认使用标准错误输出，直到我们打开日志文件
}
func getPodLogs(clientset *kubernetes.Clientset, podName string, namespace string) error {
	podLogOpts := v1.PodLogOptions{}
	req := clientset.CoreV1().Pods(namespace).GetLogs(podName, &podLogOpts)
	podLogs, err := req.Stream(context.TODO())
	if err != nil {
		log.Errorf("Error getting logs of pod %s: %v", podName, err)
		return err
	}

	defer podLogs.Close()

	scanner := bufio.NewScanner(podLogs)
	for scanner.Scan() {
		if IsMaliciousLog(scanner.Text()) == 1 {
			processLog(scanner.Text(), podName)
		} else {
			continue
		}
	}
	if err := scanner.Err(); err != nil {
		log.Errorf("Error reading logs of pod %s: %v", podName, err)
		// Return error instead of just logging it
		return err
	}

	return nil
}

func processLog(logStr string, podName string) {
	//fmt.Println("success log in")

	// 创建日志文件，并设置为log输出
	file, err := os.OpenFile(logFilePath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	if err == nil {
		log.SetOutput(file)
	} else {
		log.Info("Failed to log to file, using default stderr")
	}

	// 格式化日志，添加 pod name
	formattedLog := fmt.Sprintf("%s | podname=%s", logStr, podName)

	// 开始写日志
	log.WithFields(log.Fields{
		"logContent": formattedLog,
	}).Info()
}

func GetPod() {
	// 使用 InClusterConfig 获取当前集群配置
	config, err := rest.InClusterConfig()
	if err != nil {
		panic(err.Error())
	}

	// 使用集群配置创建 clientset
	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		panic(err.Error())
	}

	// 获取所有命名空间中的Pods
	pods, err := clientset.CoreV1().Pods("").List(context.TODO(), metav1.ListOptions{})
	if err != nil {
		panic(err.Error())
	}

	// 循环获取所有Pod的日志
	for _, pod := range pods.Items {
		getPodLogs(clientset, pod.Name, pod.Namespace) // 确保提供合适的getPodLogs函数
	}
}

//GetPod --> getPodlogs --> 处理函数
