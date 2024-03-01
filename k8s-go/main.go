package main

import (
	"malicious/mypackage"
	"time"
)

const logFilePath = "/root/k8s-scanner/logfile.json"

func periodicallyCallFunctions() {
	for {
		// 调用 mypackage 中的 GetPod 函数
		mypackage.GetPod()

		// 调用 mypackage 中的 ProcessLogFile 函数，并处理可能发生的错误
		err := mypackage.ProcessLogFile(logFilePath)
		if err != nil {
			return
		}

		// 休眠5分钟后再次调用函数
		time.Sleep(5 * time.Minute)
	}
}
func main() {
	go periodicallyCallFunctions()
	select {}
}
