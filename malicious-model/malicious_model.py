from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch
import torch.nn.functional as F

# 将模型和Tokenizer的加载移到函数外部，以避免每次调用都重新加载
model_path = 'malicious/'
model = DistilBertForSequenceClassification.from_pretrained(model_path)
tokenizer = DistilBertTokenizer.from_pretrained(model_path)

def predict(text_to_predict, model, tokenizer):
    # 使用tokenizer准备模型的输入数据
    inputs = tokenizer(text_to_predict, return_tensors="pt", padding=True, truncation=True, max_length=512)

    # 利用模型进行预测
    model.eval()  # 将模型设置为评估模式
    with torch.no_grad():  # 禁用梯度计算
        outputs = model(**inputs)

    # 提取logits（预测得分）
    logits = outputs.logits

    # 计算概率值
    probabilities = F.softmax(logits, dim=-1).squeeze()
    predicted_class_idx = probabilities.argmax().item()
    if probabilities.numel() > predicted_class_idx:
        # 获取概率值最高的类别索引
        predicted_class_idx = probabilities.argmax().item()
        # 获取预测概率中最大值的概率
        max_probability = probabilities[predicted_class_idx].item()
    else:
        raise IndexError(
            f"Predicted class index {predicted_class_idx} is out of bounds with size {probabilities.numel()}.")

    return predicted_class_idx, max_probability
