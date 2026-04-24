<think>The user wants me to generate Markdown content for a chapter titled "控制结构与函数" (Control Structures and Functions) in a Python beginner course. Let me follow the requirements:

1. Only output Markdown content, no explanations
2. Must include: chapter introduction, section content, examples/cases, exercises, chapter summary
3. Language should be concise, teaching-friendly, in Chinese
4. Template: compact

I need to structure this with:
- 章节导学 (Chapter Introduction)
- 条件判断 section with subsections
- 循环结构 section with subsections
- 函数定义与调用 section with subsections
- 练习题
- 本章总结

Let me write this in a compact but comprehensive way.

The structure should be:
1. 章节导学
2. 第一节: 条件判断 (if, elif, else, nested)
3. 第二节: 循环结构 (for, while, break, continue)
4. 第三节: 函数定义与调用 (concepts, parameters, return values, default arguments)
5. 练习题
6. 本章总结

I'll use Markdown formatting with headers, code blocks, lists, etc.</think>

# 控制结构与函数

## 章节导学

本章将学习Python中三种核心编程概念：

- **条件判断**：让程序根据不同情况做出不同反应
- **循环结构**：让程序自动重复执行任务
- **函数**：将代码块封装成可重复使用的独立模块

掌握这三项技能后，你将能够编写结构清晰、功能完整的Python程序。

---

## 第一节 条件判断

### 1.1 基本 if 语句

```python
age = 18
if age >= 18:
    print("已成年，可以考驾照")
```

### 1.2 if-else 结构

```python
score = 72
if score >= 60:
    print("及格")
else:
    print("不及格")
```

### 1.3 if-elif-else 多分支

```python
grade = 85
if grade >= 90:
    print("优秀")
elif grade >= 80:
    print("良好")
elif grade >= 60:
    print("及格")
else:
    print("不及格")
```

### 1.4 嵌套条件

```python
age = 20
has_ticket = True

if age >= 18:
    if has_ticket:
        print("允许入场")
    else:
        print("需要购票")
else:
    print("未满18岁，禁止入场")
```

> **提示**：多层嵌套时注意代码缩进，Python 以缩进区分代码块。

---

## 第二节 循环结构

### 2.1 for 循环

遍历字符串：
```python
for char in "Python":
    print(char)
```

遍历数字序列：
```python
for i in range(1, 6):
    print(f"第 {i} 次循环")
```

### 2.2 while 循环

```python
count = 0
while count < 5:
    print(count)
    count += 1
```

### 2.3 break 与 continue

```python
for i in range(10):
    if i == 5:
        break       # 终止循环
    print(i)

for i in range(5):
    if i == 2:
        continue    # 跳过本次循环
    print(i)
```

### 2.4 循环的 else 子句

循环正常结束时执行 else（未使用 break 时）：
```python
for n in range(2, 10):
    for x in range(2, n):
        if n % x == 0:
            print(f"{n} 不是质数")
            break
    else:
        print(f"{n} 是质数")
```

---

## 第三节 函数定义与调用

### 3.1 定义简单函数

无参函数：
```python
def greet():
    print("你好，欢迎学习Python！")

greet()
```

### 3.2 带参数的函数

```python
def greet_user(name):
    print(f"你好，{name}！")

greet_user("小明")
```

### 3.3 默认参数

```python
def greet(name, msg="祝你学习愉快"):
    print(f"{name}，{msg}")

greet("小红")
greet("小李", "加油！")
```

### 3.4 返回值

```python
def add(a, b):
    return a + b

result = add(3, 5)
print(result)  # 输出: 8
```

### 3.5 完整示例：计算器函数

```python
def calculator(a, b, operator="+"):
    if operator == "+":
        return a + b
    elif operator == "-":
        return a - b
    elif operator == "*":
        return a * b
    elif operator == "/":
        if b != 0:
            return a / b
        return "除数不能为零"
    else:
        return "无效运算符"

print(calculator(10, 5))        # 加法: 15
print(calculator(10, 5, "-"))  # 减法: 5
```

---

## 练习题

### 一、选择题

1. 下列哪个关键字用于多条件分支判断？
   - A. case
   - B. switch
   - C. elif
   - D. when

2. `for i in range(1, 10, 2)` 循环会输出哪些数字？

3. 以下代码的输出结果是什么？
   ```python
   def test(x):
       if x > 0:
           return "正数"
       else:
           return "非正数"
   print(test(-5))
   ```

### 二、编程题

1. 编写程序，输入一个分数，输出对应的等级（A/B/C/D/F）。

2. 使用循环打印九九乘法表。

3. 定义一个函数，计算给定列表的平均值。

### 三、改错题

找出以下代码的错误：
```python
def multiply(a, b=2, c)
    return a * b * c

print(multiply(3))
```

---

## 本章总结

| 概念 | 关键词 | 要点 |
|------|--------|------|
| 条件判断 | `if` `elif` `else` | 根据条件选择执行不同代码块 |
| 循环 | `for` `while` | 重复执行代码，配合 `break`/`continue` 控制流程 |
| 函数 | `def` `return` | 封装代码，支持参数传递与默认值 |

**核心要点回顾**：

- 条件语句需注意逻辑顺序，elif 需在 else 前
- `range()` 生成数字序列，`range(n)` 从 0 到 n-1
- 函数提升代码复用性，默认参数必须放在参数列表末尾
- 善用 `return` 获取函数结果，无 return 则返回 `None`

下一章将介绍 Python 中的数据结构（列表、元组、字典），进一步增强数据管理能力。
