package mypackage

// log_filter.go

import (
	"regexp"
)

// 定义敏感日志的正则表达式规则
var maliciousPatterns = []*regexp.Regexp{
	regexp.MustCompile(`(?i)sql injection`),
	regexp.MustCompile(`(?i)cross-site scripting`),
	regexp.MustCompile(`(?i)malware`),
	regexp.MustCompile(`(?i)error`),
	regexp.MustCompile(`(?i)privilege`),
	regexp.MustCompile(`(?i)root`),
	regexp.MustCompile(`(?i)mount`),
	regexp.MustCompile(`(?i)delete`),
	regexp.MustCompile(`(?i)update`),
	regexp.MustCompile(`(?i)change`),
	regexp.MustCompile(`(?i)create`),
	regexp.MustCompile(`(?i)secret`),
	regexp.MustCompile(`(?i)ssh`),
	regexp.MustCompile(`(?i)login`),
	regexp.MustCompile(`(?i)sudo`),
}

// IsMaliciousLog 检查一个日志条目是否匹配恶意日志规则
func IsMaliciousLog(log string) int {
	for _, pattern := range maliciousPatterns {
		if pattern.MatchString(log) {
			return 1
		}
	}
	return 0
}
