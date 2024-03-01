package mypackage

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"os"
	"strings"

	_ "github.com/go-sql-driver/mysql"
)

type LogData struct {
	LogContent string `json:"logContent"`
	Level      string `json:"level"`
	Time       string `json:"time"`
}
type LogOut struct {
	LogContent string `json:"logContent"`
	Time       string `json:"time"`
}

var db *sql.DB

func init() {
	var err error

	// 打开数据库连接
	db, err = sql.Open("mysql", "uu2fu3o:uu2fu3o@tcp(mysql:3306)/k8s")
	if err != nil {
		fmt.Printf("错误打开MySQL数据库: %v\n", err)
		os.Exit(1) // 如果连接失败，退出程序
	}

	// 删除 Logs 表（如果存在）
	_, err = db.Exec("DROP TABLE IF EXISTS Logs")
	if err != nil {
		fmt.Printf("删除日志表时出错: %v\n", err)
		os.Exit(1) // 如果删除失败，退出程序
	}
	fmt.Println("删除成功")

	// 创建一个新的 Logs 表
	_, err = db.Exec("CREATE TABLE Logs (LogContent TEXT, Level VARCHAR(20), Time TEXT)")
	if err != nil {
		fmt.Printf("创建日志表时出错: %v\n", err)
		os.Exit(1) // 如果创建失败，退出程序
	}
}
func ProcessLogFile(filePath string) error {
	content, err := os.ReadFile(filePath)
	if err != nil {
		fmt.Printf("读取文件错误: %v\n", err)
		return err
	}

	// 准备JSON内容，假设每个JSON对象由'}{'分隔
	jsonContent := "[" + strings.ReplaceAll(string(content), "}\n{", "},{") + "]"

	var logs []LogData
	err = json.Unmarshal([]byte(jsonContent), &logs)
	if err != nil {
		fmt.Printf("解码日志错误: %v\n", err)
		return err
	}

	defer db.Close()

	stmt, err := db.Prepare("CREATE TABLE IF NOT EXISTS Logs (LogContent TEXT, Level VARCHAR(20), Time TEXT)")
	if err != nil {
		fmt.Printf("Error preparing statement for table creation: %v", err)
		return err
	}
	_, err = stmt.Exec()
	if err != nil {
		fmt.Printf("Error executing statement for table creation: %v", err)
		return err
	}

	tx, err := db.Begin()
	if err != nil {
		fmt.Printf("Error starting transaction: %v", err)
		return err
	}

	stmt, err = db.Prepare("INSERT INTO Logs(LogContent, Level, Time) values(?, ?, ?)")
	if err != nil {
		fmt.Printf("Error preparing insert statement: %v", err)
		return err
	}

	for _, logData := range logs {
		_, err = stmt.Exec(logData.LogContent, logData.Level, logData.Time)
		if err != nil {
			rbErr := tx.Rollback()
			if rbErr != nil {
				fmt.Printf("Error inserting into table: %v, failed to roll back transaction:%v", err, rbErr)
				return fmt.Errorf("failed to insert into table: %v, failed to roll back: %v", err, rbErr)
			}

			fmt.Printf("Error inserting data into table: %v", err)
			return err
		}
	}

	err = tx.Commit()
	if err != nil {
		fmt.Printf("Error committing transaction: %v", err)
		return err
	}

	fmt.Printf("Data has been successfully imported.")
	return nil
}
