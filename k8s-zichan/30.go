package main

import (
	"context"
	"database/sql"
	"flag"
	"fmt"
	"time"

	_ "github.com/go-sql-driver/mysql"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
)

func runTask() {
	flag.Parse()

	// 用 InClusterConfig 替代 kubeconfig
	config, err := rest.InClusterConfig()
	if err != nil {
		fmt.Printf("无法创建 Kubernetes 客户端配置: %v\n", err)
		return
	}

	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		fmt.Printf("无法创建 Kubernetes 客户端集合: %v\n", err)
		return
	}

	ctx := context.TODO()

	nodes, err := clientset.CoreV1().Nodes().List(ctx, metav1.ListOptions{})
	if err != nil {
		fmt.Printf("无法获取节点信息: %v\n", err)
		return
	}

	db, err := sql.Open("mysql", "uu2fu3o:uu2fu3o@tcp(mysql:3306)/k8s")
	if err != nil {
		fmt.Printf("无法连接到数据库: %v\n", err)
		return
	}
	defer db.Close()

	// 删除现有表
	dropTablesSQL := `
	DROP TABLE IF EXISTS node;
`
	_, err = db.Exec(dropTablesSQL)
	if err != nil {
		fmt.Printf("无法删除表: %v\n", err)
		return
	}

	dropTablesSQL = `
	DROP TABLE IF EXISTS pod;
`
	_, err = db.Exec(dropTablesSQL)
	if err != nil {
		fmt.Printf("无法删除表: %v\n", err)
		return
	}

	dropTablesSQL = `
	DROP TABLE IF EXISTS services;
`
	_, err = db.Exec(dropTablesSQL)
	if err != nil {
		fmt.Printf("无法删除表: %v\n", err)
		return
	}

	dropTablesSQL = `
	DROP TABLE IF EXISTS deployment;
`
	_, err = db.Exec(dropTablesSQL)
	if err != nil {
		fmt.Printf("无法删除表: %v\n", err)
		return
	}

	createTableSQL := `
    CREATE TABLE IF NOT EXISTS node (
        id INT PRIMARY KEY AUTO_INCREMENT,
        node_name VARCHAR(255),
        ip_address VARCHAR(255),
        os_image VARCHAR(255),
        kernel_version VARCHAR(255),
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
`

	_, err = db.Exec(createTableSQL)
	if err != nil {
		fmt.Printf("无法创建表: %v\n", err)
		return
	}
	// 创建Pods表
	createPodsTableSQL := `
    CREATE TABLE IF NOT EXISTS pod (
  		id INT PRIMARY KEY AUTO_INCREMENT,
  		pod_name VARCHAR(255),
  		namespace VARCHAR(255),
  		status VARCHAR(255),
  		pod_ip VARCHAR(255),
  		container_name VARCHAR(255),
  		container_image VARCHAR(255),
  		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
	) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
`
	_, err = db.Exec(createPodsTableSQL)
	if err != nil {
		fmt.Printf("无法创建 Pods 表: %v\n", err)
		return
	}

	// 创建 Services 表
	createServicesTableSQL := `
    CREATE TABLE IF NOT EXISTS services (
  		id INT PRIMARY KEY AUTO_INCREMENT,
  		service_name VARCHAR(255),
  		namespace VARCHAR(255),
  		service_type VARCHAR(255),
  		port_name VARCHAR(255),
  		port_value INT,
  		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
	) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
`
	_, err = db.Exec(createServicesTableSQL)
	if err != nil {
		fmt.Printf("无法创建 Services 表: %v\n", err)
		return
	}

	// 创建 Deployments 表
	createDeploymentsTableSQL := `
    CREATE TABLE IF NOT EXISTS deployment (
  		id INT PRIMARY KEY AUTO_INCREMENT,
  		deployment_name VARCHAR(255) NOT NULL,
  		namespace VARCHAR(255) NOT NULL,
  		replicas INT,
  		available_replicas INT,
  		update_strategy VARCHAR(255),
  		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
	) 
`
	_, err = db.Exec(createDeploymentsTableSQL)
	if err != nil {
		fmt.Printf("无法创建 Deployments 表: %v\n", err)
		return
	}

	for _, node := range nodes.Items {
		insertSQL := `
        INSERT INTO node (node_name, ip_address, os_image, kernel_version, updated_at)
        VALUES (?, ?, ?, ?, ?)
    `

		_, err = db.Exec(insertSQL, node.Name, node.Status.Addresses[0].Address, node.Status.NodeInfo.OSImage, node.Status.NodeInfo.KernelVersion, time.Now())
		if err != nil {
			fmt.Printf("无法插入数据: %v\n", err)
			return
		}
	}

	// 获取 Pod, Services, Deployment 信息
	//...
	pods, _ := clientset.CoreV1().Pods("").List(ctx, metav1.ListOptions{})
	services, _ := clientset.CoreV1().Services("").List(ctx, metav1.ListOptions{})
	deployments, _ := clientset.AppsV1().Deployments("").List(ctx, metav1.ListOptions{})
	timeNow := time.Now()
	for _, pod := range pods.Items {
		for _, container := range pod.Spec.Containers {
			_, err = db.Exec("INSERT INTO pod (pod_name, namespace, status, pod_ip, container_name, container_image, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
				pod.Name, pod.Namespace, pod.Status.Phase, pod.Status.PodIP, container.Name, container.Image, timeNow)
			if err != nil {
				fmt.Println("Error inserting Pod:", err)
			}
		}
	}

	for _, service := range services.Items {
		for _, port := range service.Spec.Ports {
			_, err = db.Exec("INSERT INTO services (service_name, namespace, service_type, port_name, port_value, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
				service.Name, service.Namespace, service.Spec.Type, port.Name, port.Port, timeNow)
			if err != nil {
				fmt.Println("Error inserting Service:", err)
			}
		}
	}

	for _, deployment := range deployments.Items {
		_, err = db.Exec("INSERT INTO deployment (deployment_name, namespace, replicas, available_replicas, update_strategy, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
			deployment.Name, deployment.Namespace, *deployment.Spec.Replicas, deployment.Status.AvailableReplicas, deployment.Spec.Strategy.Type, timeNow)
		if err != nil {
			fmt.Println("Error inserting Deployment:", err)
		}
	}
	//...
	// 打印集群节点信息
	fmt.Println("集群节点信息:")
	for _, node := range nodes.Items {
		fmt.Printf("节点名称: %s\n", node.Name)
		fmt.Printf("节点IP地址: %s\n", node.Status.Addresses[0].Address)
		fmt.Printf("节点操作系统：%s\n", node.Status.NodeInfo.OSImage)
		fmt.Printf("节点内核版本：%s\n", node.Status.NodeInfo.KernelVersion)
		fmt.Println("--------------------")
	}

	// 打印 Pods 信息并将数据写入数据库
	fmt.Println("Pods信息:")
	for _, pod := range pods.Items {
		fmt.Printf("Pod名称: %s\n", pod.Name)
		fmt.Printf("Namespace: %s\n", pod.Namespace)
		fmt.Printf("状态: %s\n", pod.Status.Phase)
		fmt.Printf("启动时间: %v\n", pod.Status.StartTime)
		fmt.Printf("Pod IP： %s\n", pod.Status.PodIP)
		for _, container := range pod.Spec.Containers {
			fmt.Printf("容器名称： %s\n", container.Name)
			fmt.Printf("容器镜像： %s\n", container.Image)
		}
		fmt.Println("--------------------")
	}

	// 打印 Services 信息并将数据写入数据库
	fmt.Println("Services信息:")
	for _, service := range services.Items {
		fmt.Printf("Service名称: %s\n", service.Name)
		fmt.Printf("Namespace: %s\n", service.Namespace)
		fmt.Printf("Service类型: %s\n", service.Spec.Type)
		if len(service.Spec.Ports) > 0 {
			for i, port := range service.Spec.Ports {
				fmt.Printf("端口%d: %d->%d/%s\n", i, port.Port, port.NodePort, port.Protocol)
			}
		}
		fmt.Println("--------------------")
	}

	// 打印 Deployments 信息并将数据写入数据库
	fmt.Println("Deployments信息:")
	for _, deployment := range deployments.Items {
		fmt.Printf("Deployment名称: %s\n", deployment.Name)
		fmt.Printf("Namespace: %s\n", deployment.Namespace)
		fmt.Printf("副本数: %d\n", *deployment.Spec.Replicas)
		fmt.Printf("可用副本数: %d\n", deployment.Status.AvailableReplicas)
		fmt.Printf("更新策略: %s\n", deployment.Spec.Strategy.Type)
		fmt.Println("--------------------")
	}
}

func main() {
	// Set up a ticker to run runTask every minute
	ticker := time.NewTicker(4 * time.Minute)

	for {
		select {
		case <-ticker.C:
			runTask()
		}
	}
}

