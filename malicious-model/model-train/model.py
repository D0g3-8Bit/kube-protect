from transformers import DistilBertForSequenceClassification, DistilBertTokenizer
from transformers import Trainer, TrainingArguments
import torch
import pandas as pd
from datasets import Dataset, DatasetDict

# 1. 加载预训练的tokenizer和模型
tokenizer = DistilBertTokenizer.from_pretrained('./distilbert-base-uncased')
# 具体的类别数（num_labels）需要根据实际情况来设置
model = DistilBertForSequenceClassification.from_pretrained('./distilbert-base-uncased', num_labels=3)

# 数据标签映射
label_to_id = {'ssh': 0, 'docker': 1, 'reverseshell': 2}

# 2. 读取Excel文件，并将标签字符串转化为数字
excel_path = './try.xlsx'  # 实际的Excel文件路径
df = pd.read_excel(excel_path, sheet_name='test')  # 实际的Excel文件的sheet名称
df['labels'] = df['label'].map(label_to_id)  # 'labels' 是训练时预期的字段名

# 3. 数据预处理
def encode(examples):
    return tokenizer(examples['text'], truncation=True, padding='max_length', max_length=256)

# 使用 Dataset.from_pandas 创建数据集
dataset = Dataset.from_pandas(df)

# 将数据集分割为训练和测试集。注意：如果您的Excel已经有预分割的数据则跳过这步。
train_test_split = dataset.train_test_split(test_size=0.2)
datasets = DatasetDict({
    'train': train_test_split['train'],
    'test': train_test_split['test']
})

# 使用 map 方法应用 encode 函数
encoded_datasets = datasets.map(encode, batched=True)

# 4. 将数据集转化为torch.Dataset
class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, dataset):
        self.dataset = dataset

    def __getitem__(self, idx):
        # 从编码的数据集中提取特定索引的项目，但只提取数值类型的特征
        item = {key: torch.tensor(self.dataset[idx][key]) for key in self.dataset.features if key != 'labels' and not isinstance(self.dataset[idx][key], str)}
        item['labels'] = torch.tensor(self.dataset[idx]['labels'], dtype=torch.long)  # 确保标签是长整型张量
        return item

    def __len__(self):
        return len(self.dataset)

# 使用数据集对象初始化 CustomDataset
train_dataset = CustomDataset(encoded_datasets['train'])

# 5. 设置训练参数
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=16,
    evaluation_strategy='steps',
    save_steps=10_000,
    eval_steps=5_000,
    warmup_steps=1_000,
    weight_decay=0.01,
    logging_dir='./logs'
)

# 6. 初始化Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset
)

# 7. 开始训练
trainer.train()
model.save_pretrained('./malicious/')
tokenizer.save_pretrained('./malicious/')