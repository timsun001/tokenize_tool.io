import re
import jieba
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import chardet
from chardet.universaldetector import UniversalDetector


def preprocess_text(text):
    # 去除标点符号、空格、数字、英文字母
    text = re.sub(r'[^\u4e00-\u9fa5]', '', text)
    # 限制字符长度为15
    text = text[:20]
    return text


# 定义分词函数
def tokenize(text):
    words = jieba.lcut(text)
    return words


def process_data(raw_data_file, user_dict_file):
    # 加载自定义分词字典
    jieba.load_userdict(user_dict_file)

    # 读取原始数据文件
    data = pd.read_csv(raw_data_file, encoding='utf-8')

    result_set = []
    items = data[['商品名称', '商品链接', '商品销量']][:2000]
    # 数据预处理：去除标点符号、空格、数字、英文字母，并限制字符长度
    items['商品简称'] = items['商品名称'].apply(lambda x: preprocess_text(x))

    # 分词并聚合数据
    word_counts = {}
    word_sales = {}

    for index, row in items.iterrows():
        product_name = row['商品简称']
        sales = row['商品销量']
        words = tokenize(product_name)

        for word in words:
            if word in word_counts:
                word_counts[word] += 1
                word_sales[word] += sales
            else:
                word_counts[word] = 1
                word_sales[word] = sales

    # 构建结果表
    result = pd.DataFrame({'词': list(word_counts.keys()),
                           '出现次数': list(word_counts.values()),
                           '商品销量': list(word_sales.values())})
    result['平均销量'] = result['商品销量'] / result['出现次数']
    result_set.append(result)

    result = pd.concat(result_set)

    return result


def select_raw_data_file():
    global raw_data_file
    raw_data_file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if raw_data_file:
        # 检测文件编码
        detector = UniversalDetector()
        with open(raw_data_file, 'rb') as f:
            for line in f:
                detector.feed(line)
                if detector.done:
                    break
            detector.close()
            encoding = detector.result['encoding']
        # 读取文件并显示文件路径
        with open(raw_data_file, 'r', encoding=encoding, errors='replace') as f:
            raw_data_content = f.read()
        entry_raw_data.delete(0, tk.END)
        entry_raw_data.insert(tk.END, raw_data_file + " (编码：" + encoding + ")")


def select_user_dict_file():
    user_dict_file = filedialog.askopenfilename(filetypes=[('Text Files', '*.txt')])
    entry_user_dict.delete(0, tk.END)
    entry_user_dict.insert(0, user_dict_file)


def select_result_file():
    result_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[('CSV Files', '*.csv')])
    entry_result_file.delete(0, tk.END)
    entry_result_file.insert(0, result_file)


def tokenize_data():
    raw_data_file = entry_raw_data.get()
    user_dict_file = entry_user_dict.get()
    result_file = entry_result_file.get()

    if raw_data_file != "" and user_dict_file != "" and result_file != "":
        try:
            result = process_data(raw_data_file, user_dict_file)
            result.to_csv(result_file, encoding="utf-8-sig", index=False)
            messagebox.showinfo("分词结果", "分词完成并保存到文件：" + result_file)
        except Exception as e:
            messagebox.showerror("错误", "发生错误：" + str(e))
    else:
        messagebox.showwarning("警告", "请选择原始数据文件、自定义分词文件和结果文件的位置。")


# 创建主窗口
window = tk.Tk()
window.title("分词工具")

# 创建文件选择框和按钮
label_raw_data = tk.Label(window, text="原始数据文件：")
label_raw_data.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
entry_raw_data = tk.Entry(window, width=50)
entry_raw_data.grid(row=0, column=1, padx=10, pady=5)
button_select_raw_data = tk.Button(window, text="选择文件", command=select_raw_data_file)
button_select_raw_data.grid(row=0, column=2, padx=10, pady=5)

label_user_dict = tk.Label(window, text="自定义分词文件：")
label_user_dict.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
entry_user_dict = tk.Entry(window, width=50)
entry_user_dict.grid(row=1, column=1, padx=10, pady=5)
button_select_user_dict = tk.Button(window, text="选择文件", command=select_user_dict_file)
button_select_user_dict.grid(row=1, column=2, padx=10, pady=5)

label_result_file = tk.Label(window, text="结果文件：")
label_result_file.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
entry_result_file = tk.Entry(window, width=50)
entry_result_file.grid(row=2, column=1, padx=10, pady=5)
button_select_result_file = tk.Button(window, text="选择文件", command=select_result_file)
button_select_result_file.grid(row=2, column=2, padx=10, pady=5)

button_tokenize = tk.Button(window, text="分词", command=tokenize_data)
button_tokenize.grid(row=3, column=1, padx=10, pady=10)

window.mainloop()
