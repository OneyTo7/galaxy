"""课程章节讲义种子脚本。

为已存在的三套课程（Python/Java/C）创建 Markdown 章节内容，
每章关联对应作业，学生可"先看课本再做题"。

用法：
    cd backend && source .venv/bin/activate
    MOCK=1 python scripts/seed_lessons.py            # 幂等
    MOCK=1 python scripts/seed_lessons.py --reset     # 清空章节后重建
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.contexts.assignment.models import Assignment
from app.contexts.lesson.models import Lesson
from app.contexts.organization.models import Course
from app.core.database import SessionLocal

# ── Python 课程章节（12 章）──────────────────────────────
# 每章：(title, content_markdown, assignment_title_or_None)
# assignment_title 用于关联已有作业（按标题查找）

PYTHON_LESSONS = [
    ("第 1 章：Python 环境与第一个程序", """# 第 1 章：Python 环境与第一个程序

## 1.1 Python 简介

Python 是一门解释型、高级编程语言，语法简洁清晰，适合初学者入门。

## 1.2 输出与输入

### 输出：`print()`
```python
print("Hello, World!")
print(1 + 2)  # 输出 3
```

### 输入：`input()`
```python
name = input("请输入姓名：")
print("你好，" + name)
```

`input()` 返回字符串，需要 `int()` 或 `float()` 转换为数字。

## 1.3 变量与类型

Python 是动态类型语言，变量无需声明类型：
```python
x = 10          # int
y = 3.14        # float
s = "hello"     # str
b = True        # bool
```

## 1.4 类型转换

```python
s = "42"
n = int(s)      # 字符串 → 整数
s2 = str(n)     # 整数 → 字符串
```

## 要点
- `input()` 永远返回字符串，做数学运算前必须转换
- `int()` 可以解析 "42"，但不能解析 "3.14"（会报 ValueError）
- `print()` 自动换行
""", "两数之和"),

    ("第 2 章：条件判断", """# 第 2 章：条件判断

## 2.1 if-elif-else

```python
score = int(input())
if score >= 90:
    print("A")
elif score >= 80:
    print("B")
elif score >= 60:
    print("C")
else:
    print("D")
```

## 2.2 比较运算符

`==` `!=` `>` `<` `>=` `<=`

## 2.3 逻辑运算符

- `and`：两个条件都为 True
- `or`：任一条件为 True
- `not`：取反

```python
if n > 0 and n < 100:
    print("有效范围")
```

## 2.4 奇偶判断

```python
n = int(input())
if n % 2 == 0:
    print("even")
else:
    print("odd")
```

## 要点
- Python 用缩进（4 空格）表示代码块，不用大括号
- `elif` 不是 `else if`
- `==` 是比较，`=` 是赋值，不要混
""", "判断奇偶"),

    ("第 3 章：循环基础", """# 第 3 章：循环基础

## 3.1 for 循环

```python
for i in range(5):      # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 6):  # 1, 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2):  # 0, 2, 4, 6, 8
    print(i)
```

## 3.2 while 循环

```python
n = int(input())
while n > 0:
    print(n)
    n -= 1
```

## 3.3 break 与 continue

- `break`：立即跳出循环
- `continue`：跳过本次，进入下一次

```python
for i in range(10):
    if i == 5:
        break
    if i % 2 == 0:
        continue
    print(i)  # 输出 1, 3
```

## 要点
- `range(n)` 生成 0 到 n-1，不包含 n
- `range(a, b)` 生成 a 到 b-1
- 循环变量在循环结束后仍然存在
""", "数组求和"),

    ("第 4 章：列表（数组）", """# 第 4 章：列表（数组）

## 4.1 创建与访问

```python
arr = [1, 2, 3, 4, 5]
print(arr[0])    # 1
print(arr[-1])   # 5（倒数第一个）
print(len(arr))  # 5
```

## 4.2 从输入创建列表

```python
n = int(input())
arr = list(map(int, input().split()))
```

## 4.3 遍历

```python
for x in arr:
    print(x)

for i in range(len(arr)):
    print(arr[i])
```

## 4.4 常用操作

```python
arr.append(6)      # 尾部添加
arr.sort()          # 排序
arr.reverse()       # 反转
max(arr)            # 最大值
min(arr)            # 最小值
sum(arr)            # 求和
```

## 要点
- 索引从 0 开始，到 len(arr)-1 结束
- 负索引从尾部倒数（-1 是最后一个）
- 越界访问会报 IndexError
""", "数组最大值"),

    ("第 5 章：字符串基础", """# 第 5 章：字符串基础

## 5.1 字符串操作

```python
s = "hello"
print(len(s))      # 5
print(s[0])        # h
print(s[-1])       # o
```

## 5.2 切片

```python
s = "hello world"
print(s[0:5])     # hello
print(s[6:])      # world
print(s[::-1])    # dlrow olleh（反转）
```

## 5.3 拼接与分割

```python
s = "a" + "b"           # ab
parts = "1 2 3".split()  # ['1', '2', '3']
joined = "-".join(["a", "b", "c"])  # a-b-c
```

## 5.4 常用方法

```python
s.upper()       # 大写
s.lower()       # 小写
s.strip()       # 去首尾空白
s.replace("a", "b")  # 替换
```

## 要点
- 字符串不可变，操作返回新字符串
- 切片 `[start:end]` 包含 start 不包含 end
- `[::-1]` 是反转字符串的惯用法
""", "字符串反转"),

    ("第 6 章：函数", """# 第 6 章：函数

## 6.1 定义与调用

```python
def greet(name):
    return "Hello, " + name

print(greet("Alice"))  # Hello, Alice
```

## 6.2 参数与返回值

```python
def add(a, b):
    return a + b

def max_of_three(a, b, c):
    if a >= b and a >= c:
        return a
    elif b >= c:
        return b
    else:
        return c
```

## 6.3 默认参数

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}"

print(greet("Alice"))           # Hello, Alice
print(greet("Bob", "Hi"))      # Hi, Bob
```

## 要点
- 函数用 `def` 定义
- `return` 返回值，无 return 返回 None
- 参数按位置传递
""", None),

    ("第 7 章：多重循环", """# 第 7 章：多重循环

## 7.1 嵌套 for

```python
for i in range(3):
    for j in range(3):
        print(f"({i}, {j})")
```

## 7.2 打印图案

```python
# 直角三角形
for i in range(1, 6):
    print("*" * i)
```

## 7.3 冒泡排序

```python
arr = [3, 1, 4, 1, 5]
for i in range(len(arr)):
    for j in range(len(arr) - i - 1):
        if arr[j] > arr[j + 1]:
            arr[j], arr[j + 1] = arr[j + 1], arr[j]
print(arr)  # [1, 1, 3, 4, 5]
```

## 要点
- 内层循环完整执行一轮，外层才前进一步
- 冒泡排序内层范围 `n - i - 1`（每轮少比一个）
- 交换用 `a, b = b, a`，不需要临时变量
""", "冒泡排序"),

    ("第 8 章：递归", """# 第 8 章：递归

## 8.1 基本概念

递归是函数调用自身。必须有两个部分：
1. **递归出口**（base case）：停止条件
2. **递归步骤**：向出口靠近

## 8.2 阶乘

```python
def factorial(n):
    if n <= 1:       # 递归出口
        return 1
    return n * factorial(n - 1)  # 递归步骤
```

## 8.3 斐波那契

```python
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
```

## 要点
- 必须有递归出口，否则栈溢出
- 每次递归调用问题规模必须缩小
- 阶乘的出口是 n <= 1（0! = 1! = 1）
""", "计算阶乘"),

    ("第 9 章：字典与集合", """# 第 9 章：字典与集合

## 9.1 字典 dict

```python
d = {"name": "Alice", "age": 20}
print(d["name"])     # Alice
d["grade"] = "A"     # 添加
del d["age"]         # 删除

for key, value in d.items():
    print(key, value)
```

## 9.2 集合 set

```python
s = {1, 2, 3}
s.add(4)
s.discard(2)    # 删除（不存在不报错）
print(1 in s)   # True
```

## 要点
- 字典键唯一，集合元素唯一
- 字典查找 O(1)
- 集合用于去重和快速判断存在性
""", None),

    ("第 10 章：文件操作", """# 第 10 章：文件操作

## 10.1 读写文件

```python
# 写
with open("output.txt", "w") as f:
    f.write("Hello\\n")

# 读
with open("input.txt", "r") as f:
    content = f.read()
    lines = f.readlines()
```

## 10.2 逐行处理

```python
with open("data.txt") as f:
    for line in f:
        line = line.strip()
        print(line)
```

## 要点
- `with` 自动关闭文件
- `"w"` 覆盖写，`"a"` 追加，`"r"` 只读
- 读出的行带换行符，用 `.strip()` 去掉
""", None),

    ("第 11 章：异常处理", """# 第 11 章：异常处理

## 11.1 try-except

```python
try:
    n = int(input())
    print(10 / n)
except ValueError:
    print("输入不是整数")
except ZeroDivisionError:
    print("除零错误")
```

## 11.2 finally

```python
try:
    f = open("data.txt")
    content = f.read()
finally:
    f.close()  # 无论是否异常都执行
```

## 要点
- 捕获具体异常类型，不要裸 `except`
- `finally` 用于资源清理
- 常见异常：ValueError, TypeError, IndexError, KeyError
""", None),

    ("第 12 章：二维数组与矩阵", """# 第 12 章：二维数组与矩阵

## 12.1 创建二维列表

```python
# m 行 n 列
m, n = 3, 4
mat = [[0] * n for _ in range(m)]

# 从输入读取
m, n = map(int, input().split())
mat = [list(map(int, input().split())) for _ in range(m)]
```

## 12.2 访问与遍历

```python
# 访问 mat[i][j]
print(mat[0][1])

# 遍历
for i in range(m):
    for j in range(n):
        print(mat[i][j], end=" ")
    print()

# 转置
for j in range(n):
    for i in range(m):
        print(mat[i][j], end=" ")
    print()
```

## 要点
- `[[0] * n] * m` 是错的（浅拷贝），必须用列表推导式
- 矩阵转置：外层遍历列，内层遍历行
- 索引 `mat[i][j]`：i 是行，j 是列
""", "矩阵转置"),
]

# ── Java 课程章节（10 章）──────────────────────────────
JAVA_LESSONS = [
    ("第 1 章：Java 入门与基本语法", """# 第 1 章：Java 入门与基本语法

## 1.1 第一个程序

```java
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

## 1.2 输入：Scanner

```java
import java.util.Scanner;
Scanner sc = new Scanner(System.in);
int n = sc.nextInt();
String s = sc.next();
```

## 1.3 变量与类型

```java
int x = 10;
double y = 3.14;
String s = "hello";
boolean b = true;
```

## 要点
- 类名必须与文件名一致（Main）
- `System.out.println()` 自动换行，`print()` 不换行
- `Scanner` 需要 `import java.util.Scanner`
""", "两数之和"),

    ("第 2 章：条件判断", """# 第 2 章：条件判断

## 2.1 if-else if-else

```java
int score = sc.nextInt();
if (score >= 90) System.out.println("A");
else if (score >= 80) System.out.println("B");
else if (score >= 60) System.out.println("C");
else System.out.println("D");
```

## 2.2 三目运算

```java
String result = n % 2 != 0 ? "odd" : "even";
```

## 要点
- Java 用 `else if`，不是 `elif`
- 条件必须是布尔表达式，不能写 `if (n)`（必须是 `if (n != 0)`）
""", "判断奇偶"),

    ("第 3 章：循环", """# 第 3 章：循环

## 3.1 for 循环

```java
for (int i = 0; i < n; i++) {
    System.out.println(i);
}
```

## 3.2 while 循环

```java
while (n > 0) {
    System.out.println(n);
    n--;
}
```

## 3.3 break 与 continue

同 Python，`break` 跳出循环，`continue` 跳过本次。

## 要点
- `for (int i = 0; i < n; i++)` 是最常用写法
- 循环变量通常在 for 内声明
""", "数组求和"),

    ("第 4 章：数组", """# 第 4 章：数组

## 4.1 声明与使用

```java
int[] arr = new int[n];
for (int i = 0; i < n; i++) {
    arr[i] = sc.nextInt();
}
```

## 4.2 遍历

```java
for (int i = 0; i < arr.length; i++) {
    System.out.println(arr[i]);
}
```

## 4.3 常用操作

```java
Arrays.sort(arr);           // 排序
int max = Arrays.stream(arr).max().getAsInt();
int sum = Arrays.stream(arr).sum();
```

## 要点
- 数组长度固定，创建后不可变
- 索引从 0 到 `arr.length - 1`
- 越界访问抛 `ArrayIndexOutOfBoundsException`
""", "数组最大值"),

    ("第 5 章：字符串", """# 第 5 章：字符串

## 5.1 基本操作

```java
String s = "hello";
int len = s.length();       // 5
char c = s.charAt(0);       // h
```

## 5.2 StringBuilder

```java
StringBuilder sb = new StringBuilder("hello");
sb.reverse();               // olleh
String reversed = sb.toString();
```

## 5.3 分割与拼接

```java
String[] parts = "1 2 3".split(" ");
String joined = String.join(" ", parts);
```

## 要点
- String 不可变，操作返回新对象
- 频繁拼接用 StringBuilder
- `s.equals("hello")` 比较内容，`==` 比较引用
""", "字符串反转"),

    ("第 6 章：方法（函数）", """# 第 6 章：方法（函数）

## 6.1 定义方法

```java
public static int add(int a, int b) {
    return a + b;
}
```

## 6.2 调用

```java
int result = add(3, 5);
```

## 要点
- 方法必须在类内定义
- `static` 方法可直接调用，不需要创建对象
- 返回类型必须声明（int, void, String...）
""", None),

    ("第 7 章：嵌套循环", """# 第 7 章：嵌套循环

## 7.1 冒泡排序

```java
for (int i = 0; i < n; i++) {
    for (int j = 0; j < n - i - 1; j++) {
        if (arr[j] > arr[j + 1]) {
            int temp = arr[j];
            arr[j] = arr[j + 1];
            arr[j + 1] = temp;
        }
    }
}
```

## 要点
- 内层循环范围 `n - i - 1`
- 交换需要临时变量
""", "冒泡排序"),

    ("第 8 章：递归", """# 第 8 章：递归

## 8.1 阶乘

```java
public static long factorial(int n) {
    if (n <= 1) return 1;           // 递归出口
    return n * factorial(n - 1);   // 递归步骤
}
```

## 要点
- 必须有递归出口
- Java 栈深度有限，过深递归会 StackOverflowError
- 大数阶乘用 `long` 防溢出
""", "计算阶乘"),

    ("第 9 章：面向对象基础", """# 第 9 章：面向对象基础

## 9.1 类与对象

```java
class Student {
    String name;
    int score;
    
    Student(String name, int score) {
        this.name = name;
        this.score = score;
    }
    
    String getGrade() {
        if (score >= 90) return "A";
        if (score >= 60) return "C";
        return "D";
    }
}

Student s = new Student("Alice", 95);
System.out.println(s.getGrade());  // A
```

## 要点
- 构造方法名与类名相同
- `this` 指向当前对象
- 成员变量和方法通过 `.` 访问
""", None),

    ("第 10 章：集合框架", """# 第 10 章：集合框架

## 10.1 ArrayList

```java
import java.util.ArrayList;
ArrayList<Integer> list = new ArrayList<>();
list.add(1);
list.add(2);
list.get(0);    // 1
list.size();    // 2
```

## 10.2 HashMap

```java
import java.util.HashMap;
HashMap<String, Integer> map = new HashMap<>();
map.put("Alice", 95);
map.get("Alice");  // 95
```

## 要点
- ArrayList 是动态数组，长度可变
- HashMap 是键值对，查找 O(1)
- 泛型指定元素类型
""", None),
]

# ── C 语言课程章节（10 章）──────────────────────────────
C_LESSONS = [
    ("第 1 章：C 语言入门", """# 第 1 章：C 语言入门

## 1.1 第一个程序

```c
#include <stdio.h>
int main() {
    printf("Hello, World!\\n");
    return 0;
}
```

## 1.2 输入输出

```c
int a, b;
scanf("%d %d", &a, &b);
printf("%d\\n", a + b);
```

## 1.3 变量与类型

```c
int x = 10;
double y = 3.14;
char c = 'A';
```

## 要点
- `scanf` 必须传地址（`&a`）
- `printf` 用格式符：`%d` 整数、`%f` 浮点、`%c` 字符、`%s` 字符串
- `main` 返回 0 表示正常结束
""", "两数之和"),

    ("第 2 章：条件判断", """# 第 2 章：条件判断

## 2.1 if-else

```c
if (n >= 90) printf("A\\n");
else if (n >= 80) printf("B\\n");
else if (n >= 60) printf("C\\n");
else printf("D\\n");
```

## 2.2 三目运算

```c
printf("%s\\n", n % 2 ? "odd" : "even");
```

## 要点
- C 的 `if` 和 Python 类似，但用大括号 `{}`
- `0` 为假，非零为真
""", "判断奇偶"),

    ("第 3 章：循环", """# 第 3 章：循环

## 3.1 for 循环

```c
for (int i = 0; i < n; i++) {
    printf("%d ", i);
}
```

## 3.2 while 循环

```c
while (n > 0) {
    printf("%d\\n", n);
    n--;
}
```

## 要点
- `for (init; condition; update)` 三段式
- C99 允许在 for 内声明变量
""", "数组求和"),

    ("第 4 章：数组", """# 第 4 章：数组

## 4.1 声明与使用

```c
int arr[100];
for (int i = 0; i < n; i++) {
    scanf("%d", &arr[i]);
}
```

## 4.2 遍历与求和

```c
int sum = 0;
for (int i = 0; i < n; i++) {
    sum += arr[i];
}
printf("%d\\n", sum);
```

## 要点
- 数组大小必须编译时确定（或用变长数组 VLA）
- 数组名本身是地址，`scanf` 读取到 `arr[i]` 仍需 `&`
- 越界访问是未定义行为，不会报错但可能崩溃
""", "数组最大值"),

    ("第 5 章：字符串", """# 第 5 章：字符串

## 5.1 字符数组

```c
char s[1000];
scanf("%s", s);      // 读到空格为止
int len = strlen(s); // 需 #include <string.h>
```

## 5.2 反转

```c
int n = strlen(s);
for (int i = n - 1; i >= 0; i--) {
    putchar(s[i]);
}
putchar('\\n');
```

## 要点
- C 没有字符串类型，用 `char` 数组 + `\\0` 结尾
- `scanf("%s")` 遇空格停止，读整行用 `fgets`
- `strlen` 需要 `#include <string.h>`
""", "字符串反转"),

    ("第 6 章：函数", """# 第 6 章：函数

## 6.1 定义

```c
int add(int a, int b) {
    return a + b;
}
```

## 6.2 调用

```c
int result = add(3, 5);
printf("%d\\n", result);
```

## 要点
- 函数声明（原型）放在 `main` 前，定义放后面
- 参数按值传递，修改形参不影响实参
- 指针参数可以修改实参
""", None),

    ("第 7 章：嵌套循环", """# 第 7 章：嵌套循环

## 7.1 冒泡排序

```c
for (int i = 0; i < n; i++) {
    for (int j = 0; j < n - i - 1; j++) {
        if (a[j] > a[j + 1]) {
            int t = a[j];
            a[j] = a[j + 1];
            a[j + 1] = t;
        }
    }
}
```

## 要点
- 内层范围 `n - i - 1`
- 交换需要临时变量
""", "冒泡排序"),

    ("第 8 章：递归", """# 第 8 章：递归

## 8.1 阶乘

```c
long long factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
```

## 要点
- 必须有递归出口
- 大数用 `long long` 防溢出
- 格式符 `%lld`
""", "计算阶乘"),

    ("第 9 章：指针", """# 第 9 章：指针

## 9.1 基本概念

```c
int x = 10;
int *p = &x;       // p 存储 x 的地址
printf("%d\\n", *p); // 10（解引用）
```

## 9.2 指针与数组

```c
int arr[5] = {1, 2, 3, 4, 5};
int *p = arr;      // 数组名就是首元素地址
printf("%d\\n", *(p + 2));  // 3
```

## 要点
- `&` 取地址，`*` 解引用
- 数组名是指向首元素的指针
- 指针加减以元素大小为单位
""", None),

    ("第 10 章：结构体", """# 第 10 章：结构体

## 10.1 定义与使用

```c
struct Student {
    char name[50];
    int score;
};

struct Student s = {"Alice", 95};
printf("%s: %d\\n", s.name, s.score);
```

## 10.2 数组结构体

```c
struct Student students[100];
for (int i = 0; i < n; i++) {
    scanf("%s %d", students[i].name, &students[i].score);
}
```

## 要点
- `struct` 把多个变量打包
- 用 `.` 访问成员
- 结构体数组用于管理多条记录
""", None),
]

COURSE_LESSONS = [
    ("PY-101", PYTHON_LESSONS),
    ("JAVA-101", JAVA_LESSONS),
    ("C-101", C_LESSONS),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="清空章节后重建")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.reset:
            db.query(Lesson).delete()
            db.commit()
            print("已清空所有章节（--reset）")

        created = 0
        for course_code, lessons in COURSE_LESSONS:
            course = db.query(Course).filter(Course.code == course_code).first()
            if not course:
                print(f"  跳过：课程 {course_code} 不存在，请先运行 seed_courses.py")
                continue

            for idx, (title, content, assignment_title) in enumerate(lessons):
                # 幂等：按课程 + 标题查重
                existing = db.query(Lesson).filter(
                    Lesson.course_id == course.id,
                    Lesson.title == title,
                ).first()
                if existing:
                    continue

                # 关联作业
                assignment_id = None
                if assignment_title:
                    a = db.query(Assignment).filter(
                        Assignment.course_id == course.id,
                        Assignment.title == assignment_title,
                    ).first()
                    if a:
                        assignment_id = a.id

                lesson = Lesson(
                    course_id=course.id,
                    title=title,
                    content=content,
                    sort_order=idx + 1,
                    assignment_id=assignment_id,
                )
                db.add(lesson)
                db.commit()
                created += 1
                link = f" → 关联作业「{assignment_title}」" if assignment_id else ""
                print(f"  [{course_code}] {title}{link}")

        print(f"\n完成！共创建 {created} 个章节。")
        print("  学生选课后，在课程页可查看章节讲义，每章可关联对应练习作业")
    finally:
        db.close()


if __name__ == "__main__":
    main()
