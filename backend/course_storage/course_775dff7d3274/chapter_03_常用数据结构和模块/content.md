<think>
The user wants a markdown content for a chapter "常用数据结构和模块". The template is compact. They require: only markdown, no extra explanation. Must contain: chapter introduction (章节导学), sub-section content, examples or case studies, exercises, and chapter summary. Language: Chinese, concise, teaching-friendly.

We need to create sections:

- 章节导学 (overview)
- 小节1: 列表、元组与字典
- 小节2: 集合与文件操作
- 小节3: 常用标准模块简介

Each sub-section should include some explanation, examples, and at least one exercise or quick practice.

We also need to have overall summary at end.

Given the template "compact", the content should be concise but still thorough.

We need to output only markdown; no extra text. So final answer should be a markdown file (or snippet) containing these sections.

We can include code blocks for Python examples.

The chapter intro: brief description, learning objectives.

We'll also need to add "练习题" maybe after each sub-section or a combined section. The instruction: "至少包含：章节导学、小节内容、示例或案例、练习题、本章总结". So we must include those elements. We can have a "练习题" at the end (maybe separate section) or each sub-section can have small practice.

Probably better to have a dedicated "练习题" after each sub-section with a couple of questions.

We'll follow:

# 章节导学

## 小节 1: 列表、元组与字典

- Content...
- 示例...
- 练习题 (maybe 1-2)

## 小节 2: 集合与文件操作

- Content...
- 示例...
- 练习题

## 小节 3: 常用标准模块简介

- Content...
- 示例...
- 练习题

Then a "本章总结" (Chapter summary) and maybe a "完整练习题" section.

Because we need to keep it compact but thorough.

We'll incorporate code fences with Python.

Now let's craft content.

---

# 章节导学

Brief overview of data structures and modules.

Learning objectives: list, tuple, dict, set, file I/O, standard modules.

We'll include bullet points.

---

## 1. 列表、元组与字典

- 列表: mutable sequence, creation, indexing, slicing, methods (append, pop, sort, etc.)
- 元组: immutable, creation, indexing, why use tuples.
- 字典: key-value mapping, creation, access, methods (get, keys, values, items), iteration.

Examples:

```python
# 列表
fruits = ["apple", "banana", "cherry"]
fruits.append("date")
print(fruits[1:3])   # ['banana', 'cherry']
fruits.sort()
print(fruits)

# 元组
point = (3, 4)
x, y = point
print(x, y)

# 字典
scores = {"Alice": 90, "Bob": 85}
scores["Carol"] = 92
print(scores.get("Alice"))
print(scores.items())
```

练习题:

1. 将列表 `[1, 2, 3, 4, 5]` 中所有奇数乘以 2，得到新列表。
2. 创建一个字典 `info`，包含姓名、年龄、职业三个键，并遍历打印键值对。

---

## 2. 集合与文件操作

- 集合: mutable, unordered, unique elements, creation, add, remove, set operations (union, intersection, difference).
- 文件操作: `open`, modes `r`, `w`, `a`, reading lines with `readline`, `readlines`, writing with `write`, using `with` statement to auto-close.

示例:

```python
# 集合
a = {1, 2, 3}
b = {3, 4, 5}
print(a | b)   # union
print(a & b)   # intersection
print(a - b)   # difference

# 文件写入
with open("demo.txt", "w", encoding="utf-8") as f:
    f.write("第一行\n")
    f.write("第二行\n")

# 文件读取
with open("demo.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())
```

练习题:

1. 合并两个集合 `{1,2,3}` 与 `{2,3,4}`，求并集、交集、差集。
2. 将字符串 `"Hello\nPython"` 写入 `hello.txt`，再读取并打印全部内容。

---

## 3. 常用标准模块简介

- `os`: 路径操作 (`os.path.join`, `os.getcwd`, `os.listdir`), 文件系统交互.
- `random`: 随机数生成 (`random.random`, `random.randint`, `random.choice`, `random.shuffle`).
- `json`: JSON 序列化与反序列化 (`json.dumps`, `json.loads`).
- 导入方式: `import module` 或 `from module import func`.

示例:

```python
import os
import random
import json

# os 示例
cwd = os.getcwd()
files = os.listdir(cwd)
print("当前目录文件:", files)

# random 示例
print(random.randint(1, 10))
cards = ["A", "K", "Q", "J"]
random.shuffle(cards)
print("洗牌后:", cards)

# json 示例
data = {"name": "Alice", "score": 98}
json_str = json.dumps(data, ensure_ascii=False)
print("JSON 字符串:", json_str)
parsed = json.loads(json_str)
print("解析后:", parsed)
```

练习题:

1. 使用 `os.path.join` 构造路径 `"folder/subfolder/file.txt"`。
2. 用 `random.sample` 从列表 `[1,2,3,4,5]` 中随机抽取 3 个不重复的元素。
3. 将字典 `{"city":"Beijing","population":2154}` 序列化为 JSON 字符串并打印。

---

## 本章总结

- 列表、元组、字典是最常用的内建容器，各有特点：列表可变、支持多种操作；元组不可变、适合作为固定数据；字典提供键值映射，查找速度快。
- 集合提供唯一性保证和丰富的集合运算，适合去重和逻辑运算。
- 文件 I/O 通过 `open`/`with` 实现，要养成关闭文件的好习惯。
- 标准库模块 (`os`, `random`, `json`) 扩展了 Python 功能，导入方式灵活，可直接使用函数或别名。
- 多练习、多写代码，是掌握这些概念的最佳途径。

---

## 综合练习

1. 编写函数 `process_scores(scores_dict)`，返回平均分、最高分、最低分。  
2. 将 1‑100 中所有 3 或 5 的倍数存入集合 `multiples`，并打印个数。  
3. 实现一个简易的“日志写入器”，使用 `with open` 把当前时间戳写入 `log.txt`，每次运行追加一行。  

--- 

We need to ensure we adhere to the "compact" template: the content is relatively concise, not overly verbose, bullet points, code snippets, and exercises.

The answer should be in markdown. We'll produce as final answer.
</think>

# 章节导学

本章节将介绍 Python 中最常用的内置数据结构——**列表、元组、字典、集合**，以及 **文件操作** 与 **常用标准模块**（`os`、`random`、`json`）。掌握这些内容后，你能够在实际项目中高效地组织、存储和处理数据，并利用标准库快速完成常见任务。

**学习目标**  
- 熟练创建、索引、切片列表；了解元组的不可变特性及字典的键值操作。  
- 熟悉集合的创建、交/并/差运算，能够读写文本文件。  
- 学会导入并使用 `os`、`random`、`json` 模块的基本功能。  

---

## 1. 列表、元组与字典

### 列表（list）
- **创建**：`[1, 2, 3]`、`list(range(4))`  
- **索引/切片**：`lst[0]`、`lst[-1]`、`lst[1:3]`  
- **常用方法**：`append`、`pop`、`insert`、`remove`、`sort`、`reverse`  

```python
fruits = ["apple", "banana", "cherry"]
fruits.append("date")
print(fruits[1:3])   # ['banana', 'cherry']
fruits.sort()
print(fruits)       # ['apple', 'banana', 'cherry', 'date']
```

### 元组（tuple）
- **创建**：`(1, 2, 3)`、`tuple([1, 2, 3])`  
- **不可变**：适用于固定数据、函数多返回值。  
- **可拆包**：`x, y = (3, 4)`

```python
point = (3, 4)
x, y = point
print(x, y)   # 3 4
```

### 字典（dict）
- **创建**：`{"Alice": 90, "Bob": 85}`、`dict([("a",1), ("b",2)])`  
- **访问**：`d["key"]`、`d.get("key", default)`  
- **常用方法**：`keys()`、`values()`、`items()`、`update`、`pop`

```python
scores = {"Alice": 90, "Bob": 85}
scores["Carol"] = 92
print(scores.get("Alice"))      # 90
print(scores.items())          # dict_items([('Alice', 90), ('Bob', 85), ('Carol', 92)])
```

### 练习题
1. 将列表 `[1, 2, 3, 4, 5]` 中所有奇数乘以 2，得到新列表。  
2. 创建一个字典 `info`，包含 `name`、`age`、`job` 三个键，并遍历打印键值对。  

---

## 2. 集合与文件操作

### 集合（set）
- **创建**：`{1, 2, 3}`、`set([1, 2, 2, 3])`（自动去重）  
- **常用方法**：`add`、`remove`、`discard`、`pop`  
- **集合运算**：`|`（并集）、`&`（交集）、`-`（差集）、`^`（对称差）

```python
a = {1, 2, 3}
b = {3, 4, 5}
print(a | b)   # {1, 2, 3, 4, 5}
print(a & b)   # {3}
print(a - b)   # {1, 2}
```

### 文件操作
- **打开**：`f = open("path", mode, encoding="utf-8")`  
- **模式**：`r`（读）、`w`（写，覆盖）、`a`（追加）  
- **自动关闭**：使用 `with` 语句  

```python
# 写入
with open("demo.txt", "w", encoding="utf-8") as f:
    f.write("第一行\n")
    f.write("第二行\n")

# 读取
with open("demo.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())
```

### 练习题
1. 合并集合 `{1,2,3}` 与 `{2,3,4}`，求并集、交集、差集。  
2. 将字符串 `"Hello\nPython"` 写入 `hello.txt`，再读取并打印全部内容。  

---

## 3. 常用标准模块简介

### `os` – 操作系统接口
```python
import os

cwd = os.getcwd()
print("当前工作目录:", cwd)
files = os.listdir(cwd)
print("目录内容:", files)
path = os.path.join("folder", "subfolder", "file.txt")
print("拼接路径:", path)
```

### `random` – 随机数生成
```python
import random

print(random.randint(1, 10))           # 随机整数
print(random.random())                 # [0,1) 浮点数
cards = ["A", "K", "Q", "J"]
random.shuffle(cards)                  # 原地洗牌
print("洗牌后:", cards)
print(random.sample([1,2,3,4,5], 3))   # 不放回抽样
```

### `json` – JSON 序列化
```python
import json

data = {"city": "Beijing", "population": 2154}
json_str = json.dumps(data, ensure_ascii=False)  # 序列化
print("JSON:", json_str)

parsed = json.loads(json_str)                    # 反序列化
print("解析后:", parsed)
```

### 练习题
1. 用 `os.path.join` 构造路径 `"folder/subfolder/file.txt"`。  
2. 使用 `random.sample` 从列表 `[1,2,3,4,5]` 中随机抽取 3 个不重复的元素。  
3. 将字典 `{"city":"Shanghai","pop":2428}` 序列化为 JSON 字符串并打印。  

---

## 本章总结

- **列表、元组、字典**是最常用的容器。列表可变、支持丰富操作；元组不可变、适合作为固定数据；字典提供键值映射，查找速度快。  
- **集合**保证元素唯一，适合去重和集合运算（交、并、差）。  
- **文件 I/O** 通过 `open`/`with` 实现，要养成使用 `with` 自动关闭文件的习惯。  
- **标准库模块**（`os`、`random`、`json`）扩展了 Python 功能，导入方式灵活，可直接调用函数。  
- 多动手编写代码，才能熟练掌握这些基础概念与技巧。

---

## 综合练习

1. 编写函数 `process_scores(scores_dict)`，返回平均分、最高分、最低分。  
2. 将 1‑100 中所有 3 或 5 的倍数存入集合 `multiples`，并打印集合大小。  
3. 实现一个简易 “日志写入器”，使用 `with open` 把当前时间戳追加写入 `log.txt`，每次运行追加一行。  

---
