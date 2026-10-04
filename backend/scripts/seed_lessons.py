# -*- coding: utf-8 -*-
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
    ('第 1 章：Python 环境与第一个程序', '# 第 1 章：Python 环境与第一个程序\n\n欢迎来到 Python 编程的世界！在这一章里，我们会从"电脑是什么"讲起，带你写出人生中第一个程序。别担心，**你不需要有任何编程经验**，只要你认识字、会按键盘，就能跟着学。\n\n## 1.1 什么是编程？为什么要学 Python？\n\n### 编程是什么\n\n你平时用电脑做事情，比如打开浏览器上网、用聊天软件发消息，这些都是**别人写好的程序**在帮你干活。那如果你想让电脑做一件**没人做过的事**呢？比如：自动帮你算出全班同学的平均分？这就需要你**自己写程序**告诉电脑怎么做。\n\n**编程，就是用电脑能听懂的语言，给电脑下指令。** 电脑是非常听话的工人，但它听不懂中文、英文这些人类语言，它只听懂**编程语言**。Python 就是众多编程语言中的一种。\n\n### 为什么选 Python\n\n编程语言有很多种：C、Java、Python、JavaScript……为什么我们选 Python？\n\n1. **语法简单**：Python 的写法很像英语，没有复杂的符号，初学者容易看懂。\n2. **代码短**：同样的功能，Python 写出来比别的语言短很多。\n3. **用得广**：人工智能、网站开发、数据分析、自动化办公……Python 到处都能用。\n\n**生活类比**：如果编程语言是工具，那 C 语言像一把精密的手术刀（锋利但难用），Java 像一台全自动工厂（强大但启动慢），而 **Python 像一支好写的圆珠笔**——拿起来就能写，谁都能上手。\n\n## 1.2 安装 Python 与编写第一个程序\n\n### 安装 Python 解释器\n\n电脑本身不懂 Python，需要装一个"翻译官"——**Python 解释器**。它会把我们写的 Python 代码翻译成电脑能执行的指令。\n\n1. 打开浏览器，访问官网：https://www.python.org/downloads/\n2. 点击黄色的 "Download Python" 按钮。\n3. 下载后双击安装，**安装时务必勾选 "Add Python to PATH"**（这一步很重要，勾了才能在命令行用 python 命令）。\n\n**生活类比**：解释器就像一个翻译官。你用 Python 语言说一句话，翻译官立刻把它翻译成电脑听得懂的"0 和 1"，电脑就照着做了。\n\n### 第一个程序：Hello World\n\n学任何编程语言，传统上第一个程序都是输出 "Hello, World!"（你好，世界！）。这就像搬新家要先贴春联一样，是个好彩头。\n\n打开任意文本编辑器（记事本就行），新建一个文件 `hello.py`（`.py` 是 Python 文件的后缀名），输入：\n\n```python\nprint("Hello, World!")\n```\n\n**逐行解释**：\n- `print` 是 Python 自带的一个"命令"（叫**函数**），意思是"把括号里的内容显示到屏幕上"。\n- `"Hello, World!"` 是一串文字，用双引号包起来，表示"这是一段文字，不是变量名"。这种用引号包起来的文字叫**字符串**。\n- 括号 `()` 表示"调用这个函数"，引号里的内容是传给它的参数。\n\n保存后，打开命令行（Windows 按 Win+R 输入 cmd；Mac 打开"终端"），进入文件所在目录，运行：\n\n```\npython hello.py\n```\n\n屏幕会显示：\n\n```\nHello, World!\n```\n\n看到这句话，恭喜你！你已经写出了人生第一个程序。\n\n## 1.3 输出与输入\n\n### 输出：print()\n\n`print()` 的作用是"把内容显示到屏幕上"。它非常灵活：\n\n```python\nprint("你好")            # 显示：你好\nprint(1 + 2)            # 显示：3（先算 1+2 再显示）\nprint("1 + 2")           # 显示：1 + 2（引号里是文字，不计算）\nprint("我", "爱", "Python")  # 显示：我 爱 Python（多个内容用空格隔开）\n```\n\n**逐行解释**：\n- 第 1 行：括号里是字符串"你好"，原样显示。\n- 第 2 行：括号里是算式 `1 + 2`，Python 会**先算出结果 3**，再显示。\n- 第 3 行：因为加了引号，Python 把它当文字，不会算，原样显示 `1 + 2`。\n- 第 4 行：三个字符串用逗号隔开，print 会用空格连接它们。\n\n**重要**：`print("1 + 2")` 和 `print(1 + 2)` 完全不同！引号包起来的是"文字"，不包的是"算式"。这就像你写"3+5"在纸上 vs 用计算器算 3+5，一个只是字，一个是结果。\n\n### 输入：input()\n\n`print()` 是电脑对我们说话，`input()` 是我们向电脑说话（让电脑等我们输入）。\n\n```python\nname = input("请输入你的名字：")\nprint("你好，" + name)\n```\n\n**逐行解释**：\n- 第 1 行：`input("请输入你的名字：")` 会先显示这句话，然后**程序停下来等**你输入。你输入完按回车，输入的内容会被存进 `name` 这个变量里（变量下一节细讲）。\n- 第 2 行：把"你好，"和 `name` 里的内容拼接起来，一起显示。\n\n运行示例：\n\n```\n请输入你的名字：小明\n你好，小明\n```\n\n**关键点**：`input()` 永远返回**字符串**（文字），即使你输入了数字。比如你输入 `42`，Python 拿到的是文字"42"，不是数字 42。要把它当数字用，必须转换（见 1.5 节）。\n\n## 1.4 变量与数据类型\n\n### 变量是什么\n\n**变量是贴了标签的盒子，盒子里装东西。** 你给盒子贴个标签叫 `name`，里面放"小明"；贴个标签叫 `age`，里面放 12。要用的时候喊一声标签名，盒子就把里面的东西给你。\n\n```python\nname = "小明"    # 把"小明"放进贴着 name 标签的盒子\nage = 12          # 把 12 放进贴着 age 标签的盒子\nprint(name)       # 显示：小明\nprint(age)        # 显示：12\n```\n\n**赋值语句的格式**：`变量名 = 值`。等号 `=` 在这里是"赋值"的意思（把右边放进左边的盒子），不是数学里的"相等"。\n\n**生活类比**：变量就像你书包里的小格子。一个格子贴标签"语文书"，一个贴"数学书"。`name = "小明"` 就是给一个格子贴上 name 标签，放进"小明"这张纸条。\n\n### 变量命名规则\n\n变量名不能随便起，有几条规矩：\n1. 只能用**字母、数字、下划线**，不能有空格、不能有特殊符号。\n2. **不能用数字开头**：`1name` 错，`name1` 对。\n3. **区分大小写**：`Name` 和 `name` 是两个不同的变量。\n4. 不能用 Python 的关键字（如 `print`、`if`、`for`）做变量名。\n\n**好名字**：`student_name`、`total_score`、`age`——一看就懂。\n**坏名字**：`a`、`x1`、`asdf`——过几天自己都看不懂。\n\n### 常见数据类型\n\nPython 里有几种常见的"数据类型"，就像超市里商品分门别类：\n\n```python\nx = 10          # int（整数）：没有小数点的数\ny = 3.14        # float（浮点数/小数）：带小数点的数\ns = "hello"     # str（字符串）：用引号包起来的文字\nb = True        # bool（布尔值）：只有 True（真）和 False（假）两种\n```\n\n**生活类比**：\n- 整数 = 一整个苹果（不能切）\n- 浮点数 = 切成块的苹果（有小数）\n- 字符串 = 写着字的纸条\n- 布尔值 = 开关（只有"开"和"关"两个状态）\n\nPython 是**动态类型**语言，意思是：你不需要提前声明变量是什么类型，Python 自动判断。同一个变量还能反复"换装"：\n\n```python\nx = 10          # x 现在是整数\nx = "hello"     # x 现在变字符串了\nx = True        # x 现在变布尔值了\n```\n\n但在初学阶段，**不建议**这样换来换去，容易把自己搞晕。\n\n## 1.5 类型转换\n\n### 为什么需要转换\n\n`input()` 永远给你字符串。但你想做加法，比如输入两个数相加：\n\n```python\na = input("第一个数：")    # 输入 3\nb = input("第二个数：")    # 输入 5\nprint(a + b)              # 显示：35（不是 8！）\n```\n\n为什么显示 35 而不是 8？因为 `a` 和 `b` 都是字符串"3"和"5"，`+` 对字符串来说是"拼接"（把两段文字连起来），不是数学加法。"3" + "5" = "35"，就像"你" + "好" = "你好"。\n\n### 怎么转换\n\n用 `int()` 把字符串转成整数，用 `float()` 转成小数，用 `str()` 把数字转成字符串：\n\n```python\na = int(input("第一个数："))   # 输入 3，转成整数 3\nb = int(input("第二个数："))   # 输入 5，转成整数 5\nprint(a + b)                  # 显示：8（现在是数学加法）\n```\n\n**逐行解释**：\n- `input(...)` 先拿到字符串"3"。\n- `int(...)` 把字符串"3"转换成整数 3。\n- 把整数 3 存进 `a`。\n- 同理 `b` 是整数 5。\n- `a + b` 现在是两个整数相加，得到 8。\n\n```python\ns = "3.14"\nn = float(s)      # 字符串 → 浮点数 3.14\nprint(n * 2)      # 显示：6.28\n\nnum = 100\ntext = str(num)   # 整数 100 → 字符串 "100"\nprint("分数：" + text)   # 显示：分数：100\n```\n\n## 常见错误\n\n### 错误 1：忘了引号\n\n```python\nprint(你好)     # 错！Python 以为你好是变量名\n```\n\n修正：字符串要加引号。\n\n```python\nprint("你好")   # 对\n```\n\n### 错误 2：input 没转换就做数学\n\n```python\nage = input("年龄：")    # 输入 12\nprint(age + 1)          # 报错！字符串不能加整数\n```\n\n修正：用 int 转换。\n\n```python\nage = int(input("年龄："))\nprint(age + 1)           # 显示：13\n```\n\n### 错误 3：int 转换小数字符串\n\n```python\nn = int("3.14")    # 报错 ValueError\n```\n\n修正：小数要用 float。\n\n```python\nn = float("3.14")  # 对\n```\n\n## 本章要点\n\n1. **编程就是用电脑听得懂的语言给它下指令**，Python 是一门简洁易学的语言。\n2. `print()` 输出内容到屏幕，`input()` 等待用户输入，input 返回的永远是字符串。\n3. **变量**是贴了标签的盒子，用 `变量名 = 值` 来赋值。\n4. 常见类型：`int` 整数、`float` 小数、`str` 字符串、`bool` 真假。\n5. 做数学运算前，必须把字符串转换成数字（`int()` 或 `float()`）。\n6. **引号里的内容是文字**，不会计算；不带引号才会被当成变量或算式。\n\n## 动手试试\n\n1. 写一个程序，输入你的名字和年龄，输出"我叫XX，今年X岁"。\n2. 输入两个整数，输出它们的和、差、积、商。\n3. 想一想：`print("3" + "5")` 和 `print(3 + 5)` 分别显示什么？为什么？', '两数之和'),
    ('第 2 章：条件判断', '# 第 2 章：条件判断\n\n这一章我们学习让电脑"做选择"。生活中我们每天都在做判断——"如果下雨就带伞，否则就不带"。电脑也能这样做，只要你用 Python 告诉它条件。\n\n## 2.1 什么是条件判断\n\n### 生活里的判断\n\n你每天出门前会想：\n- 如果**下雨**，就**带伞**。\n- 如果**不下雨**，就**不带伞**。\n\n这就是条件判断：**根据某个条件是否成立，决定做不同的事**。Python 也能做这种判断，用的是 `if` 语句。\n\n**生活类比**：条件判断就像走到十字路口选方向。前面有两条路，你看路牌（条件），决定走哪条。`if` 就是"看路牌"这个动作。\n\n### 最简单的 if\n\n```python\nage = int(input("请输入年龄："))\nif age >= 18:\n    print("你已经成年了")\n```\n\n**逐行解释**：\n- 第 1 行：输入年龄，用 `int()` 转成数字。\n- 第 2 行：`if age >= 18:` 意思是"如果 age 大于等于 18"。注意末尾有**冒号 `:`**。\n- 第 3 行：这行**缩进了 4 个空格**，表示"属于 if 的内容"。条件成立时才会执行。\n\n**关键**：Python 用**缩进**（行首的空格）来表示"这行代码属于上面那个 if"。这是 Python 的特色——别的语言用大括号 `{}`，Python 用空格。**缩进必须一致**，通常用 4 个空格。\n\n## 2.2 if-else（二选一）\n\n### 语法\n\n`if` 后面可以跟 `else`，表示"如果条件成立做 A，否则做 B"。\n\n```python\nage = int(input("请输入年龄："))\nif age >= 18:\n    print("成年")\nelse:\n    print("未成年")\n```\n\n**逐行解释**：\n- `if age >= 18:` 条件成立（成年），执行下一行。\n- `print("成年")` 属于 if，条件成立时执行。\n- `else:` 意思是"否则"——条件不成立时走这里。\n- `print("未成年")` 属于 else，条件不成立时执行。\n\n**执行流程**：电脑先看 `if` 条件，成立就做 if 下面的，不成立就做 else 下面的，**二选一**。\n\n### 奇偶判断\n\n判断一个数是奇数还是偶数，用**取余运算符 `%`**。`n % 2` 表示 n 除以 2 的余数。余数为 0 是偶数，余数 1 是奇数。\n\n```python\nn = int(input("请输入一个整数："))\nif n % 2 == 0:\n    print("偶数")\nelse:\n    print("奇数")\n```\n\n**逐行解释**：\n- `n % 2` 算 n 除以 2 的余数（比如 6 % 2 = 0，7 % 2 = 1）。\n- `==` 是"等于"的判断（注意：**两个等号**，不是赋值的一个等号 `=`）。\n- 余数等于 0 → 偶数；否则 → 奇数。\n\n## 2.3 if-elif-else（多选一）\n\n### 为什么需要 elif\n\n成绩分等级：90 以上 A，80-89 B，60-79 C，60 以下 D。这是**多选一**，不是二选一。用 `elif`（else if 的缩写）。\n\n```python\nscore = int(input("请输入成绩："))\nif score >= 90:\n    print("A")\nelif score >= 80:\n    print("B")\nelif score >= 60:\n    print("C")\nelse:\n    print("D")\n```\n\n**逐行解释**：\n- 电脑**从上到下**依次检查每个条件。\n- 第 1 个 `if score >= 90`：成立就打印 A，然后**跳过所有 elif 和 else**，结束。\n- 如果第 1 个不成立，看第 2 个 `elif score >= 80`：成立打印 B，跳过后面。\n- 依此类推。\n- 如果所有 if/elif 都不成立，执行 `else`。\n\n**重要**：条件是**从上到下**判断的，一旦某个条件成立，后面的都不会再看了。所以顺序很重要。如果你写成 `if score >= 60` 在最前面，那 95 分也会先满足 >=60 而打印 C，就错了。\n\n### elif vs 多个 if\n\n```python\n# 错误写法：用多个独立 if\nif score >= 90:\n    print("A")\nif score >= 80:     # 即使已经打印了 A，这里还会再判断\n    print("B")\n```\n\n这样 95 分会同时打印 A 和 B，因为每个 if 都会独立判断。而 `elif` 是"前面的 if 不成立才看这个"，**互斥**的。\n\n## 2.4 比较运算符\n\n判断条件离不开比较运算符：\n\n| 运算符 | 含义 | 例子 |\n|--------|------|------|\n| `==` | 等于 | `a == b` |\n| `!=` | 不等于 | `a != b` |\n| `>` | 大于 | `a > b` |\n| `<` | 小于 | `a < b` |\n| `>=` | 大于等于 | `a >= b` |\n| `<=` | 小于等于 | `a <= b` |\n\n**注意**：`==`（两个等号）是判断相等，`=`（一个等号）是赋值。这是初学者最常混的。\n\n```python\nx = 5      # 赋值：把 5 放进 x\nif x == 5:  # 判断：x 等于 5 吗？\n    print("x 是 5")\n```\n\n## 2.5 逻辑运算符\n\n有时一个条件不够，需要**组合多个条件**。Python 有三个逻辑运算符：\n\n- `and`（并且）：**两个都成立**才算成立。\n- `or`（或者）：**任一个成立**就算成立。\n- `not`（非）：**取反**，True 变 False，False 变 True。\n\n```python\nage = 20\nif age >= 18 and age <= 60:\n    print("适龄劳动者")\n```\n\n意思是"年龄 >= 18 **并且** 年龄 <= 60"才打印。两个条件都要满足。\n\n```python\nweather = "晴天"\nif weather == "晴天" or weather == "多云":\n    print("适合出门")\n```\n\n意思是"晴天**或**多云"都适合出门，只要满足一个。\n\n```python\nraining = False\nif not raining:\n    print("不用带伞")\n```\n\n`not raining` 把 False 变成 True，所以打印"不用带伞"。\n\n### 简写：链式比较\n\nPython 支持"链式比较"，像数学里的写法：\n\n```python\nif 0 < n < 100:    # 等价于 n > 0 and n < 100\n    print("n 在 0 到 100 之间")\n```\n\n## 2.6 嵌套判断\n\nif 里面还能再套 if，叫**嵌套**：\n\n```python\nage = int(input())\ngender = input()\nif age >= 18:\n    if gender == "男":\n        print("成年男性")\n    else:\n        print("成年女性")\nelse:\n    print("未成年")\n```\n\n**注意缩进**：内层 if 要比外层 if 多缩进 4 个空格。\n\n## 常见错误\n\n### 错误 1：忘了冒号\n\n```python\nif age >= 18      # 错！末尾少冒号\n    print("成年")\n```\n\n修正：if 末尾加冒号。\n\n```python\nif age >= 18:\n    print("成年")\n```\n\n### 错误 2：用 = 当比较\n\n```python\nif age = 18:     # 错！= 是赋值，不是比较\n    print("18")\n```\n\n修正：比较用 `==`。\n\n```python\nif age == 18:\n    print("18")\n```\n\n### 错误 3：缩进不一致\n\n```python\nif age >= 18:\n    print("成年")\n      print("可以上网")    # 错！缩进多了\n```\n\n修正：同一代码块的缩进要一致。\n\n```python\nif age >= 18:\n    print("成年")\n    print("可以上网")    # 都是 4 空格\n```\n\n## 本章要点\n\n1. `if` 让程序根据条件决定执行什么——**像十字路口选方向**。\n2. `if-else` 是二选一，`if-elif-else` 是多选一。\n3. **冒号 `:` 不能忘**，条件后面必须有。\n4. **缩进 4 个空格**表示代码属于哪个 if，必须一致。\n5. `==` 是比较相等，`=` 是赋值，**不要混**。\n6. `and`（且）、`or`（或）、`not`（非）组合多个条件。\n\n## 动手试试\n\n1. 输入一个数，判断它是正数、负数还是零。\n2. 输入身高和体重，判断 BMI 是否正常（BMI = 体重/身高²，18.5-24 正常）。\n3. 想一想：`if score >= 60: print("及格")` 和 `if not score < 60: print("及格")` 效果一样吗？', '判断奇偶'),
    ('第 3 章：循环基础', '# 第 3 章：循环基础\n\n上一章我们学了条件判断，让电脑能"做选择"。这一章学**循环**，让电脑能"重复做同一件事"。想象你要抄写 100 遍生字，让人来抄手都酸了，但电脑几毫秒就搞定——这就是循环的威力。\n\n## 3.1 什么是循环？为什么需要它\n\n### 生活里的重复\n\n老师让你抄写"我要好好学习"100 遍。你不会真的写 100 行 `print("我要好好学习")` 吧？那太累了。**循环**就是让电脑自动重复执行同一段代码。\n\n**生活类比**：循环就像你拿着一张写好的字条，在复印机上按 100 下复印键——字条只写一次，但能印出 100 份。循环让你**写一次代码，重复执行多次**。\n\n### 两种循环\n\nPython 有两种循环：\n- `for` 循环：**已知重复次数**时用（比如抄 100 遍）。\n- `while` 循环：**不知道重复几次，只知道停止条件**时用（比如一直读输入直到读到 0）。\n\n## 3.2 for 循环\n\n### 基本语法\n\n```python\nfor 变量 in 序列:\n    要重复做的事\n```\n\n最常用的"序列"是 `range()`，它生成一串数字。\n\n### range 的三种用法\n\n```python\nfor i in range(5):      # i 依次取 0,1,2,3,4\n    print(i)\n\nfor i in range(1, 6):  # i 依次取 1,2,3,4,5\n    print(i)\n\nfor i in range(0, 10, 2):  # i 依次取 0,2,4,6,8\n    print(i)\n```\n\n**逐行解释**：\n- `range(5)`：生成从 0 开始、**不包含 5** 的 5 个数：0,1,2,3,4。\n- `range(1, 6)`：从 1 开始、**不包含 6**：1,2,3,4,5。\n- `range(0, 10, 2)`：从 0 开始、到 10 之前、**每次加 2**：0,2,4,6,8。\n\n**记忆口诀**：`range(开始, 结束, 步长)`——**包含开始，不包含结束**。\n\n### 抄写 100 遍\n\n```python\nfor i in range(100):\n    print("我要好好学习")\n```\n\n`i` 从 0 取到 99，每次都打印这句话，共打印 100 次。`i` 是循环变量，记录当前是第几次。\n\n### 累加求和\n\n求 1+2+3+...+100 的和：\n\n```python\ntotal = 0                    # 先准备一个"累加器"，初始为 0\nfor i in range(1, 101):     # i 从 1 到 100\n    total = total + i        # 每次把 i 加到 total 上\nprint(total)                # 显示：5050\n```\n\n**逐行解释**：\n- `total = 0`：像准备一个空盒子，准备往里放东西。\n- `for i in range(1, 101)`：i 依次是 1,2,3,...,100。\n- `total = total + i`：把当前的 total 值加上 i，再放回 total。比如第 1 次：0+1=1；第 2 次：1+2=3；第 3 次：3+3=6……\n- 最后 total 就是 1 到 100 的和 5050。\n\n**生活类比**：累加就像往储蓄罐里存钱。一开始储蓄罐空（total=0），每天存 i 元，存 100 天后打开看总额。\n\n## 3.3 while 循环\n\n### 基本语法\n\n```python\nwhile 条件:\n    要重复做的事\n```\n\n意思是"**当条件成立时**，就一直重复做"。\n\n```python\nn = int(input())\nwhile n > 0:\n    print(n)\n    n = n - 1\n```\n\n**逐行解释**：\n- `n = int(input())`：输入一个数，比如 3。\n- `while n > 0:`：只要 n 大于 0，就一直循环。\n- 第 1 轮：n=3，打印 3，然后 n=3-1=2。\n- 第 2 轮：n=2，打印 2，然后 n=2-1=1。\n- 第 3 轮：n=1，打印 1，然后 n=1-1=0。\n- 第 4 轮：n=0，条件 `n > 0` 不成立，循环结束。\n\n输出：3, 2, 1。\n\n### for vs while\n\n- **知道次数**用 for：抄 100 遍、遍历 1 到 100。\n- **不知道次数、只知道停止条件**用 while：读输入直到读到 0、不断猜数直到猜对。\n\n## 3.4 break 与 continue\n\n### break：提前跳出\n\n`break` 让循环**立即结束**，不再继续。\n\n```python\nfor i in range(1, 11):     # i 从 1 到 10\n    if i == 5:\n        break               # i 等于 5 时，跳出循环\n    print(i)\n# 输出：1 2 3 4\n```\n\ni=5 时触发 break，循环结束，5 和后面的都不打印。\n\n### continue：跳过本次\n\n`continue` 跳过**这一次**剩余的代码，直接进入下一轮循环。\n\n```python\nfor i in range(1, 11):\n    if i % 2 == 0:      # 偶数\n        continue         # 跳过这次，不打印偶数\n    print(i)\n# 输出：1 3 5 7 9\n```\n\ni 是偶数时，`continue` 跳过下面的 `print`，直接进入下一轮。所以只打印奇数。\n\n**区别**：`break` 是"我不干了，结束"，`continue` 是"这次跳过，继续下一次"。\n\n## 常见错误\n\n### 错误 1：忘了更新循环变量（死循环）\n\n```python\nn = 5\nwhile n > 0:\n    print(n)\n    # 忘了 n = n - 1，n 永远是 5，无限循环！\n```\n\n修正：循环体里要让条件逐渐"不成立"。\n\n```python\nn = 5\nwhile n > 0:\n    print(n)\n    n = n - 1    # 每次减 1，最终 n=0 时停止\n```\n\n### 错误 2：range 边界搞错\n\n```python\nfor i in range(1, 100):    # 想要 1 到 100，实际只有 1 到 99\n    print(i)\n```\n\n修正：range 不包含结束值，要写 101。\n\n```python\nfor i in range(1, 101):    # 1 到 100\n    print(i)\n```\n\n### 错误 3：忘了冒号或缩进\n\n```python\nfor i in range(5)    # 错！少冒号\nprint(i)             # 错！没缩进，不属于循环\n```\n\n修正：\n\n```python\nfor i in range(5):\n    print(i)\n```\n\n## 本章要点\n\n1. **循环让电脑自动重复做事**——像复印机按多次复印键。\n2. `for` 用于**已知次数**，`while` 用于**已知停止条件**。\n3. `range(a, b)` 生成 a 到 b-1，**含 a 不含 b**。\n4. 累加套路：`total = 0` 开始，循环里 `total = total + i`。\n5. `break` 跳出整个循环，`continue` 跳过本次。\n6. while 循环**必须在循环体里更新条件变量**，否则死循环。\n\n## 动手试试\n\n1. 用 for 循环打印 1 到 100 里所有 3 的倍数。\n2. 输入一个正整数 n，求 1+2+...+n 的和。\n3. 想一想：怎么用 while 循环实现"输入若干个数，输入 0 时停止，求和"？', '数组求和'),
    ('第 4 章：列表（数组）', '# 第 4 章：列表（数组）\n\n前面我们学的变量一次只能装**一个**值。但生活中常常要处理**一堆**数据，比如全班 50 个同学的成绩、购物车里的 10 件商品。这种"装一串数据"的容器，Python 叫**列表（list）**。\n\n## 4.1 什么是列表\n\n### 生活类比\n\n列表就像**一排编了号的抽屉**。每个抽屉有个编号（从 0 开始），里面装一个东西。你可以按编号打开抽屉拿东西，也可以往抽屉里放新东西。\n\n```\n编号:   0    1    2    3    4\n内容:  [88, 95, 76, 60, 82]\n```\n\n### 创建列表\n\n用**方括号 `[]`** 把一串数据包起来，数据之间用逗号隔开：\n\n```python\nscores = [88, 95, 76, 60, 82]\nnames = ["小明", "小红", "小刚"]\nempty = []                    # 空列表\n```\n\n### 访问元素\n\n用 `列表名[编号]` 访问某个抽屉，这个编号叫**索引**，**从 0 开始**：\n\n```python\nscores = [88, 95, 76, 60, 82]\nprint(scores[0])    # 88（第 1 个，编号 0）\nprint(scores[1])    # 95（第 2 个，编号 1）\nprint(scores[4])    # 82（第 5 个，编号 4）\n```\n\n**为什么从 0 开始？** 这是编程的惯例。可以理解成"偏移量"：第 1 个元素离起点偏移 0 位，第 2 个偏移 1 位。\n\n### 负索引\n\nPython 支持从后往前数，用负数：\n\n```python\nprint(scores[-1])   # 82（倒数第 1 个）\nprint(scores[-2])   # 60（倒数第 2 个）\n```\n\n### 长度\n\n`len(列表)` 返回元素个数：\n\n```python\nprint(len(scores))  # 5\n```\n\n## 4.2 从输入创建列表\n\n### 一次读一行多个数\n\n很多题目是这样输入的：第一行一个数 n，第二行 n 个用空格隔开的数。怎么读？\n\n```python\nn = int(input())                          # 读 n\narr = list(map(int, input().split()))     # 读一行，转成整数列表\nprint(arr)\n```\n\n输入示例：\n```\n5\n3 1 4 1 5\n```\n\n输出：`[3, 1, 4, 1, 5]`\n\n**逐行解释**：\n- `input()` 读一整行字符串 `"3 1 4 1 5"`。\n- `.split()` 按空格切分，得到字符串列表 `[\'3\', \'1\', \'4\', \'1\', \'5\']`。\n- `map(int, ...)` 把每个字符串转成整数。\n- `list(...)` 把结果转成列表。\n\n### 一行行读\n\n```python\nn = int(input())\narr = []\nfor _ in range(n):\n    arr.append(int(input()))    # append 往尾部加一个\n```\n\n## 4.3 遍历列表\n\n### 方式一：直接遍历元素\n\n```python\nscores = [88, 95, 76, 60, 82]\nfor s in scores:        # s 依次取每个成绩\n    print(s)\n```\n\n### 方式二：遍历索引\n\n```python\nfor i in range(len(scores)):    # i 从 0 到 4\n    print(scores[i])\n```\n\n### 方式三：同时要索引和值\n\n```python\nfor i, s in enumerate(scores):\n    print(f"第{i+1}个成绩是{s}")\n```\n\n**生活类比**：遍历就像老师挨个点名。方式一是只念名字，方式二是按学号念，方式三是学号和名字一起念。\n\n## 4.4 列表常用操作\n\n### 增删改\n\n```python\narr = [1, 2, 3]\narr.append(4)         # 尾部添加：[1, 2, 3, 4]\narr.insert(0, 0)       # 在索引 0 处插入 0：[0, 1, 2, 3, 4]\narr[0] = 10            # 修改第 0 个：[10, 1, 2, 3, 4]\narr.remove(2)          # 删除第一个值为 2 的元素\narr.pop()              # 删除并返回最后一个\ndel arr[0]             # 删除指定索引\n```\n\n### 查询和统计\n\n```python\narr = [3, 1, 4, 1, 5]\nprint(len(arr))      # 5（长度）\nprint(max(arr))      # 5（最大值）\nprint(min(arr))      # 1（最小值）\nprint(sum(arr))      # 14（求和）\nprint(arr.count(1))   # 2（1 出现的次数）\nprint(arr.index(4))  # 2（4 的索引）\n```\n\n### 排序与反转\n\n```python\narr = [3, 1, 4, 1, 5]\narr.sort()           # 升序排列：[1, 1, 3, 4, 5]\narr.sort(reverse=True)  # 降序：[5, 4, 3, 1, 1]\narr.reverse()        # 反转\n```\n\n### 切片\n\n取列表的一部分，用 `列表[开始:结束]`，**含开始不含结束**：\n\n```python\narr = [10, 20, 30, 40, 50]\nprint(arr[1:3])    # [20, 30]（索引 1、2）\nprint(arr[:2])     # [10, 20]（从头到索引 1）\nprint(arr[2:])     # [30, 40, 50]（从索引 2 到末尾）\n```\n\n## 常见错误\n\n### 错误 1：索引越界\n\n```python\narr = [1, 2, 3]\nprint(arr[3])    # 错！索引最大是 2，越界报 IndexError\n```\n\n修正：列表有 n 个元素，索引范围是 0 到 n-1。\n\n```python\nprint(arr[2])    # 3（最后一个）\nprint(arr[-1])   # 3（用负索引也行）\n```\n\n### 错误 2：用 + 给列表加元素\n\n```python\narr = [1, 2, 3]\narr + 4     # 错！列表不能直接加整数\n```\n\n修正：用 append，或加列表。\n\n```python\narr.append(4)      # 对\narr = arr + [4]    # 也对（加一个列表）\n```\n\n### 错误 3：遍历时修改列表\n\n```python\narr = [1, 2, 3, 4]\nfor x in arr:\n    if x == 2:\n        arr.remove(x)    # 遍历时删除，会漏元素\n```\n\n修正：遍历副本，或用推导式。\n\n```python\narr = [x for x in arr if x != 2]\n```\n\n## 本章要点\n\n1. **列表是一排编了号的抽屉**，用 `[]` 创建，元素用逗号隔开。\n2. **索引从 0 开始**，最大到 `len-1`；负索引从后往前数（-1 是最后一个）。\n3. 读一行多个数：`list(map(int, input().split()))`。\n4. 遍历：`for x in arr` 直接取元素，`for i in range(len(arr))` 取索引。\n5. 常用：`append` 加、`sort` 排序、`max/min/sum` 统计、`len` 长度。\n6. 切片 `[a:b]` **含 a 不含 b**。\n\n## 动手试试\n\n1. 输入 n 个数，输出最大值和最小值之差。\n2. 输入 n 个成绩，输出平均值（保留 2 位小数）。\n3. 想一想：怎么把一个列表原地反转？（提示：`reverse()` 或切片 `[::-1]`）', '数组最大值'),
    ('第 5 章：字符串基础', '# 第 5 章：字符串基础\n\n字符串就是"一串文字"。我们在第 1 章已经用过它（`print("Hello")`）。这一章深入学习字符串的各种操作——它比你想象的强大得多。\n\n## 5.1 什么是字符串\n\n### 概念\n\n**字符串是一串字符，用引号包起来。** 单引号、双引号都行，三引号可以包多行。\n\n```python\ns1 = "hello"\ns2 = \'world\'\ns3 = \'\'\'这是\n多行字符串\'\'\'\n```\n\n**生活类比**：字符串就像一串珍珠项链——每颗珍珠是一个字符，按顺序串在一起。你可以单独取一颗，也可以一段一段切下来。\n\n### 字符串长度与单个字符\n\n```python\ns = "hello"\nprint(len(s))    # 5（5 个字符）\nprint(s[0])      # h（第 0 个字符）\nprint(s[-1])     # o（最后一个）\n```\n\n字符串和列表一样，可以用索引取单个字符，也能用负索引。\n\n## 5.2 字符串不可变\n\n**重要**：Python 的字符串**不可变**——创建后不能修改其中的字符。所有"修改"操作都是返回一个**新字符串**，原字符串不变。\n\n```python\ns = "hello"\ns[0] = "H"     # 错！字符串不能这样改\n```\n\n要"改"，只能造一个新字符串：\n\n```python\ns = "hello"\ns = "H" + s[1:]    # 新字符串 "Hello"\nprint(s)            # Hello\n```\n\n## 5.3 切片\n\n和列表一样，字符串可以**切片**取一段：\n\n```python\ns = "hello world"\nprint(s[0:5])     # hello（索引 0 到 4）\nprint(s[6:])      # world（从索引 6 到末尾）\nprint(s[:5])       # hello（从头到索引 4）\nprint(s[-5:])      # world（最后 5 个字符）\nprint(s[::-1])     # dlrow olleh（反转！）\n```\n\n**`[::-1]` 解释**：`[开始:结束:步长]`，开始和结束都省略表示全部，步长 -1 表示**从后往前**——所以是反转。\n\n**记忆**：切片 `[a:b]` 含 a 不含 b，和 range 一样。\n\n## 5.4 拼接与重复\n\n### 拼接：+\n\n```python\ns = "你好" + "，" + "世界"\nprint(s)    # 你好，世界\n```\n\n### 重复：*\n\n```python\nprint("=" * 10)    # ==========\nprint("ab" * 3)     # ababab\n```\n\n字符串乘整数 = 重复若干次。这在打印分隔线时很有用。\n\n## 5.5 分割与连接\n\n### split：分割\n\n`split()` 把字符串按分隔符切成列表：\n\n```python\ns = "1 2 3 4 5"\nparts = s.split()        # 默认按空白切：[\'1\', \'2\', \'3\', \'4\', \'5\']\nprint(parts)\n\ns = "a,b,c"\nparts = s.split(",")    # 按逗号切：[\'a\', \'b\', \'c\']\n```\n\n### join：连接\n\n`join` 是 split 的反操作，把列表用某分隔符连成字符串：\n\n```python\nparts = [\'a\', \'b\', \'c\']\ns = "-".join(parts)     # a-b-c\nprint(s)\n\nnums = [\'1\', \'2\', \'3\']\ns = "+".join(nums)      # 1+2+3\n```\n\n**注意语法**：是 `分隔符.join(列表)`，不是 `列表.join(分隔符)`。可以理解为：分隔符"钻进"列表元素之间把它们连起来。\n\n## 5.6 常用方法\n\n```python\ns = "  Hello World  "\nprint(s.strip())         # "Hello World"（去首尾空白）\nprint(s.upper())         # 全大写\nprint(s.lower())         # 全小写\nprint(s.replace("l", "L"))  # 替换\nprint(s.find("World"))   # 查找子串，返回索引，找不到返回 -1\nprint(s.count("l"))      # 字符 l 出现次数\n```\n\n### 判断类方法\n\n```python\n"123".isdigit()      # True（全是数字）\n"abc".isalpha()      # True（全是字母）\n"abc123".isalnum()   # True（字母或数字）\n"hello".startswith("he")  # True\n"hello".endswith("lo")    # True\n```\n\n## 5.7 f-string 格式化\n\n拼接字符串用 `+` 不够方便，f-string 更优雅——在字符串前加 `f`，用 `{}` 放变量：\n\n```python\nname = "小明"\nscore = 95\nprint(f"{name}的成绩是{score}分")    # 小明的成绩是95分\nprint(f"平均分：{95/3:.2f}")        # 保留 2 位小数\n```\n\n**逐行解释**：\n- `f"..."` 表示这是格式化字符串。\n- `{name}` 会被替换成变量 name 的值。\n- `{95/3:.2f}` 中 `:.2f` 表示保留 2 位小数。\n\n## 常见错误\n\n### 错误 1：混淆 + 和数字\n\n```python\nage = 12\nprint("年龄：" + age)    # 错！字符串不能加整数\n```\n\n修正：用 str 转换，或用 f-string。\n\n```python\nprint("年龄：" + str(age))      # 对\nprint(f"年龄：{age}")           # 更优雅\n```\n\n### 错误 2：引号不匹配\n\n```python\ns = "It\'s a book\'    # 错！引号不配对\n```\n\n修正：内外用不同引号。\n\n```python\ns = "It\'s a book"    # 外双内单，对\n```\n\n### 错误 3：修改字符串\n\n```python\ns = "hello"\ns[0] = "H"     # 错！字符串不可变\n```\n\n修正：造新字符串。\n\n```python\ns = "H" + s[1:]\n```\n\n## 本章要点\n\n1. **字符串是一串字符**，用引号包起来，可用 `len()`、索引、切片。\n2. **字符串不可变**——修改操作返回新字符串，原字符串不变。\n3. 切片 `[a:b]` 含 a 不含 b，`[::-1]` 反转字符串。\n4. `+` 拼接，`*` 重复，`split` 分割，`join` 连接。\n5. 常用方法：`strip`、`upper`、`lower`、`replace`、`find`、`count`。\n6. **f-string**（`f"...{变量}..."`）是最优雅的字符串拼接方式。\n\n## 动手试试\n\n1. 输入一个字符串，反转后输出。\n2. 输入一行用空格隔开的数字，输出它们的和（提示：split + int 转换）。\n3. 想一想：怎么统计一个字符串里有多少个元音字母（a/e/i/o/u）？', '字符串反转'),
    ('第 6 章：函数', '# 第 6 章：函数\n\n到现在你写的代码都是"一条龙"从头写到尾。当代码变长，你会发现有些代码**重复出现**——比如每次都要算"两数之和"。函数就是把这些重复的代码"打包"起来，起个名字，以后用名字就能调用。\n\n## 6.1 什么是函数\n\n### 生活类比\n\n函数就像**菜谱**。你给菜谱一些原料（食材），它告诉你怎么做出一道菜。原料叫**参数**，做出来的菜叫**返回值**。菜谱写一次，你想做几次就照着做几次。\n\n```\n菜谱"炒蛋"：原料=鸡蛋2个 → 步骤 → 成品=一盘炒蛋\n```\n\n对应函数：\n\n```python\ndef scramble(eggs):\n    # 步骤（代码）\n    return "一盘炒蛋"   # 成品\n```\n\n### 为什么要函数\n\n1. **避免重复**：写一次，用多次。\n2. **让代码更清晰**：把长代码分成有名字的小块。\n3. **方便修改**：要改逻辑，只改函数里一处。\n\n## 6.2 定义和调用函数\n\n### 定义语法\n\n```python\ndef 函数名(参数):\n    函数体（要执行的代码）\n    return 返回值\n```\n\n- `def` 是 define（定义）的缩写，告诉 Python"我要定义一个函数"。\n- 函数名遵循变量命名规则，建议用小写加下划线，如 `add`、`get_max`。\n- 参数是给函数的"原料"，可有可无。\n- `return` 是"返回成品"，函数到这里结束并把值送回调用处。\n\n### 第一个函数\n\n```python\ndef greet(name):\n    return "Hello, " + name\n\nprint(greet("Alice"))    # Hello, Alice\nprint(greet("Bob"))      # Hello, Bob\n```\n\n**逐行解释**：\n- `def greet(name):` 定义一个叫 greet 的函数，它接收一个参数 name。\n- `return "Hello, " + name` 把"Hello, "和 name 拼接，返回给调用者。\n- `greet("Alice")` **调用**函数，传入"Alice"。函数返回"Hello, Alice"。\n- `print(...)` 把返回值打印出来。\n\n**生活类比**：定义函数像写下菜谱，调用函数像"按菜谱做菜"。菜谱写一次，做多少次都行。\n\n## 6.3 参数与返回值\n\n### 多个参数\n\n```python\ndef add(a, b):\n    return a + b\n\nprint(add(3, 5))    # 8\n```\n\n`a` 和 `b` 是参数，调用时按**位置**对应：3 给 a，5 给 b。\n\n### 多个返回值\n\nPython 函数能返回多个值（用元组）：\n\n```python\ndef min_max(arr):\n    return min(arr), max(arr)\n\nlo, hi = min_max([3, 1, 4, 1, 5])\nprint(lo, hi)    # 1 5\n```\n\n### 无返回值\n\n没有 `return` 或 `return` 后面没值，函数返回 `None`（空值）：\n\n```python\ndef say_hello(name):\n    print("你好，" + name)\n    # 没 return\n\nresult = say_hello("小明")    # 打印"你好，小明"\nprint(result)                  # None\n```\n\n## 6.4 默认参数\n\n参数可以设"默认值"，调用时不传就用默认：\n\n```python\ndef greet(name, greeting="Hello"):\n    return f"{greeting}, {name}"\n\nprint(greet("Alice"))           # Hello, Alice（用默认 greeting）\nprint(greet("Bob", "Hi"))       # Hi, Bob（传入 greeting）\n```\n\n**逐行解释**：\n- `greeting="Hello"` 表示参数 greeting 的默认值是"Hello"。\n- 调用 `greet("Alice")` 只传一个参数，greeting 用默认值"Hello"。\n- 调用 `greet("Bob", "Hi")` 传两个参数，greeting 用"Hi"覆盖默认值。\n\n## 6.5 写一个完整的例子：判断素数\n\n把前面学的综合起来，写一个判断素数的函数：\n\n```python\ndef is_prime(n):\n    if n < 2:\n        return False        # 小于 2 不是素数\n    for i in range(2, n):   # 从 2 试到 n-1\n        if n % i == 0:      # 能整除，不是素数\n            return False\n    return True             # 全不能整除，是素数\n\nn = int(input())\nif is_prime(n):\n    print(f"{n} 是素数")\nelse:\n    print(f"{n} 不是素数")\n```\n\n**逐行解释**：\n- `def is_prime(n):` 定义函数，接收 n。\n- `if n < 2: return False`：0 和 1 不是素数。\n- `for i in range(2, n)`：i 从 2 到 n-1。\n- `if n % i == 0: return False`：如果 n 能被 i 整除（余数为 0），说明有因子，不是素数，立刻返回 False。\n- 循环结束没找到因子，返回 True。\n\n## 6.6 变量作用域\n\n函数**内部**的变量叫**局部变量**，函数外**看不到**：\n\n```python\ndef test():\n    x = 10          # 局部变量\n    print(x)        # 10\n\ntest()\nprint(x)            # 错！函数外访问不到 x\n```\n\n函数**外**的变量叫**全局变量**，函数内**能读不能改**（除非用 global）：\n\n```python\npi = 3.14          # 全局变量\ndef area(r):\n    return pi * r * r    # 能读全局变量\n```\n\n**生活类比**：局部变量像你家的碗，只能在自家厨房用；全局变量像公共广场的时钟，所有人都能看到时间。\n\n## 常见错误\n\n### 错误 1：调用前没定义\n\n```python\nprint(add(3, 5))    # 错！add 还没定义\ndef add(a, b):\n    return a + b\n```\n\n修正：先定义后调用。\n\n```python\ndef add(a, b):\n    return a + b\nprint(add(3, 5))    # 对\n```\n\n### 错误 2：参数数量不对\n\n```python\ndef add(a, b):\n    return a + b\nprint(add(1, 2, 3))    # 错！只要 2 个参数\n```\n\n修正：参数数量要匹配。\n\n```python\nprint(add(1, 2))    # 对\n```\n\n### 错误 3：忘了 return\n\n```python\ndef add(a, b):\n    result = a + b    # 忘了 return\nprint(add(1, 2))     # 显示 None\n```\n\n修正：要返回结果必须 return。\n\n```python\ndef add(a, b):\n    return a + b\n```\n\n## 本章要点\n\n1. **函数是菜谱**：给参数（原料），返回结果（成品），写一次用多次。\n2. 用 `def 函数名(参数):` 定义，用 `函数名(值)` 调用。\n3. `return` 返回值；没 return 则返回 None。\n4. 参数按位置对应；可设默认值。\n5. 局部变量只在函数内有效，全局变量函数内可读。\n6. 函数让代码不重复、更清晰、易修改。\n\n## 动手试试\n\n1. 写一个函数 `max_of_three(a, b, c)` 返回三个数的最大值。\n2. 写一个函数 `is_even(n)` 判断 n 是否偶数，返回 True/False。\n3. 想一想：为什么"先定义后调用"？电脑读代码是从上到下的，定义前它不知道这函数存在。', None),
    ('第 7 章：多重循环', '# 第 7 章：多重循环\n\n前面学的循环只有一层。但有些问题一层循环搞不定——比如打印一个乘法表，要行也要列。这时需要**循环套循环**，叫**多重循环**（嵌套循环）。\n\n## 7.1 什么是多重循环\n\n### 概念\n\n多重循环就是**一个循环里面再套一个循环**。外层循环每走一步，内层循环**完整地走一圈**。\n\n```python\nfor i in range(3):          # 外层：i = 0, 1, 2\n    for j in range(3):      # 内层：每次 j 完整走 0,1,2\n        print(f"({i}, {j})")\n```\n\n输出：\n```\n(0, 0)\n(0, 1)\n(0, 2)\n(1, 0)\n(1, 1)\n(1, 2)\n(2, 0)\n(2, 1)\n(2, 2)\n```\n\n**生活类比**：多重循环像钟表的指针。分针（内层）转一整圈，时针（外层）才走一格。i 是时针，j 是分针。\n\n### 执行流程\n\n1. 外层 i=0，进入内层，j 从 0 到 2 走完。\n2. 外层 i=1，内层 j 又从 0 到 2 走完。\n3. 外层 i=2，内层 j 再从 0 到 2 走完。\n4. 结束。\n\n**总次数 = 外层次数 × 内层次数**。上面是 3×3=9 次。\n\n## 7.2 打印图形\n\n### 直角三角形\n\n```python\nfor i in range(1, 6):      # i = 1 到 5\n    print("*" * i)          # 打印 i 个星号\n```\n\n输出：\n```\n*\n**\n***\n****\n*****\n```\n\n**解释**：`"*" * i` 是字符串重复，i=1 打印 1 个星号，i=5 打印 5 个。\n\n### 矩形\n\n```python\nfor i in range(3):          # 3 行\n    for j in range(5):      # 每行 5 列\n        print("*", end="") # end="" 不换行\n    print()                 # 一行结束换行\n```\n\n输出：\n```\n*****\n*****\n*****\n```\n\n**关键点**：`print()` 默认每次输出后换行。用 `end=""` 让它不换行，一行打完再用空 `print()` 换行。\n\n### 九九乘法表\n\n```python\nfor i in range(1, 10):              # 行：1 到 9\n    for j in range(1, i + 1):       # 列：1 到 i\n        print(f"{j}×{i}={j*i}", end="\\t")\n    print()\n```\n\n**逐行解释**：\n- 外层 i 控制行，从 1 到 9。\n- 内层 j 控制列，从 1 到 i（第 i 行有 i 个式子）。\n- `\\t` 是制表符，让列对齐。\n- 每行结束 `print()` 换行。\n\n## 7.3 冒泡排序\n\n冒泡排序是经典的排序算法，用**双重循环**实现。\n\n### 原理\n\n像水里的气泡，大的先冒上来（或小的先沉下去）。每次比较相邻两个元素，顺序错就交换，一轮下来最大（或最小）的就"冒"到最后。\n\n**生活类比**：排队按身高。从头到尾两两比较，矮的站前面高的站后面，一轮比完最高的肯定到了最后。再比一轮，第二高的到了倒数第二……重复 n 轮就排好了。\n\n### 代码\n\n```python\narr = [3, 1, 4, 1, 5, 9, 2, 6]\nn = len(arr)\nfor i in range(n):                  # 外层：共 n 轮\n    for j in range(n - i - 1):      # 内层：每轮少比一个\n        if arr[j] > arr[j + 1]:     # 相邻比，前大于后\n            arr[j], arr[j + 1] = arr[j + 1], arr[j]   # 交换\nprint(arr)    # [1, 1, 2, 3, 4, 5, 6, 9]\n```\n\n**逐行解释**：\n- `for i in range(n)`：外层跑 n 轮。\n- `for j in range(n - i - 1)`：内层比较次数。每过一轮，最后一个已经排好，少比一个，所以是 `n - i - 1`。\n- `if arr[j] > arr[j+1]`：相邻两个比，前大于后说明顺序错了。\n- `arr[j], arr[j+1] = arr[j+1], arr[j]`：Python 的优雅交换，不用临时变量。\n\n### 交换的原理\n\n```python\na, b = b, a    # 等价于：先算右边的 (b, a) 元组，再分别赋给左边的 a, b\n```\n\n**注意**：写成 `a = b; b = a` 是错的！第一步 a 变成 b 的值后，b = a 时 a 已经是新的，原 a 丢了。\n\n## 7.4 查找与统计\n\n### 找二维最大值\n\n```python\nmatrix = [\n    [1, 2, 3],\n    [4, 5, 6],\n    [7, 8, 9]\n]\nmax_val = matrix[0][0]\nfor i in range(len(matrix)):\n    for j in range(len(matrix[i])):\n        if matrix[i][j] > max_val:\n            max_val = matrix[i][j]\nprint(max_val)    # 9\n```\n\n## 常见错误\n\n### 错误 1：内外层用同一变量名\n\n```python\nfor i in range(3):\n    for i in range(3):    # 错！内外都用 i，内层覆盖外层\n        print(i)\n```\n\n修正：内外层用不同变量名，习惯上外层 i、内层 j。\n\n```python\nfor i in range(3):\n    for j in range(3):\n        print(i, j)\n```\n\n### 错误 2：内层范围没递减（冒泡）\n\n```python\nfor i in range(n):\n    for j in range(n - 1):    # 每轮都比 n-1 次，能跑但多余\n        ...\n```\n\n不算错，但效率低。正确写 `n - i - 1`。\n\n### 错误 3：忘了 print 换行\n\n```python\nfor i in range(3):\n    for j in range(3):\n        print("*", end="")\n    # 忘了 print()，所有星号挤一行\n```\n\n修正：每行结束加 `print()` 换行。\n\n```python\nfor i in range(3):\n    for j in range(3):\n        print("*", end="")\n    print()\n```\n\n## 本章要点\n\n1. **多重循环是循环套循环**——像钟表，分针转一圈时针走一格。\n2. 总次数 = 外层次数 × 内层次数。\n3. 打印图形：外层控制行，内层控制列，`end=""` 不换行，`print()` 换行。\n4. 冒泡排序：外层 n 轮，内层 `n - i - 1` 次，相邻比较交换。\n5. Python 交换：`a, b = b, a`，优雅且不会丢值。\n6. 内外层循环变量**不要同名**。\n\n## 动手试试\n\n1. 打印一个 n×n 的正方形星号图案。\n2. 自己实现冒泡排序，输入 n 个数，输出排序后的列表。\n3. 想一想：九九乘法表为什么内层是 `range(1, i+1)` 而不是 `range(1, 10)`？', '冒泡排序'),
    ('第 8 章：递归', '# 第 8 章：递归\n\n这一章学一个有点"烧脑"但很神奇的东西——**递归**。它是一种特殊的解题思路：**函数自己调用自己**。听起来奇怪，但很多问题用递归来想会特别简单。\n\n## 8.1 什么是递归\n\n### 生活类比\n\n**递归就像站在两面镜子中间**——你看到镜子里有镜子，镜子的镜子里又有镜子，无限重复。\n\n再举一个：你要查字典里"递归"这个词，字典说"递归：参见\'递归\'"——这就是递归（虽然是个笑话）。\n\n正经的例子：**排队数人数**。你问前面的人"你排第几？"，他再问前面的人"你排第几？"……一直问到第一个人说"我排第 1"。然后每个人在前面人的答案上加 1，就是自己的名次。**问题被分解成更小的同类问题**，这就是递归。\n\n### 递归的两个必备\n\n递归函数必须有两部分，缺一不可：\n\n1. **递归出口（base case）**：停止条件，不再调用自己。否则会无限调用，电脑崩溃。\n2. **递归步骤（recursive case）**：把问题变小一步，调用自己。\n\n```python\ndef f(问题):\n    if 是最小情况:        # 递归出口\n        return 直接答案\n    else:                # 递归步骤\n        return f(更小的问题)  # 调用自己，问题缩小\n```\n\n**生活类比**：递归像俄罗斯套娃——打开一个娃娃，里面有个更小的娃娃，再打开……直到最里面那个最小的娃娃（出口），不能再开了。\n\n## 8.2 阶乘\n\n### 什么是阶乘\n\nn 的阶乘写作 `n!`，等于 `n × (n-1) × ... × 2 × 1`。比如 `5! = 5×4×3×2×1 = 120`。规定 `0! = 1`。\n\n### 递归思路\n\n观察：`5! = 5 × 4!`，而 `4! = 4 × 3!`……也就是 **`n! = n × (n-1)!`**。这就是递归！\n\n- 出口：`n = 0` 时返回 1（`0! = 1`）。\n- 步骤：`n! = n × (n-1)!`，调用自己算 `(n-1)!`。\n\n### 代码\n\n```python\ndef factorial(n):\n    if n <= 1:                  # 递归出口\n        return 1\n    return n * factorial(n - 1) # 递归步骤\n\nprint(factorial(5))    # 120\n```\n\n**执行过程**（算 factorial(5)）：\n1. `factorial(5)` = 5 × factorial(4)\n2. `factorial(4)` = 4 × factorial(3)\n3. `factorial(3)` = 3 × factorial(2)\n4. `factorial(2)` = 2 × factorial(1)\n5. `factorial(1)` 命中出口，返回 1\n6. 往回算：2×1=2 → 3×2=6 → 4×6=24 → 5×24=120\n\n**生活类比**：像你问老板"我工资多少"，老板说"比下属多1000"，你问下属，下属问他的下属……问到最底层员工说"我3000"，然后一层层加上来。\n\n## 8.3 斐波那契数列\n\n### 定义\n\n斐波那契数列：1, 1, 2, 3, 5, 8, 13, 21, ... 每个数是前两个数之和。\n\n- `fib(1) = 1`，`fib(2) = 1`（出口）\n- `fib(n) = fib(n-1) + fib(n-2)`（步骤）\n\n### 代码\n\n```python\ndef fib(n):\n    if n <= 2:                      # 递归出口\n        return 1\n    return fib(n - 1) + fib(n - 2)  # 递归步骤\n\nprint(fib(7))    # 13\n```\n\n**注意**：这个递归效率很低，因为会**重复计算**（算 fib(5) 要算 fib(4) 和 fib(3)，算 fib(4) 又算 fib(3)……fib(3) 算了多次）。n 大时非常慢。初学理解递归用它没问题，实际应用要优化（用记忆化或循环）。\n\n## 8.4 递归 vs 循环\n\n任何递归都能用循环改写。比如阶乘用循环：\n\n```python\ndef factorial_loop(n):\n    result = 1\n    for i in range(1, n + 1):\n        result *= i\n    return result\n```\n\n**什么时候用递归**：\n- 问题本身是递归定义的（如阶乘、树结构）。\n- 用递归思路更清晰、代码更短。\n\n**什么时候用循环**：\n- 简单重复操作。\n- 递归太慢或层数太深（会栈溢出）。\n\n## 8.5 递归的"栈"\n\n每次函数调用，电脑都会在内存里"压栈"——记住当前调用状态，等被调用的返回后再继续。递归层数太深，栈会满，叫**栈溢出**（Stack Overflow）。\n\n```python\ndef f(n):\n    return f(n - 1)    # 没有出口！\nf(1)    # 无限递归，最终 RecursionError\n```\n\n**生活类比**：栈像一摞盘子。你每调用一次就放一个盘子上去，返回一次就拿走一个。递归太深，盘子摞太高就塌了。\n\n## 常见错误\n\n### 错误 1：忘了递归出口\n\n```python\ndef factorial(n):\n    return n * factorial(n - 1)    # 没出口，无限递归\n```\n\n修正：加出口。\n\n```python\ndef factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\n```\n\n### 错误 2：问题没缩小\n\n```python\ndef f(n):\n    if n == 0:\n        return 0\n    return f(n)    # 错！还是 f(n)，没缩小\n```\n\n修正：每次调用要让 n 变小。\n\n```python\ndef f(n):\n    if n == 0:\n        return 0\n    return f(n - 1)\n```\n\n### 错误 3：出口条件写错\n\n```python\ndef factorial(n):\n    if n == 1:          # 只考虑 n=1，n=0 时无限递归\n        return 1\n    return n * factorial(n - 1)\nprint(factorial(0))    # 无限递归\n```\n\n修正：出口要覆盖所有基本情况。\n\n```python\nif n <= 1:\n    return 1\n```\n\n## 本章要点\n\n1. **递归是函数调用自己**——像俄罗斯套娃，或站在两面镜子中间。\n2. 必须有**递归出口**（停止）和**递归步骤**（问题缩小），缺一不可。\n3. 阶乘：`n! = n × (n-1)!`，出口 `0! = 1`。\n4. 斐波那契：`fib(n) = fib(n-1) + fib(n-2)`，出口 `fib(1)=fib(2)=1`。\n5. 递归层数太深会**栈溢出**。\n6. 任何递归都能用循环改写，递归胜在思路清晰。\n\n## 动手试试\n\n1. 用递归求 1+2+...+n 的和（提示：`sum(n) = n + sum(n-1)`，出口 `sum(1)=1`）。\n2. 用递归打印 1 到 n。\n3. 想一想：为什么递归算斐波那契很慢？因为重复计算，你能画图看看哪些被算了多次吗？', '计算阶乘'),
    ('第 9 章：字典与集合', '# 第 9 章：字典与集合\n\n前面学的列表用**编号（索引）**找东西。但有时我们想用**名字**找东西——比如用"小明"找他的成绩。Python 的**字典**就是干这个的。**集合**则是装不重复东西的容器。\n\n## 9.1 字典 dict\n\n### 生活类比\n\n字典（dict）就像**真正的字典**——用"词条"查"释义"。或者像**通讯录**：用人名查电话号码。你说"小明"，它给你 138xxxx。这种"用键查值"的结构，就是字典。\n\n```\n通讯录:\n  "小明" -> 13800000001\n  "小红" -> 13800000002\n```\n\n### 创建字典\n\n用**花括号 `{}`**，里面是 `键: 值` 对，用逗号隔开：\n\n```python\nscores = {"小明": 90, "小红": 85, "小刚": 78}\nphone = {}                      # 空字典\nphone["小明"] = "138xxx"        # 添加\n```\n\n### 访问与修改\n\n```python\nscores = {"小明": 90, "小红": 85}\nprint(scores["小明"])       # 90（用键查值）\nscores["小明"] = 95         # 修改\nscores["小刚"] = 78         # 添加新键值对\ndel scores["小红"]           # 删除\nprint(scores)                # {\'小明\': 95, \'小刚\': 78}\n```\n\n### 安全访问：get\n\n直接用 `[]` 访问不存在的键会报错。用 `get` 更安全，找不到返回 None（或指定默认值）：\n\n```python\nprint(scores.get("小王"))          # None（不存在不报错）\nprint(scores.get("小王", 0))       # 0（指定默认值）\n```\n\n### 遍历字典\n\n```python\nscores = {"小明": 90, "小红": 85}\n# 遍历键\nfor name in scores:\n    print(name)\n# 遍历键值对\nfor name, score in scores.items():\n    print(f"{name}: {score}")\n```\n\n**逐行解释**：\n- `for name in scores` 默认遍历键。\n- `scores.items()` 返回所有 (键, 值) 对，每次循环 name 取键、score 取值。\n\n### 字典的特点\n\n1. **键唯一**：同一个键只能有一个值，后赋的覆盖前面的。\n2. **键必须是不可变类型**：字符串、数字、元组可以，列表不行。\n3. **查找极快**：无论字典有多大，查找都几乎瞬间（O(1) 复杂度）。\n\n## 9.2 集合 set\n\n### 生活类比\n\n集合像**一筐球**——球没有编号，且**不重复**。你往里扔两个一样的球，它只留一个。集合专门用来**去重**和**快速判断有没有**。\n\n### 创建集合\n\n```python\ns = {1, 2, 3, 3}      # 字面量，重复的 3 只留一个\nprint(s)                # {1, 2, 3}\ns = set([1, 2, 2, 3]) # 从列表创建\n```\n\n### 常用操作\n\n```python\ns = {1, 2, 3}\ns.add(4)           # 添加\ns.discard(2)       # 删除（不存在不报错）\nprint(1 in s)      # True（判断是否存在，超快）\nprint(len(s))      # 3\n```\n\n### 集合运算\n\n集合支持数学里的运算：\n\n```python\na = {1, 2, 3}\nb = {2, 3, 4}\nprint(a & b)    # 交集 {2, 3}（两个都有的）\nprint(a | b)    # 并集 {1, 2, 3, 4}（所有）\nprint(a - b)    # 差集 {1}（a 有 b 没有）\n```\n\n### 用途：去重\n\n列表去重最快的方法：\n\n```python\narr = [1, 2, 2, 3, 3, 3, 4]\nunique = list(set(arr))\nprint(unique)    # [1, 2, 3, 4]\n```\n\n## 9.3 综合例子：词频统计\n\n统计一段文字里每个字出现几次：\n\n```python\ntext = "hello world hello python"\nwords = text.split()\ncount = {}\nfor w in words:\n    count[w] = count.get(w, 0) + 1\nprint(count)\n# {\'hello\': 2, \'world\': 1, \'python\': 1}\n```\n\n**逐行解释**：\n- `split()` 把字符串切成单词列表。\n- `count.get(w, 0)`：如果 w 已在字典里，取它的计数；否则取 0。\n- `+1`：次数加 1。\n- 存回字典 `count[w]`。\n\n## 常见错误\n\n### 错误 1：访问不存在的键\n\n```python\nd = {"a": 1}\nprint(d["b"])    # 错！KeyError\n```\n\n修正：用 get 或先判断。\n\n```python\nprint(d.get("b"))            # None\nif "b" in d:\n    print(d["b"])\n```\n\n### 错误 2：用列表当键\n\n```python\nd = {}\nd[[1, 2]] = "x"    # 错！列表不可变，不能当键\n```\n\n修正：键必须不可变，用元组。\n\n```python\nd[(1, 2)] = "x"    # 对\n```\n\n### 错误 3：集合用 {} 创建空集\n\n```python\ns = {}          # 错！这是空字典不是空集合\ns.add(1)        # 报错，字典没 add 方法\n```\n\n修正：空集合用 `set()`。\n\n```python\ns = set()\ns.add(1)\n```\n\n## 本章要点\n\n1. **字典是用键查值的容器**——像通讯录，用名字查号码。\n2. 字典用 `{键: 值}` 创建，`d[键]` 访问，`get` 安全访问。\n3. **键唯一、不可变**；查找极快（O(1)）。\n4. **集合是不重复元素的容器**——像一筐球，自动去重。\n5. 空集合用 `set()`，`{}` 是空字典。\n6. 集合支持 `&`（交）、`|`（并）、`-`（差）运算；`in` 判断超快。\n\n## 动手试试\n\n1. 输入若干同学姓名和成绩（姓名作键），输入"end"结束，再输入姓名查成绩。\n2. 给一个列表，去重后输出（用集合）。\n3. 想一想：为什么字典和集合查找比列表快？（提示：列表要挨个找，字典用"哈希"直接定位。）', None),
    ('第 10 章：文件操作', '# 第 10 章：文件操作\n\n到现在，你写的程序运行完数据就没了——变量存在内存里，程序一关就消失。要让数据**永久保存**，就要写到**文件**里。这一章学怎么用 Python 读写文件。\n\n## 10.1 为什么需要文件\n\n### 内存 vs 硬盘\n\n- **内存**：程序运行时存数据的地方，**快但断电就没**。\n- **硬盘**：永久存储，**关机也不丢**。\n\n你的变量在内存里，程序结束就没了。要把成绩单、用户记录保存下来，必须写进硬盘上的**文件**。\n\n**生活类比**：内存像你的草稿纸，下课就擦了；文件像写在笔记本上，明天还能翻出来看。\n\n## 10.2 打开与关闭文件\n\n### 基本步骤\n\n操作文件三步走：\n1. **打开**文件：`open(文件名, 模式)`。\n2. **读/写**：`f.read()` / `f.write(...)`。\n3. **关闭**文件：`f.close()`。\n\n```python\nf = open("test.txt", "w")    # "w" 是写模式\nf.write("Hello, File!")\nf.close()\n```\n\n**模式**：\n- `"r"`：read，只读（文件必须存在）。\n- `"w"`：write，写入（**覆盖**原内容；文件不存在则创建）。\n- `"a"`：append，追加（在末尾加，不覆盖）。\n\n### 为什么必须关闭\n\n不关闭文件，数据可能**没真正写进硬盘**（还在缓冲区）。`close()` 强制把数据刷进硬盘。但**用 with 更省心**（见 10.3）。\n\n## 10.3 with 语句（推荐）\n\n手动 open/close 容易忘关。Python 的 `with` 语句**自动关闭**文件，哪怕中间出错：\n\n```python\nwith open("test.txt", "w") as f:\n    f.write("Hello, File!")\n# 离开 with 块自动关闭，不用 f.close()\n```\n\n**生活类比**：with 像自动门——你进去它开，你出来它自动关。不用担心忘关门。\n\n**强烈建议**：永远用 `with` 操作文件，不要手动 close。\n\n## 10.4 写文件\n\n### 写字符串\n\n```python\nwith open("output.txt", "w") as f:\n    f.write("第一行\\n")\n    f.write("第二行\\n")\n```\n\n**注意**：`write` 不会自动换行，要自己加 `\\n`。`print` 默认换行，`write` 不换行。\n\n### 写多行\n\n```python\nlines = ["apple", "banana", "cherry"]\nwith open("fruits.txt", "w") as f:\n    for line in lines:\n        f.write(line + "\\n")\n```\n\n或用 `writelines`：\n\n```python\nwith open("fruits.txt", "w") as f:\n    f.writelines([l + "\\n" for l in lines])\n```\n\n### 追加写\n\n用 `"a"` 模式，在文件末尾追加，不覆盖：\n\n```python\nwith open("log.txt", "a") as f:\n    f.write("2026-10-03 程序启动\\n")\n```\n\n每次运行这行，log.txt 末尾就多一行。如果是 `"w"`，每次都覆盖。\n\n## 10.5 读文件\n\n### 一次读完\n\n```python\nwith open("input.txt", "r") as f:\n    content = f.read()    # 整个文件读成一个字符串\nprint(content)\n```\n\n### 逐行读\n\n```python\nwith open("input.txt") as f:\n    for line in f:            # f 本身可迭代，每次给一行\n        line = line.strip()   # 去掉行末的换行符\n        print(line)\n```\n\n**逐行解释**：\n- `for line in f` 每次取一行（包含行末的 `\\n`）。\n- `.strip()` 去掉首尾空白和换行符。\n- 这样处理大文件不占内存（一次只读一行）。\n\n### readlines\n\n```python\nwith open("input.txt") as f:\n    lines = f.readlines()    # 读成列表，每个元素一行\nprint(lines)    # [\'第一行\\n\', \'第二行\\n\', ...]\n```\n\n每个元素**带换行符**，用时要 `strip`。\n\n## 10.6 综合例子：学生成绩\n\n写入 3 个学生成绩，再读出来求平均：\n\n```python\n# 写\nwith open("scores.txt", "w") as f:\n    f.write("小明 90\\n")\n    f.write("小红 85\\n")\n    f.write("小刚 78\\n")\n\n# 读\ntotal = 0\ncount = 0\nwith open("scores.txt") as f:\n    for line in f:\n        name, score = line.split()\n        total += int(score)\n        count += 1\nprint(f"平均分：{total / count:.2f}")\n```\n\n**逐行解释**：\n- 写：每个学生一行，姓名和成绩用空格隔开。\n- 读：`line.split()` 把一行切成 `[姓名, 成绩]` 两个部分。\n- 把成绩转 int 加到 total。\n- 最后算平均。\n\n## 常见错误\n\n### 错误 1：忘了关或忘 with\n\n```python\nf = open("a.txt", "w")\nf.write("data")\n# 忘了 f.close()，数据可能没写入\n```\n\n修正：用 with。\n\n```python\nwith open("a.txt", "w") as f:\n    f.write("data")\n```\n\n### 错误 2：读模式打开不存在的文件\n\n```python\nwith open("no_exist.txt", "r") as f:    # 错！文件不存在\n    content = f.read()\n```\n\n修正：r 模式要求文件存在。先创建文件，或检查。\n\n### 错误 3：忘 strip 换行符\n\n```python\nwith open("a.txt") as f:\n    for line in f:\n        print(line)    # 多出一个空行，因为 line 末尾有 \\n，print 又加 \\n\n```\n\n修正：strip 掉换行符。\n\n```python\nprint(line.strip())\n```\n\n## 本章要点\n\n1. **文件让数据永久保存**——内存是草稿纸，文件是笔记本。\n2. 三步走：open → read/write → close。\n3. **永远用 `with`** 操作文件，自动关闭。\n4. 模式：`"r"` 读、`"w"` 覆盖写、`"a"` 追加。\n5. `read()` 全读、`for line in f` 逐行读、`readlines()` 读成列表。\n6. 读出的行**带换行符**，用 `.strip()` 去掉；`write` 不自动换行，要加 `\\n`。\n\n## 动手试试\n\n1. 写一个程序，把 1 到 100 的平方数写进文件，每行一个。\n2. 读一个文件，统计它有多少行、多少字符。\n3. 想一想：为什么 `"w"` 模式会清空原文件？如果要保留原内容并加新内容，该用哪个模式？', None),
    ('第 11 章：异常处理', '# 第 11 章：异常处理\n\n你写过这么多程序，肯定遇到过报错——比如输入不是数字、除以零。报错会让程序**立刻崩溃**。这一章学怎么**优雅地处理错误**，让程序不会因为一个小错就整个崩掉。\n\n## 11.1 什么是异常\n\n### 异常是什么\n\n**异常**就是程序运行时发生的错误。比如：\n\n```python\nn = int(input())    # 输入 "abc"\n# ValueError: invalid literal for int() with base 10: \'abc\'\n```\n\n```python\nprint(10 / 0)\n# ZeroDivisionError: division by zero\n```\n\n这些错误叫**异常**。如果不处理，程序会**立即停止**并打印一长串错误信息。用户看到这个会一头雾水。\n\n**生活类比**：异常像做菜时发现没盐了。你不处理，菜就做不下去（程序崩）；你可以选择用酱油代替（处理异常），菜还能上桌。\n\n## 11.2 try-except\n\n### 基本语法\n\n```python\ntry:\n    可能出错的代码\nexcept:\n    出错时执行的代码\n```\n\n意思是"**试着**执行 try 里的代码，**如果**出错就执行 except 里的"。\n\n```python\ntry:\n    n = int(input("请输入整数："))\n    print(10 / n)\nexcept:\n    print("输入有问题")\n```\n\n- 如果输入合法（如 2），打印 5.0。\n- 如果输入"abc"或 0，不崩溃，打印"输入有问题"。\n\n### 捕获具体异常\n\n裸 `except` 会捕获**所有**错误，不建议。最好捕获**具体的异常类型**：\n\n```python\ntry:\n    n = int(input())\n    print(10 / n)\nexcept ValueError:\n    print("输入不是整数")\nexcept ZeroDivisionError:\n    print("不能除以零")\n```\n\n**逐行解释**：\n- 输入"abc"：`int("abc")` 抛 ValueError，跳到 `except ValueError`，打印"输入不是整数"。\n- 输入 0：`int("0")` 成功转成 0，但 `10/0` 抛 ZeroDivisionError，跳到对应 except，打印"不能除以零"。\n- 输入 2：正常执行，打印 5.0。\n\n### 常见异常类型\n\n| 异常 | 何时发生 |\n|------|----------|\n| ValueError | 值转换错误，如 `int("abc")` |\n| TypeError | 类型不对，如 `"a" + 1` |\n| IndexError | 列表索引越界 |\n| KeyError | 字典键不存在 |\n| ZeroDivisionError | 除以零 |\n| FileNotFoundError | 文件不存在 |\n\n## 11.3 else 和 finally\n\n### else：没出错时执行\n\n```python\ntry:\n    n = int(input())\nexcept ValueError:\n    print("输入非法")\nelse:\n    print(f"你输入了 {n}")    # 没异常才执行\n```\n\n### finally：无论如何都执行\n\n```python\ntry:\n    f = open("data.txt")\n    content = f.read()\nexcept FileNotFoundError:\n    print("文件不存在")\nfinally:\n    f.close()    # 无论是否异常都关闭\n```\n\n**`finally` 用于资源清理**——比如关文件、断开连接，确保一定执行。\n\n**生活类比**：finally 像出门前一定锁门——不管你今天顺不顺利，门都要锁。\n\n### 完整结构\n\n```python\ntry:\n    # 可能出错的代码\nexcept ValueError as e:\n    # 捕获 ValueError，e 是错误详情\nexcept (TypeError, IndexError):\n    # 捕获多种异常\nelse:\n    # 没异常时执行\nfinally:\n    # 无论如何都执行\n```\n\n## 11.4 主动抛异常：raise\n\n有时你想**自己**抛异常，用 `raise`：\n\n```python\ndef set_age(age):\n    if age < 0:\n        raise ValueError("年龄不能为负")\n    return age\n\nprint(set_age(-5))    # 抛 ValueError: 年龄不能为负\n```\n\n这让你能在函数里**检查参数合法性**，不合法就报错。\n\n## 11.5 综合例子：安全的除法\n\n```python\ntry:\n    a = int(input("被除数："))\n    b = int(input("除数："))\n    result = a / b\nexcept ValueError:\n    print("请输入整数")\nexcept ZeroDivisionError:\n    print("除数不能为 0")\nelse:\n    print(f"结果：{result:.2f}")\nfinally:\n    print("计算结束")\n```\n\n**运行示例**：\n- 输入 10 和 2 → "结果：5.00" "计算结束"\n- 输入 10 和 0 → "除数不能为 0" "计算结束"\n- 输入 abc → "请输入整数" "计算结束"\n\n无论哪种情况，"计算结束"都会打印（finally 的作用）。\n\n## 常见错误\n\n### 错误 1：裸 except 吞所有错误\n\n```python\ntry:\n    x = 1 / 0\n    y = some_undefined_var\nexcept:\n    print("出错了")    # 所有错误都吞，bug 难发现\n```\n\n修正：捕获具体异常。\n\n```python\nexcept ZeroDivisionError:\n    print("除零错误")\n```\n\n### 错误 2：捕获范围太大\n\n```python\ntry:\n    a = int(input())\n    b = int(input())\n    print(a / b)\n    print(arr[100])    # 这行也可能越界，但和输入无关\nexcept ValueError:\n    ...\n```\n\n修正：try 只包可能出错的最小代码段。\n\n```python\ntry:\n    a = int(input())\n    b = int(input())\nexcept ValueError:\n    ...\nprint(a / b)    # 放外面\n```\n\n### 错误 3：except 里访问未定义变量\n\n```python\ntry:\n    n = int(input())\nexcept ValueError:\n    print(n)    # 错！n 没赋值就出错了，n 不存在\n```\n\n修正：except 里不要用 try 里失败才定义的变量。\n\n## 本章要点\n\n1. **异常是运行时错误**——像做菜发现没盐，不处理就崩。\n2. `try-except` 捕获异常，让程序优雅地处理错误。\n3. **捕获具体异常类型**，不要裸 except。\n4. `else` 没异常时执行，`finally` 无论如何都执行（用于清理）。\n5. `raise` 主动抛异常，用于参数检查。\n6. 常见异常：ValueError、TypeError、IndexError、KeyError、ZeroDivisionError、FileNotFoundError。\n\n## 动手试试\n\n1. 写一个程序，输入两个数做除法，处理除零和非法输入。\n2. 写一个函数 `divide(a, b)`，b 为 0 时 raise ValueError，调用时用 try 捕获。\n3. 想一想：为什么"裸 except"不好？因为它会吞掉你没预料到的 bug，让调试变难。', None),
    ('第 12 章：二维数组与矩阵', '# 第 12 章：二维数组与矩阵\n\n前面学的列表是"一排抽屉"——一维的。但有些数据是"一格一格排成行列"的，比如棋盘、Excel 表格、图片像素。这种**有行有列**的数据结构，叫**二维数组**或**矩阵**。\n\n## 12.1 什么是二维数组\n\n### 生活类比\n\n二维数组像**电影院的座位**——有排（行）有列（座）。你要找某个座位，得说"第 3 排第 5 座"。在程序里就是 `座位[2][4]`（从 0 开始）。\n\n```\n        列0  列1  列2  列3\n行0:    [1,  2,  3,  4]\n行1:    [5,  6,  7,  8]\n行2:    [9, 10, 11, 12]\n```\n\n### 本质：列表的列表\n\nPython 没有专门的"二维数组"类型，用**列表里装列表**实现：\n\n```python\nmatrix = [\n    [1, 2, 3, 4],\n    [5, 6, 7, 8],\n    [9, 10, 11, 12]\n]\n```\n\n`matrix` 是一个列表，有 3 个元素，每个元素又是一个列表（一行）。`matrix[0]` 是第 0 行 `[1,2,3,4]`，`matrix[0][1]` 是第 0 行第 1 列 = 2。\n\n**记忆**：`matrix[行][列]`——**先行后列**，像说"第几排第几座"。\n\n## 12.2 创建二维列表\n\n### 方法一：直接写\n\n```python\nmatrix = [\n    [1, 2, 3],\n    [4, 5, 6],\n    [7, 8, 9]\n]\n```\n\n### 方法二：列表推导式（推荐）\n\n创建一个 m 行 n 列全 0 的矩阵：\n\n```python\nm, n = 3, 4\nmatrix = [[0] * n for _ in range(m)]\nprint(matrix)    # [[0,0,0,0], [0,0,0,0], [0,0,0,0]]\n```\n\n**逐行解释**：\n- `[0] * n` 创建一行 n 个 0：`[0,0,0,0]`。\n- `for _ in range(m)` 重复 m 次，每次造一行。\n- `[[0]*n for _ in range(m)]` 是列表推导式，生成 m 行。\n\n### 错误方法：`[[0]*n]*m`\n\n```python\nmatrix = [[0] * n] * m    # 错！浅拷贝\nmatrix[0][0] = 1\nprint(matrix)    # [[1,0,0,0], [1,0,0,0], [1,0,0,0]] 全改了！\n```\n\n**原因**：`* m` 把**同一个**列表引用复制了 m 次，改一行等于改所有行。必须用列表推导式，每行是独立的新列表。\n\n### 方法三：从输入读\n\n输入格式：第 1 行 m n（行数列数），后面 m 行每行 n 个数。\n\n```python\nm, n = map(int, input().split())\nmatrix = []\nfor _ in range(m):\n    row = list(map(int, input().split()))\n    matrix.append(row)\n# 一行写法：\nmatrix = [list(map(int, input().split())) for _ in range(m)]\n```\n\n## 12.3 访问与遍历\n\n### 访问单个元素\n\n```python\nmatrix = [[1,2,3],[4,5,6],[7,8,9]]\nprint(matrix[0][0])    # 1（第 0 行第 0 列）\nprint(matrix[1][2])    # 6（第 1 行第 2 列）\nprint(matrix[2][1])    # 8（第 2 行第 1 列）\n```\n\n### 按行遍历\n\n```python\nfor i in range(m):              # 外层遍历行\n    for j in range(n):          # 内层遍历列\n        print(matrix[i][j], end=" ")\n    print()                      # 一行结束换行\n```\n\n**逐行解释**：\n- 外层 i 控制行，从 0 到 m-1。\n- 内层 j 控制列，从 0 到 n-1。\n- `end=" "` 让同行元素用空格隔开。\n- `print()` 一行打完换行。\n\n### 按列遍历（转置思路）\n\n按列遍历就是把行列的循环**对调**：\n\n```python\nfor j in range(n):              # 外层遍历列\n    for i in range(m):          # 内层遍历行\n        print(matrix[i][j], end=" ")\n    print()\n```\n\n这就是**矩阵转置**的核心——行列交换。\n\n## 12.4 矩阵转置\n\n转置：原来的行变列、列变行。第 i 行第 j 列变成第 j 行第 i 列。\n\n```python\nmatrix = [\n    [1, 2, 3],\n    [4, 5, 6]\n]    # 2 行 3 列\n# 转置后是 3 行 2 列：[[1,4],[2,5],[3,6]]\n\nm, n = len(matrix), len(matrix[0])\nresult = [[0] * m for _ in range(n)]    # 新矩阵是 n 行 m 列\nfor i in range(m):\n    for j in range(n):\n        result[j][i] = matrix[i][j]    # 行列交换\nprint(result)\n```\n\n**逐行解释**：\n- 原矩阵 m 行 n 列，转置后 n 行 m 列。\n- 新建 `result` 是 n 行 m 列。\n- `result[j][i] = matrix[i][j]`：把原 (i,j) 位置的值放到新 (j,i)。\n\n## 12.5 常见操作\n\n### 求每行和\n\n```python\nfor i in range(m):\n    row_sum = sum(matrix[i])\n    print(f"第{i}行和：{row_sum}")\n```\n\n### 求对角线\n\n主对角线（左上到右下）元素：`matrix[i][i]`：\n\n```python\nfor i in range(m):\n    print(matrix[i][i])\n```\n\n副对角线（右上到左下）：`matrix[i][n-1-i]`：\n\n```python\nfor i in range(m):\n    print(matrix[i][n - 1 - i])\n```\n\n### 找最大值位置\n\n```python\nmax_val = matrix[0][0]\nmax_pos = (0, 0)\nfor i in range(m):\n    for j in range(n):\n        if matrix[i][j] > max_val:\n            max_val = matrix[i][j]\n            max_pos = (i, j)\nprint(f"最大值 {max_val} 在 {max_pos}")\n```\n\n## 常见错误\n\n### 错误 1：用 `[[0]*n]*m` 创建\n\n```python\nmatrix = [[0] * 3] * 3\nmatrix[0][0] = 1\nprint(matrix)    # [[1,0,0],[1,0,0],[1,0,0]] 全乱了\n```\n\n修正：用列表推导式。\n\n```python\nmatrix = [[0] * 3 for _ in range(3)]\nmatrix[0][0] = 1    # 只改第一行\n```\n\n### 错误 2：行列索引搞反\n\n```python\n# matrix 是 3 行 4 列\nprint(matrix[4][0])    # 错！只有 3 行，索引到 2\n```\n\n修正：先行后列，行范围 0 到 m-1，列范围 0 到 n-1。\n\n```python\nprint(matrix[2][3])    # 第 2 行第 3 列\n```\n\n### 错误 3：不规则行\n\n```python\nmatrix = [[1, 2], [3, 4, 5], [6]]    # 行长不一\nprint(matrix[1][2])    # 5\nprint(matrix[2][1])    # IndexError，第 2 行只有 1 个元素\n```\n\n修正：用 `len(matrix[i])` 取每行实际长度。\n\n```python\nfor j in range(len(matrix[i])):\n    ...\n```\n\n## 本章要点\n\n1. **二维数组是"列表的列表"**——像电影院座位，有行有列。\n2. 访问用 `matrix[行][列]`，**先行后列**。\n3. **创建用列表推导式** `[[0]*n for _ in range(m)]`，**不要用 `*m`**（浅拷贝）。\n4. 遍历：外层行、内层列；转置就交换行列循环。\n5. 矩阵转置：`result[j][i] = matrix[i][j]`，行列交换。\n6. 主对角线 `matrix[i][i]`，副对角线 `matrix[i][n-1-i]`。\n\n## 动手试试\n\n1. 输入一个 m×n 矩阵，输出转置后的矩阵。\n2. 输入一个方阵，求两条对角线元素之和。\n3. 想一想：为什么 `[[0]*n]*m` 会"一行变全变"？因为它复制的是同一个列表的引用，你能画图理解吗？', '矩阵转置'),
]


# ── Java 课程章节（10 章）──────────────────────────────
JAVA_LESSONS = [
    ("第 1 章：Java 入门与基本语法", """# 第 1 章：Java 入门与基本语法

## 写在前面：什么是编程？

你每天都在和"程序"打交道——手机里的游戏、微信、抖音，都是程序。**编程**就是给计算机写一份"操作说明书"，告诉它一步步该做什么。计算机本身很笨，只会严格按照你写的命令执行，但它执行得又快又准，一秒钟能做几亿次运算。

**Java** 是一门很流行的编程语言，由 Sun 公司（后被 Oracle 收购）在 1995 年推出。它的语法比较严谨，适合培养良好的编程习惯；而且"一次编写，到处运行"，写好的程序能在 Windows、Mac、Linux 上跑。很多大公司的后台系统、Android 手机 App 都是用 Java 写的。

这一章我们从最基础的"在屏幕上打印一句话"开始，逐步认识变量、输入输出。

## 1.1 第一个程序：打印 Hello, World!

按照传统，学任何一门语言的第一件事都是让计算机说一句"Hello, World!"。看下面这段代码：

```java
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

别被这些奇怪的关键字吓到，我们一行行拆解（这一段"模板代码"你暂时不用完全理解，照抄就行，但要记住每一行的作用）：

- `public class Main { ... }`：Java 规定所有代码都必须装在一个"类（class）"里，`Main` 是这个类的名字。**类名必须和文件名完全一致**，所以这段代码必须保存在 `Main.java` 文件里。`public` 表示这个类是公开的，别人可以用。
- `public static void main(String[] args) { ... }`：这是"主方法"，也就是**程序的入口**。Java 程序运行时，会自动从这里开始执行。`static` 表示不需要创建对象就能调用；`void` 表示这个方法不返回任何结果；`String[] args` 是用来接收命令行参数的（暂时用不到）。
- `System.out.println("Hello, World!");`：这是真正干活的语句，意思是"把括号里的内容打印到屏幕上，并换行"。注意结尾的**分号 `;`**——Java 的每一条语句都必须以分号结束，就像中文每句话要用句号。
- 大括号 `{ }`：用来圈定一段代码的范围，必须**成对出现**，少一个就报错。

### 为什么需要这么多"模板"？

你可能会问：Python 只要一行 `print("Hello, World!")` 就够了，Java 怎么这么啰嗦？这是因为 Java 是"面向对象"语言，它要求一切都在类里；又要求有一个明确的程序入口。这种严谨换来的是大型项目更好维护。**初学阶段，你把这段模板背下来，每次照抄即可。**

## 1.2 在屏幕上打印：System.out.println / print

`println` 是 "print line" 的缩写，打印完会**自动换行**；`print` 不换行。

```java
public class Main {
    public static void main(String[] args) {
        System.out.println("第一行");   // 打印后换行
        System.out.println("第二行");   // 在新的一行打印
        System.out.print("同一行");      // 不换行
        System.out.print("继续");        // 紧接着上一句打印
    }
}
```

运行结果：
```
第一行
第二行
同一行继续
```

### 打印变量的值

用 `+` 可以把字符串和变量拼在一起打印：

```java
int age = 12;
System.out.println("我今年 " + age + " 岁");   // 我今年 12 岁
```

这里的 `+` 当两边有一边是字符串时，表示"拼接"，把两段文字连起来。

## 1.3 变量：贴了标签的盒子

**变量**是编程里最重要的概念之一。你可以把它想象成一个**贴了标签的盒子**：盒子里装数据，标签是变量的名字。比如你有一个贴着 `age` 标签的盒子，里面装了数字 12，那么以后只要提到 `age`，计算机就知道你指的是 12。

### 为什么需要变量？

想象你在写一个计算圆面积的程序：`3.14 * 5 * 5`。如果半径要从 5 改成 10，你得改两处。如果把 5 存进一个叫 `r` 的变量，写成 `3.14 * r * r`，以后只要改 `r` 的值，公式不用动。**变量让程序更灵活、更易改。**

### Java 是"强类型"语言

和 Python 不同，Java 在声明变量时必须**指定类型**（盒子里只能装这种东西）：

```java
int x = 10;            // int = 整数，如 10、-3、0
double y = 3.14;       // double = 小数，如 3.14、-0.5
String s = "hello";    // String = 字符串（一段文字），用双引号
boolean b = true;      // boolean = 布尔，只有 true 或 false
char c = 'A';          // char = 单个字符，用单引号
```

逐行解释：
- `int x = 10;`：声明一个 `int`（整数）类型的变量 `x`，并赋值为 10。`=` 是"赋值"，把右边的内容放进左边的盒子。
- `double y = 3.14;`：`double` 表示双精度小数，比 `float` 更精确，初学统一用 `double`。
- `String s = "hello";`：注意 `String` 首字母大写！字符串内容用**双引号**。
- `boolean b = true;`：布尔类型只有两个值 `true`（真）和 `false`（假），用于条件判断。
- `char c = 'A';`：单个字符用**单引号**，和字符串的双引号区分开。

### 常见的基本类型对照

| 类型 | 装什么 | 例子 |
|------|--------|------|
| `int` | 整数 | `int a = 100;` |
| `long` | 更大的整数 | `long b = 10000000000L;`（结尾加 L） |
| `double` | 小数 | `double pi = 3.14;` |
| `boolean` | 真/假 | `boolean ok = false;` |
| `char` | 单个字符 | `char ch = '好';` |
| `String` | 一段文字 | `String name = "小明";` |

### 变量命名规则

- 只能用字母、数字、下划线 `_`、美元符 `$`，且**不能以数字开头**。
- 不能用 Java 关键字（如 `int`、`class`、`public`）。
- 建议用**有意义的名字**，如 `age`、`studentName`，而不是 `a`、`x`。
- Java 习惯"驼峰命名"：第一个单词小写，后面单词首字母大写，如 `studentName`、`maxScore`。

## 1.4 从键盘读入：Scanner

程序如果只会打印固定内容，那就太无聊了。我们希望程序能**接收用户输入**。Java 里最常用的输入工具是 `Scanner`。

你可以把 Scanner 想象成**自动取款机上的输入键盘**——你按什么键，它就读进什么数据。

```java
import java.util.Scanner;   // 第 1 步：告诉 Java 我们要用 Scanner，它在 java.util 包里

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);   // 第 2 步：创建一个 Scanner 对象，名叫 sc，连接到键盘（System.in）
        int n = sc.nextInt();                   // 第 3 步：读一个整数
        String s = sc.next();                   // 读一个字符串（读到空格为止）
        System.out.println("你输入的整数是 " + n);
        System.out.println("你输入的字符串是 " + s);
    }
}
```

逐行解释：
- `import java.util.Scanner;`：`Scanner` 不是 Java 自带就能用的，必须"导入"。`import` 就像去图书馆借书，先声明"我要用这本书"。
- `Scanner sc = new Scanner(System.in);`：`new` 表示新建一个对象。`System.in` 代表标准输入（键盘）。这行的意思是"造一个连接键盘的扫描器，取名 sc"。
- `sc.nextInt()`：让 sc 读一个整数。程序运行到这里会**停下来等你输入**，输入一个整数并回车后，这个整数就被存进变量 `n`。
- `sc.next()`：读一个字符串，遇到空格或回车就结束。

### Scanner 常用方法

| 方法 | 读取的内容 |
|------|-----------|
| `sc.nextInt()` | 整数 |
| `sc.nextDouble()` | 小数 |
| `sc.next()` | 一个字符串（空格分隔） |
| `sc.nextLine()` | 整行字符串（回车结束） |

### 完整示例：两数之和

把上面学的串起来，写一个"读两个整数并求和"的程序：

```java
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();       // 读第一个数
        int b = sc.nextInt();       // 读第二个数
        int sum = a + b;            // 计算和
        System.out.println(sum);    // 输出结果
    }
}
```

输入 `3 5`，输出 `8`。

## 1.5 运算符

变量能参与运算，运算符和数学里基本一样：

```java
int a = 10, b = 3;
System.out.println(a + b);   // 13  加
System.out.println(a - b);   // 7   减
System.out.println(a * b);   // 30  乘
System.out.println(a / b);   // 3   整数除法，只取整数部分！
System.out.println(a % b);   // 1   取余（模），10 ÷ 3 = 3 余 1
```

**重点提醒**：两个整数相除，结果还是整数，**小数部分直接丢弃**（不是四舍五入）。`10 / 3` 得 3，不是 3.333。如果想要小数结果，至少有一边要是小数：`10.0 / 3` 得 3.333...。

## 常见错误

1. **忘记分号**：`System.out.println("hi")` 少了 `;`，编译器报错 "';' expected"。每条语句结尾一定加分号。
2. **类名和文件名不一致**：文件叫 `Main.java`，但代码里写 `public class Test`，会报错。**必须一致**。
3. **忘记 import Scanner**：用了 Scanner 却没写 `import java.util.Scanner;`，报 "cannot find symbol"。
4. **大括号不配对**：多了或少了 `{` 或 `}`，报奇怪的错误。写的时候注意缩进，左括号和右括号对齐。
5. **String 用单引号、char 用双引号**：`String s = 'hi';` 错，`char c = "A";` 也错。记住：**字符串双引号、单字符单引号**。

## 本章要点

- Java 程序必须放在 `class` 里，入口是 `main` 方法，模板代码先背下来照抄。
- `System.out.println()` 打印并换行，`print()` 不换行。
- 变量 = 贴标签的盒子；Java 声明变量必须指定类型（`int`、`double`、`String`、`boolean` 等）。
- 用 `Scanner` 从键盘读输入，需要 `import`，需要 `new Scanner(System.in)`。
- 整数相除得整数，想要小数至少一边是小数。
- 每条语句以分号结束，大括号成对出现。

## 动手试试

1. 写一个程序，打印三句话："我叫小明"、"我今年 12 岁"、"我喜欢编程"。
2. 写一个程序，读入两个整数 a 和 b，输出 `a * b` 的结果。
3. 想一想：`int x = 7; int y = 2;` 那么 `x / y` 和 `x % y` 分别是多少？先猜再写程序验证。
""", "两数之和"),

    ("第 2 章：条件判断", """# 第 2 章：条件判断

## 引入：十字路口选方向

想象你走到一个十字路口，前方有红绿灯。**红灯停，绿灯行**——这就是条件判断：根据不同情况，做不同的事。程序里也经常需要"看情况办事"，比如：成绩 90 分以上评 A，60 分以下评不及格；密码正确就登录，错误就提示。这一章我们就学怎么让程序"做选择"。

## 2.1 if 语句：如果……就……

最基本的条件判断是 `if`（如果）。语法：

```java
if (条件) {
    // 条件为真时执行的语句
}
```

括号里是"条件"，条件为 `true` 时执行大括号里的语句，为 `false` 时跳过。

```java
int score = 95;
if (score >= 90) {
    System.out.println("太棒了！");
}
```

解释：`score >= 90` 是一个比较表达式，当 score 是 95 时，95 >= 90 为 true，所以会打印"太棒了！"。

### 比较运算符

| 符号 | 含义 | 例子 |
|------|------|------|
| `==` | 等于 | `a == b`（a 和 b 相等吗） |
| `!=` | 不等于 | `a != b` |
| `>` | 大于 | `a > b` |
| `<` | 小于 | `a < b` |
| `>=` | 大于等于 | `a >= b` |
| `<=` | 小于等于 | `a <= b` |

**重点**：判断相等是 `==`（两个等号），不是 `=`！`=` 是赋值，`==` 才是比较。初学最常犯的错就是这个。

## 2.2 if-else：如果……否则……

光有"如果"不够，常常还要"否则"。`else` 表示"否则"：

```java
int n = 7;
if (n % 2 == 0) {
    System.out.println("偶数");
} else {
    System.out.println("奇数");
}
```

解释：`n % 2` 是 n 除以 2 的余数。如果余数等于 0，说明能被 2 整除，是偶数；否则是奇数。这里 n=7，7%2=1，不等于 0，走 else 分支，打印"奇数"。

### 执行流程

1. 计算括号里的条件。
2. 如果为 true，执行 if 后面 `{}` 里的内容，跳过 else。
3. 如果为 false，跳过 if 的 `{}`，执行 else 后面 `{}` 里的内容。

## 2.3 if-else if-else：多种情况

实际中往往不止两种情况。比如成绩分级：90 以上 A，80 以上 B，60 以上 C，否则 D。这时用 `else if`（否则如果）：

```java
Scanner sc = new Scanner(System.in);
int score = sc.nextInt();
if (score >= 90) {
    System.out.println("A");
} else if (score >= 80) {
    System.out.println("B");
} else if (score >= 60) {
    System.out.println("C");
} else {
    System.out.println("D");
}
```

### 关键理解：从上往下判断，一旦命中就停止

程序会**从上到下**依次判断条件，只要某一个条件为 true，执行完它对应的语句后，**整个 if-else 链就结束了**，不再往下判断。所以条件顺序很重要：上面写 `>= 60`，那 95 分也会先命中 60 分这条，永远轮不到 90 分。所以要从严格到宽松排：90 → 80 → 60。

### 为什么不用多个独立的 if？

如果写成三个独立的 `if`：
```java
if (score >= 90) { ... }
if (score >= 80) { ... }   // 95 分这里也会为 true！
```
95 分会同时满足前两条，打印两次。`else if` 保证了"互斥"——只走一条路。

## 2.4 逻辑运算符：组合多个条件

有时一个判断需要多个条件同时满足，比如"年龄在 18 到 60 之间"。Java 提供 `&&`、`||`、`!`：

- `&&`（并且，AND）：两边都为 true 才 true。
- `||`（或者，OR）：两边只要有一个 true 就 true。
- `!`（非，NOT）：取反，true 变 false，false 变 true。

```java
int age = 25;
if (age >= 18 && age <= 60) {
    System.out.println("适龄劳动人口");
}
```

`age >= 18 && age <= 60` 意思是"年龄≥18 并且 年龄≤60"，两个条件都要满足。

```java
boolean isRaining = true;
if (!isRaining) {
    System.out.println("出门玩");
} else {
    System.out.println("在家待着");
}
```

`!isRaining` 表示"不下雨吗"，isRaining 为 true，取反为 false，走 else，打印"在家待着"。

### && 和 || 的短路特性

`&&` 如果左边已经是 false，右边就不再计算了（结果必然 false）。`||` 如果左边已经是 true，右边也不再计算。这叫"短路"，能提高效率，也能避免错误，比如 `a != 0 && b / a > 1`，当 a 为 0 时左边为 false，右边 `b/a` 不执行，避免除零。

## 2.5 三目运算符（三元运算符）

对于简单的"二选一"，Java 有个简写：`条件 ? 值1 : 值2`。条件为 true 取值1，否则取值2。

```java
int n = 5;
String result = (n % 2 != 0) ? "奇数" : "偶数";
System.out.println(result);   // 奇数
```

等价于：
```java
String result;
if (n % 2 != 0) {
    result = "奇数";
} else {
    result = "偶数";
}
```

三目运算符的好处是简洁，但只适合简单的赋值，复杂逻辑还是用 if-else 更清晰。

## 2.6 嵌套 if

if 里还能再套 if，用于更复杂的判断：

```java
int age = 20;
boolean hasLicense = true;
if (age >= 18) {
    if (hasLicense) {
        System.out.println("可以开车");
    } else {
        System.out.println("年龄够了，但没驾照，不能开");
    }
} else {
    System.out.println("未成年，不能开车");
}
```

注意嵌套层数不要太多，否则代码难读。能用 `&&` 合并的就合并：
```java
if (age >= 18 && hasLicense) {
    System.out.println("可以开车");
}
```

## 2.7 完整示例：判断闰年

闰年规则：能被 4 整除且不能被 100 整除，或者能被 400 整除。

```java
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int year = sc.nextInt();
        if ((year % 4 == 0 && year % 100 != 0) || (year % 400 == 0)) {
            System.out.println("闰年");
        } else {
            System.out.println("平年");
        }
    }
}
```

解释：`year % 4 == 0` 是"能被 4 整除"，`year % 100 != 0` 是"不能被 100 整除"，这两个用 `&&` 连起来表示第一种情况；再用 `||` 连上"能被 400 整除"的第二种情况。两种情况任一满足即为闰年。括号用来明确优先级，建议多加括号增强可读性。

## 常见错误

1. **用 `=` 当等于**：`if (x = 5)` 在 Java 里会报错（因为 5 不是 boolean），但更重要的是养成用 `==` 比较的习惯。
2. **条件里直接写 `if (n)`**：Java 不像 C/Python，不允许把整数当布尔用。`if (n)` 报错，必须写 `if (n != 0)`。
3. **`else if` 写成 `elif`**：Python 用 `elif`，Java 必须写 `else if` 两个单词。
4. **忘记大括号导致逻辑错误**：`if (x > 0) System.out.println("正"); System.out.println("总是打印");`——第二条语句没有在 if 内，无论 x 正负都打印。**建议即使一条语句也加大括号**，避免后期修改出错。
5. **`else if` 顺序错误**：先写 `>= 60` 再写 `>= 90`，会导致 95 分被分到 C 档。从严格到宽松排列。

## 本章要点

- `if (条件) { ... }`：条件为 true 才执行。
- `if-else`：二选一；`if-else if-else`：多选一，从上到下命中即停。
- 比较用 `==`、`!=`、`>`、`<`、`>=`、`<=`；赋值用 `=`，二者别混。
- 逻辑运算：`&&`（且）、`||`（或）、`!`（非），有短路特性。
- 三目运算 `条件 ? 值1 : 值2` 适合简单二选一赋值。
- 条件必须是 boolean 类型，不能拿整数当布尔。

## 动手试试

1. 读入一个整数，判断它是正数、负数还是零，分别输出"正数""负数""零"。
2. 读入三条边长 a、b、c，判断能否构成三角形（任意两边之和大于第三边），能则输出"是三角形"，否则输出"不是"。
3. 读入一个年份，判断是闰年还是平年（参考 2.7 的规则）。
""", "判断奇偶"),

    ("第 3 章：循环", """# 第 3 章：循环

## 引入：重复做同一件事

想象你要抄写 100 遍"我不再迟到"。如果一行行手写，得写 100 次，非常枯燥。但如果你对弟弟说"帮我抄 100 遍这句话"，他只需要重复同一个动作 100 次就行。**循环**就是让计算机"重复做同一件事"的机制——你告诉它做什么、做多少次，剩下的它自己搞定。

生活里循环很多：每天起床刷牙、上 8 节课、跑 10 圈操场。计算机最擅长重复劳动，而且一秒能重复几亿次。这一章我们学 Java 的两种循环：`for` 和 `while`。

## 3.1 for 循环：知道次数的重复

`for` 循环适合"已知重复次数"的场景。语法：

```java
for (初始化; 条件; 更新) {
    // 要重复执行的语句
}
```

三个部分用分号隔开：
1. **初始化**：循环开始前执行一次，通常声明一个计数器变量。
2. **条件**：每次循环开始前判断，true 才继续，false 就结束循环。
3. **更新**：每次循环结束后执行，通常让计数器 +1 或 -1。

### 最经典的例子：打印 1 到 5

```java
for (int i = 1; i <= 5; i++) {
    System.out.println(i);
}
```

输出：
```
1
2
3
4
5
```

逐行拆解：
- `int i = 1`：声明计数器 i，初始值为 1。
- `i <= 5`：每次循环前判断 i 是否 ≤ 5。第 1 次 i=1，true，进入循环；...第 6 次判断 i=6，false，退出循环。
- `i++`：i++ 等同于 i = i + 1，每次循环体执行完后让 i 加 1。
- `System.out.println(i)` 是循环体，重复执行。

### 执行流程（重要）

1. 初始化：i = 1
2. 判断：1 <= 5？true，执行循环体打印 1
3. 更新：i 变成 2
4. 判断：2 <= 5？true，打印 2
5. 更新：i 变成 3
6. ……（重复）
7. i 变成 6，判断 6 <= 5？false，结束循环

### 从 0 开始的习惯

编程里习惯从 0 开始计数。`for (int i = 0; i < n; i++)` 会执行 n 次，i 依次取 0、1、2、...、n-1。

```java
for (int i = 0; i < 5; i++) {
    System.out.println("第 " + i + " 次");
}
```
输出 0、1、2、3、4，共 5 次。**记住：`i < n` 表示循环 n 次，i 从 0 到 n-1。**

### 改变步长

步长（每次 i 加多少）可以自己定：

```java
for (int i = 0; i <= 10; i += 2) {   // i 每次 +2
    System.out.println(i);   // 0 2 4 6 8 10
}
```

`i += 2` 等同于 `i = i + 2`。还可以倒着数：
```java
for (int i = 5; i >= 1; i--) {   // i 每次 -1
    System.out.println(i);   // 5 4 3 2 1
}
```

## 3.2 while 循环：不知道次数，只看条件

有时我们不知道要重复多少次，只知道"满足某条件就继续"。比如"不停地读数，直到读到 0 停止"。这时用 `while`：

```java
while (条件) {
    // 条件为 true 就重复执行
}
```

### 示例：倒计时

```java
int n = 5;
while (n > 0) {
    System.out.println(n);
    n--;            // 别忘了让 n 减小，否则死循环！
}
System.out.println("发射！");
```

输出 5、4、3、2、1，然后"发射！"。

### for 和 while 的关系

`for` 和 `while` 能互相转换：
```java
for (int i = 0; i < 5; i++) { ... }
// 等价于
int i = 0;
while (i < 5) { ...; i++; }
```

什么时候用 for，什么时候用 while？
- **知道次数**用 for（如遍历 10 次、遍历数组）。
- **不知道次数，只知道停止条件**用 while（如读输入直到某个值）。

## 3.3 do-while：至少执行一次

还有一种变体 `do-while`，先执行一次再判断条件，**保证至少执行一次**：

```java
do {
    // 循环体
} while (条件);   // 注意末尾有分号！
```

```java
int i = 1;
do {
    System.out.println(i);
    i++;
} while (i <= 5);
```

即使一开始条件就为 false，do-while 也会执行一次。而 while 可能一次都不执行。比如菜单程序：先显示一次菜单，再问用户要不要继续。

## 3.4 break 与 continue：跳出和跳过

有时需要在循环中途提前退出，或跳过某一次。

- **`break`**：立刻跳出整个循环（不再继续）。
- **`continue`**：跳过本次剩余语句，直接进入下一次循环判断。

### break 示例：找第一个大于 0 的数

```java
int[] arr = {-3, -1, 0, 5, 7};
for (int i = 0; i < arr.length; i++) {
    if (arr[i] > 0) {
        System.out.println("找到 " + arr[i]);
        break;   // 找到就停，不再继续找
    }
}
```
找到 5 后立刻停止，不会继续看 7。

### continue 示例：只打印奇数

```java
for (int i = 1; i <= 10; i++) {
    if (i % 2 == 0) {
        continue;   // 偶数跳过，不打印
    }
    System.out.println(i);   // 只打印 1 3 5 7 9
}
```

i 是偶数时执行 continue，跳过后面的 println，回到 for 的更新和判断。注意：continue 在 for 里会先执行"更新"再判断，所以不会卡死。

## 3.5 累加器模式：用循环做求和

循环最常见的用途是累加。比如求 1+2+3+...+100 的和：

```java
int sum = 0;                     // 在循环外初始化"累加器"
for (int i = 1; i <= 100; i++) {
    sum += i;                    // 等同于 sum = sum + i
}
System.out.println(sum);         // 5050
```

**关键思路**：声明一个变量 `sum` 装累加结果，初始为 0；每次循环把新的数加进去。这就像往一个篮子里不断放苹果，最后数总数。

### 累乘同理

求 1×2×3×...×n（阶乘）：
```java
long product = 1;                // 累乘初始为 1，不是 0
for (int i = 1; i <= 10; i++) {
    product *= i;
}
System.out.println(product);     // 3628800
```

注意累乘初始值是 1（因为乘以 0 永远是 0），并且用 `long` 防止结果太大溢出。

## 3.6 完整示例：求 1 到 n 的偶数和

```java
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int sum = 0;
        for (int i = 1; i <= n; i++) {
            if (i % 2 == 0) {     // 是偶数
                sum += i;
            }
        }
        System.out.println(sum);
    }
}
```

输入 10，输出 30（2+4+6+8+10）。

## 常见错误

1. **死循环**：`while (true)` 或忘了更新计数器（如 while 循环里没写 `i++`），条件永远为 true，程序卡死。**写 while 时先检查是否有让条件变 false 的更新语句**。
2. **`for (int i = 0; i <= n; i++)` 多执行一次**：用 `<=` 会执行 n+1 次（i 从 0 到 n）。一般用 `< n` 才是 n 次。
3. **循环变量在循环外访问**：`for (int i = 0; ...)` 里的 i 只在循环内有效，循环外用 i 会报错。如果要在循环外用，得在外面声明。
4. **sum 初始化为 0 之外的其他值**：累加器初始值必须是 0（不偏移结果），累乘必须是 1。
5. **continue 后忘更新**：在 while 里写 `if (...) continue;` 后忘了 `i++`，可能死循环。for 循环的更新在 continue 后仍会执行，所以更安全。

## 本章要点

- `for (初始化; 条件; 更新) { ... }`：适合已知次数；执行顺序是 初始化→判断→循环体→更新→判断→……
- `while (条件) { ... }`：适合未知次数，只看条件；每次循环体里必须有让条件趋向 false 的更新。
- `do-while`：至少执行一次。
- `break` 跳出整个循环，`continue` 跳过本次剩余语句。
- 累加器模式：循环外声明 `sum = 0`，每次循环 `sum += 当前项`。
- `i < n` 循环 n 次（i: 0..n-1），`i <= n` 循环 n+1 次。

## 动手试试

1. 用 for 循环打印 1 到 20 中所有 3 的倍数。
2. 求 1+2+3+...+1000 的和。
3. 读入一个正整数 n，求它的各位数字之和（提示：用 `n % 10` 取个位，`n /= 10` 去掉个位，while 循环直到 n 变 0）。
""", "数组求和"),

    ("第 4 章：数组", """# 第 4 章：数组

## 引入：一排编了号的抽屉

想象学校里有一排存物柜，每个柜门上写着编号 0、1、2、3、4……你想找第 3 号柜子，直接走到 3 号位置就行，不用从头一个个数。**数组**就是这样一排"编了号的抽屉"：把一堆**同类型**的数据放在一起，每个数据有自己的编号（叫**索引**或**下标**），通过编号能直接找到对应的数据。

### 为什么需要数组？

如果班上有 50 个学生，你要存 50 个成绩。用 50 个变量 `score1`、`score2`...`score50`？太麻烦了！用数组 `int[] scores = new int[50];`，一个名字管 50 个数，还能用循环统一处理。数组是"批量管理数据"的利器。

## 4.1 声明数组

Java 里声明数组要指定**元素类型**和**长度**。有几种写法：

```java
// 写法 1：先声明长度，元素默认为 0
int[] arr = new int[5];       // 创建长度为 5 的 int 数组，元素全是 0

// 写法 2：声明的同时赋初值
int[] arr2 = {10, 20, 30, 40, 50};   // 长度 5，值已给定

// 写法 3：先声明，后用 new
int[] arr3;
arr3 = new int[3];
```

逐行解释：
- `int[]` 表示"int 数组"类型。注意方括号 `[]` 紧跟类型，这是 Java 推荐写法。
- `new int[5]`：`new` 表示在内存里开辟空间；`int[5]` 表示 5 个装 int 的格子，每个格子**自动初始化为 0**（如果是 double 数组则是 0.0，boolean 是 false，String 是 null）。
- `{10, 20, ...}`：花括号里直接列值，Java 自动推断长度。

**重要**：数组一旦创建，**长度就固定了**，不能再变。想变长要用 ArrayList（第 10 章讲）。

## 4.2 访问元素：用索引

数组里每个格子有一个编号，叫**索引**，从 **0 开始**（不是 1！）。长度为 5 的数组，索引是 0、1、2、3、4。

```java
int[] arr = {10, 20, 30, 40, 50};
System.out.println(arr[0]);    // 10  第 0 个
System.out.println(arr[2]);    // 30  第 2 个
System.out.println(arr[4]);    // 50  最后一个

arr[1] = 99;                   // 把第 1 个改成 99
System.out.println(arr[1]);    // 99
```

### 为什么从 0 开始？

这和计算机内存地址计算有关：数组名指向起始位置，索引就是"偏移量"。第一个元素偏移 0，所以索引是 0。虽然一开始不习惯，但用多了就自然了。

### 长度：arr.length

每个数组都有一个 `length` 属性表示长度（**不是方法，没有括号**）：
```java
int[] arr = {10, 20, 30};
System.out.println(arr.length);   // 3
```

**索引范围**：0 到 `arr.length - 1`。访问 `arr[arr.length]`（越界）会抛出 `ArrayIndexOutOfBoundsException`，程序崩溃。

## 4.3 从键盘读入数组

最常见的场景：第一行输入个数 n，第二行输入 n 个数。

```java
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();              // 先读个数
        int[] arr = new int[n];            // 创建长度为 n 的数组
        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();         // 逐个读入
        }
        // 接下来就能用 arr 了
    }
}
```

解释：先用 `new int[n]` 造一个能装 n 个数的数组；再用 for 循环，i 从 0 到 n-1，每次读一个数放进 `arr[i]`。**这是必背的标准写法。**

## 4.4 遍历数组：for 循环

"遍历"就是挨个访问数组里每个元素。最常用的是用索引：

```java
int[] arr = {10, 20, 30, 40, 50};
for (int i = 0; i < arr.length; i++) {
    System.out.println(arr[i]);
}
```

输出 10、20、30、40、50。注意条件是 `i < arr.length`（不是 `<=`），因为索引到 length-1 结束。

### 增强 for 循环（for-each）

Java 还有一种简写，适合"只看不改"的遍历：

```java
int[] arr = {10, 20, 30, 40, 50};
for (int x : arr) {        // 每个 arr 里的元素依次赋给 x
    System.out.println(x);
}
```

`for (int x : arr)` 读作"对 arr 里每个 int 元素 x"。好处是不用管索引，缺点是拿不到索引，也不能修改数组内容（x 是副本）。

## 4.5 求和、最大值、最小值

这些是数组的经典操作，套路都是"遍历 + 累加/比较"。

### 求和

```java
int[] arr = {10, 20, 30, 40, 50};
int sum = 0;
for (int i = 0; i < arr.length; i++) {
    sum += arr[i];            // 累加每个元素
}
System.out.println(sum);      // 150
```

### 找最大值

```java
int[] arr = {10, 50, 30, 40, 20};
int max = arr[0];             // 先假设第一个是最大的
for (int i = 1; i < arr.length; i++) {
    if (arr[i] > max) {       // 发现更大的
        max = arr[i];         // 更新 max
    }
}
System.out.println(max);      // 50
```

**思路**：先假设第一个元素最大，然后从第二个开始挨个比较，遇到比当前 max 大的就更新。最小值同理，把 `>` 换成 `<`。

## 4.6 Arrays 工具类

Java 提供了 `Arrays` 工具类，封装了常用操作。要用得先 `import`：

```java
import java.util.Arrays;

int[] arr = {5, 2, 8, 1, 9};

Arrays.sort(arr);                       // 排序（原地，从小到大）
System.out.println(Arrays.toString(arr));  // 打印 [1, 2, 5, 8, 9]
```

- `Arrays.sort(arr)`：把数组排序，排序后 arr 本身变了（从小到大）。
- `Arrays.toString(arr)`：把数组转成可读字符串如 `[1, 2, 3]`，因为**直接 println 数组只会打印地址**（如 `[I@1b6d3586`），这是初学者常踩的坑。

## 4.7 完整示例：读入数组并求最大值

```java
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }
        int max = arr[0];
        for (int i = 1; i < n; i++) {
            if (arr[i] > max) {
                max = arr[i];
            }
        }
        System.out.println(max);
    }
}
```

输入：
```
5
3 7 2 9 4
```
输出 `9`。

## 常见错误

1. **索引越界**：`int[] arr = new int[5]; arr[5] = 1;`——长度 5 的数组索引只到 4，访问 arr[5] 报 `ArrayIndexOutOfBoundsException`。**记住索引范围是 0 到 length-1。**
2. **直接打印数组**：`System.out.println(arr);` 打印出来是 `[I@xxxx`（地址），不是内容。要打印内容用 `Arrays.toString(arr)`。
3. **数组长度写错**：`int[] arr = new int[n];` 但 n 还没读到就用了。要先读 n 再创建数组。
4. **忘记初始化就用**：`int[] arr; arr[0] = 1;`——只声明没创建（没 new），arr 是 null，报空指针错。必须 `new`。
5. **for-each 里修改元素**：`for (int x : arr) { x = 0; }` 改的是副本 x，原数组不变。要修改得用索引循环。

## 本章要点

- 数组 = 一排编了号的抽屉，装同类型数据；创建后长度固定。
- 索引从 0 开始，范围 0 到 `arr.length - 1`；越界访问会报错。
- 声明：`int[] arr = new int[n];` 或 `int[] arr = {1, 2, 3};`。
- 遍历用 `for (int i = 0; i < arr.length; i++)`；只读可用 `for (int x : arr)`。
- 求和/最值套路：循环 + 累加/比较；最大值先假设 arr[0]。
- `Arrays.sort()` 排序，`Arrays.toString()` 打印内容。

## 动手试试

1. 读入 n 和 n 个整数，输出它们的和、平均值（用 double）。
2. 读入 n 个整数，倒序输出（从最后一个到第一个）。
3. 读入 n 个整数，输出最大值和最小值之差。
""", "数组最大值"),

    ("第 5 章：字符串", """# 第 5 章：字符串

## 引入：文字的处理

你已经会用 `String` 存一段文字了（第 1 章学过）。但程序里经常要对文字做各种处理：算一句话有几个字、把名字变大写、把一句话按空格拆成单词、把几段话拼起来……这一章我们就系统地学习 Java 里字符串的各种操作。

把字符串想象成**一串穿起来的珠子**，每颗珠子是一个字符，从 0 开始编号。和数组类似，可以按编号取字符。

## 5.1 创建字符串

```java
String s1 = "hello";                 // 直接用双引号
String s2 = new String("world");     // 用 new（少用）
String s3 = "";                      // 空字符串（长度 0）
```

最常用的是第一种：双引号直接写。**字符串内容必须用双引号**，单个字符才用单引号（`char`）。

## 5.2 基本属性与访问

### 长度：length()

注意：字符串的 `length()` 是**方法**（带括号），数组的 `length` 是属性（不带括号）。这是初学常混淆的点。

```java
String s = "hello";
int len = s.length();        // 5
```

### 取某个字符：charAt(i)

```java
String s = "hello";
char c = s.charAt(0);        // 'h'  第 0 个字符
char c2 = s.charAt(4);       // 'o'  最后一个
```

索引同样从 0 开始，到 `length()-1` 结束。越界访问 `s.charAt(10)` 会抛 `StringIndexOutOfBoundsException`。

### 字符串和字符数组互转

```java
String s = "hello";
char[] chars = s.toCharArray();   // 字符串 -> 字符数组
String s2 = new String(chars);     // 字符数组 -> 字符串
```

这在你需要逐个修改字符时很有用（因为 String 本身不能改）。

## 5.3 字符串比较：equals vs ==（重点！）

这是 Java 字符串最容易踩的坑。比较两个字符串内容是否相同，**必须用 `equals`**，不能用 `==`：

```java
String a = "hello";
String b = "hello";
String c = new String("hello");

System.out.println(a.equals(b));    // true   内容相同
System.out.println(a.equals(c));    // true   内容相同
System.out.println(a == b);         // true   （巧合，因为字符串常量池）
System.out.println(a == c);         // false! == 比较的是地址，c 是 new 出来的新对象
```

**解释**：
- `equals()` 比较**内容**（两个字符串是不是长得一样）。
- `==` 比较**引用**（两个变量是不是指向内存里同一个对象）。
- `a` 和 `b` 都指向常量池里同一个 "hello"，所以 `==` 为 true；但 `c` 是用 `new` 新建的，是另一个对象，地址不同，所以 `==` 为 false。

**结论**：永远用 `equals()` 比较字符串内容，别用 `==`。

### 比较时忽略大小写

```java
"Hello".equalsIgnoreCase("hello");   // true
```

## 5.4 字符串拼接

用 `+` 拼接：

```java
String s = "Hello" + " " + "World";   // Hello World
int age = 12;
String info = "我今年 " + age + " 岁";  // 我今年 12 岁
```

`+` 一边是字符串时，另一边会自动转成字符串拼接。这在打印时非常方便。

### 频繁拼接用 StringBuilder

`+` 拼接的原理是：每次都新建一个 String 对象（因为 String 不可变）。少量拼接无所谓，但在循环里拼接几千次会很低效。这时用 `StringBuilder`：

```java
StringBuilder sb = new StringBuilder();
for (int i = 1; i <= 1000; i++) {
    sb.append(i);          // 追加内容，不创建新对象
    sb.append(" ");
}
String result = sb.toString();   // 最后转成 String
System.out.println(result);
```

`append()` 把内容追加到末尾，效率高。最后 `toString()` 转回 String。

## 5.5 常用方法

```java
String s = "  Hello World  ";

s.length();                  // 13（含空格）
s.trim();                    // "Hello World"  去掉首尾空格
s.toUpperCase();             // "  HELLO WORLD  "
s.toLowerCase();             // "  hello world  "
s.replace("o", "0");         // "  Hell0 W0rld  "  替换所有 o 为 0
s.substring(2, 7);           // "Hello"  从索引 2 到 7（不含 7）
s.substring(2);              // "Hello World  "  从索引 2 到末尾
s.indexOf("World");          // 8  第一次出现的位置，找不到返回 -1
s.contains("ell");           // true  是否包含
s.startsWith("  H");         // true
s.endsWith("ld  ");          // true
```

**重点**：
- `substring(a, b)` 取索引 a 到 b-1 的子串（含 a 不含 b，和数组切片一样的规则）。
- `indexOf` 找不到返回 -1（不是报错）。
- 这些方法都**返回新字符串**，原字符串不变（因为 String 不可变）。所以你常常要写 `s = s.trim();` 来接收结果。

## 5.6 字符串反转

经典题目：把字符串倒过来。最简单的方法用 StringBuilder：

```java
String s = "hello";
String reversed = new StringBuilder(s).reverse().toString();
System.out.println(reversed);   // olleh
```

### 手动反转（理解原理）

不用 StringBuilder，自己写反转：

```java
String s = "hello";
char[] chars = s.toCharArray();    // 转字符数组
int left = 0, right = chars.length - 1;
while (left < right) {
    char tmp = chars[left];        // 交换两端
    chars[left] = chars[right];
    chars[right] = tmp;
    left++;
    right--;
}
String reversed = new String(chars);
System.out.println(reversed);      // olleh
```

思路：转成字符数组，用双指针从两头往中间走，交换字符。

## 5.7 分割与拼接

### split：按分隔符拆分

```java
String s = "1 2 3 4 5";
String[] parts = s.split(" ");      // ["1", "2", "3", "4", "5"]
for (String p : parts) {
    System.out.println(p);
}
```

`split` 返回字符串数组。**注意：split 的参数是正则表达式**，特殊字符如 `.` `|` 要转义（写成 `\.`）。

### String.join：用分隔符拼接

```java
String[] parts = {"a", "b", "c"};
String joined = String.join("-", parts);   // a-b-c
```

## 5.8 完整示例：统计元音字母

统计字符串里 a/e/i/o/u 出现的次数（不区分大小写）：

```java
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.nextLine();       // 读一整行
        int count = 0;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u'
                || c == 'A' || c == 'E' || c == 'I' || c == 'O' || c == 'U') {
                count++;
            }
        }
        System.out.println(count);
    }
}
```

输入 `Hello World`，输出 3（e、o、o）。

## 常见错误

1. **用 `==` 比较字符串**：`if (s == "yes")` 可能失败（当 s 是 new 出来的或从输入读的）。**必须用 `s.equals("yes")`**。
2. **`length()` 和 `length` 混淆**：字符串用 `s.length()`（方法），数组用 `arr.length`（属性）。
3. **修改 String 的方法"没接住"**：`s.trim();` 没写 `s = s.trim();`，原 s 没变。String 不可变，方法返回的是新对象。
4. **`charAt` 越界**：`s.charAt(s.length())` 报错，最大索引是 `length()-1`。
5. **split 的 `.` 没转义**：`"a.b.c".split(".")` 得到空数组（因为 `.` 在正则里是特殊字符）。要写 `split("\.")`。

## 本章要点

- String 是字符串类型，内容用双引号，**不可变**（操作返回新对象）。
- 长度用 `s.length()`（带括号），取字符用 `s.charAt(i)`，索引从 0 到 length()-1。
- 比较内容用 `equals()`，**别用 `==`**；忽略大小写用 `equalsIgnoreCase()`。
- 拼接用 `+`；循环里频繁拼接用 `StringBuilder.append()`。
- 常用方法：`trim`、`toUpperCase`、`substring(a,b)`、`indexOf`、`replace`、`split`。
- 反转：`new StringBuilder(s).reverse().toString()`。

## 动手试试

1. 读入一个字符串，统计其中大写字母的个数。
2. 读入一个字符串，把它反转后输出（先 StringBuilder 法，再手写双指针法）。
3. 读入一行用空格分隔的数字字符串（如 "1 2 3 4 5"），把它们拆开求和。（提示：`split(" ")` 后用 `Integer.parseInt()` 转成 int。）

""", "字符串反转"),

    ("第 6 章：方法（函数）", """# 第 6 章：方法（函数）

## 引入：菜谱——给原料，出成品

想象妈妈教你做番茄炒蛋：她给你一份**菜谱**，写明需要什么原料（鸡蛋、番茄、盐）、怎么做、最后产出什么菜。以后你想吃番茄炒蛋，只要按菜谱来，不用每次都问妈妈。**方法（也叫函数）**就是程序里的菜谱：你把"原料"（叫**参数**）交给它，它按步骤处理，最后给你"成品"（叫**返回值**）。

### 为什么需要方法？

写过几章程序你会发现：求最大值、求和这类操作反复出现。每次都复制粘贴一段代码？太啰嗦。把这段代码"打包"成一个方法，起个名字，以后只要喊这个名字就等于执行那段代码——**代码复用**，让程序更清晰。

生活类比：你不用每次跟妈妈说"打鸡蛋、切番茄、烧热锅、放油……"，只要说"做番茄炒蛋"，妈妈就懂了。方法名就像这道菜的名字，封装了细节。

## 6.1 定义方法

Java 里方法必须定义在**类里面**（也就是 `class Main { ... }` 的大括号内，和 main 同级）。语法：

```java
修饰符 返回类型 方法名(参数列表) {
    // 方法体
    return 返回值;   // 如果返回类型不是 void
}
```

### 第一个方法：两数相加

```java
public static int add(int a, int b) {
    int sum = a + b;
    return sum;
}
```

逐部分解释：
- `public static`：修饰符。`public` 表示公开；`static` 表示静态方法，可以在 main 里直接调用，不需要 new 对象。**初学阶段，自己写的方法统一加 `public static`**。
- `int`：返回类型。这个方法算完会返回一个 int。如果方法不返回东西，写 `void`。
- `add`：方法名，自己起，要有意义（驼峰命名）。
- `(int a, int b)`：参数列表。声明调用时要传两个 int，参数名 a 和 b 是方法内部的别名。**参数类型必须写**，这是 Java 和 Python 的区别。
- `return sum;`：把 sum 的值作为结果返回给调用者。一旦 return，方法立即结束。

### 完整程序示例

```java
import java.util.Scanner;

public class Main {
    // 自定义方法：求两数之和
    public static int add(int a, int b) {
        return a + b;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int x = sc.nextInt();
        int y = sc.nextInt();
        int result = add(x, y);    // 调用方法，把 x、y 传进去
        System.out.println(result);
    }
}
```

注意方法定义的位置：在 `class Main` 内部，和 `main` 同级（不是写在 main 里面）。调用时写 `add(x, y)`，把实参 x、y 传给形参 a、b。

## 6.2 参数与返回值

### 形参和实参

- **形参**（形式参数）：定义方法时写的参数，如 `add(int a, int b)` 里的 a、b。它们是方法内部的"占位符"。
- **实参**（实际参数）：调用时传进去的具体值，如 `add(3, 5)` 里的 3、5。

调用时，实参的值会**复制**给形参（这叫"值传递"）。在方法里改形参不影响外面的实参。

### 多种返回类型

返回类型可以是任何类型：`int`、`double`、`String`、`boolean`、`long` 等。也可以不返回（`void`）：

```java
// 返回较大的数
public static int max(int a, int b) {
    if (a > b) return a;
    return b;
}

// 返回是否为偶数
public static boolean isEven(int n) {
    return n % 2 == 0;
}

// 不返回值，只打印
public static void greet(String name) {
    System.out.println("你好，" + name);
}
```

调用：
```java
int m = max(3, 5);          // m = 5
boolean ok = isEven(4);     // ok = true
greet("小明");              // 打印"你好，小明"（无返回值，不能赋值）
```

### 没有返回值的方法用 void

`void` 方法只做事（如打印），不返回结果。不能写 `int x = greet("小明");`，因为 greet 没返回值。

## 6.3 方法的执行流程

调用方法时：
1. 主程序暂停，跳到方法里。
2. 把实参的值复制给形参。
3. 执行方法体。
4. 遇到 `return` 或方法体结束，带着返回值回到主程序。
5. 主程序继续，用返回值替换原调用处。

```
main 调用 add(3, 5)  →  跳到 add，a=3, b=5  →  算出 8  →  return 8  →  回到 main，result = 8
```

## 6.4 多个参数、参数顺序

方法可以有多个参数，**顺序必须对应**：

```java
public static void printInfo(String name, int age, double score) {
    System.out.println(name + " " + age + " 岁，成绩 " + score);
}

printInfo("小明", 12, 95.5);    // 正确
printInfo(12, "小明", 95.5);    // 错！类型和顺序不匹配
```

调用时实参的类型和顺序要和定义一致，否则编译报错。

## 6.5 方法重载（Overload）

Java 允许定义**同名**但**参数不同**的方法，叫**重载**：

```java
public static int add(int a, int b) {
    return a + b;
}

public static double add(double a, double b) {   // 参数类型不同
    return a + b;
}

public static int add(int a, int b, int c) {     // 参数个数不同
    return a + b + c;
}
```

调用时 Java 根据参数类型和个数自动选对应的方法：
```java
add(1, 2);          // 调用第一个，返回 3
add(1.5, 2.5);      // 调用第二个，返回 4.0
add(1, 2, 3);       // 调用第三个，返回 6
```

重载的好处：相似功能用同一个名字，调用者不用记多个名字（如 `println` 就是重载的，能打印 int、String、double 等）。

## 6.6 实战示例：判断质数

把"判断质数"封装成方法，主程序调用：

```java
import java.util.Scanner;

public class Main {
    // 判断 n 是否为质数
    public static boolean isPrime(int n) {
        if (n < 2) return false;
        for (int i = 2; i * i <= n; i++) {   // 只需试到 sqrt(n)
            if (n % i == 0) {
                return false;    // 能整除，不是质数
            }
        }
        return true;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        if (isPrime(n)) {
            System.out.println(n + " 是质数");
        } else {
            System.out.println(n + " 不是质数");
        }
    }
}
```

**好处**：判断质数的逻辑封装在方法里，主程序很简洁；以后别处要判断质数，直接调 `isPrime()`。注意 `i * i <= n` 是优化——因数成对出现，只需检查到 sqrt(n)。

## 常见错误

1. **方法定义在 main 里面**：Java 不允许方法嵌套定义。方法要写在 class 内、main 外面（同级）。
2. **忘记 return**：声明返回类型为 int，但方法体里没 return，编译报错。void 方法可以不 return。
3. **return 类型不匹配**：声明返回 int，却 `return "hello";`——类型不对。
4. **调用时参数不匹配**：方法定义 `add(int, int)`，调用 `add("3", 5)`——String 不能当 int。
5. **void 方法当有返回值用**：`int x = greet("小明");`——greet 是 void，没有返回值。

## 本章要点

- 方法 = 菜谱：给参数（原料），返回结果（成品）。代码复用的核心。
- 定义：`public static 返回类型 方法名(参数列表) { ... return ...; }`，必须写在 class 内、main 外。
- 形参是占位符，实参是调用时传的具体值；值传递——改形参不影响实参。
- `void` 方法不返回值；非 void 方法必须有 `return`。
- 方法重载：同名不同参（类型或个数不同），Java 自动选对应的。
- 把重复逻辑封装成方法，让主程序简洁、易维护。

## 动手试试

1. 写一个方法 `max(int a, int b, int c)`，返回三个数中的最大值，在 main 里读三个数调用它。
2. 写一个方法 `isPrime(int n)` 判断质数，然后在 main 里输出 1 到 100 之间所有质数。
3. 写一个方法 `factorial(int n)` 用循环求阶乘（下一章还会用递归再做一次）。

""", None),

    ("第 7 章：嵌套循环", """# 第 7 章：嵌套循环

## 引入：循环里面套循环

回忆第 3 章的 for 循环：重复做一件事。现在升级——**循环里面再套一个循环**，叫**嵌套循环**。这就像一周 7 天，每天上 4 节课：外层循环管"天"（7 次），内层循环管"每天的课"（4 次），总共 7 × 4 = 28 节课。

嵌套循环最经典的应用是：打印二维图案、处理二维数据、排序等。这一章重点学两个：打印图案、冒泡排序。

## 7.1 嵌套 for 循环的执行流程

```java
for (int i = 0; i < 3; i++) {        // 外层
    for (int j = 0; j < 3; j++) {    // 内层
        System.out.print("(" + i + "," + j + ") ");
    }
    System.out.println();            // 内层结束后换行
}
```

输出：
```
(0,0) (0,1) (0,2)
(1,0) (1,1) (1,2)
(2,0) (2,1) (2,2)
```

**关键理解**：外层每走一步，内层**完整跑一轮**。所以外层 3 步，每步内层跑 3 次，总共 9 次。

执行顺序：
1. i=0：内层 j 跑 0→1→2，打印 (0,0)(0,1)(0,2)，换行
2. i=1：内层 j 又从头跑 0→1→2，打印 (1,0)(1,1)(1,2)，换行
3. i=2：同上

### 总次数 = 外层次数 × 内层次数

外层 m 次、内层 n 次，循环体执行 m × n 次。这点要记牢，用于估算工作量。

## 7.2 打印直角三角形

用嵌套循环打印星号图案是经典练习。

### 左对齐直角三角形

```java
int n = 5;
for (int i = 1; i <= n; i++) {        // 第 i 行
    for (int j = 1; j <= i; j++) {    // 打印 i 个星号
        System.out.print("*");
    }
    System.out.println();             // 每行结束换行
}
```

输出：
```
*
**
***
****
*****
```

解释：第 1 行打印 1 个星，第 2 行打印 2 个……内层循环次数等于行号 i。外层管行数，内层管每行星号数。

### 倒三角形

```java
int n = 5;
for (int i = n; i >= 1; i--) {        // 从 n 行到 1 行
    for (int j = 1; j <= i; j++) {
        System.out.print("*");
    }
    System.out.println();
}
```

输出 5、4、3、2、1 个星，从多到少。

## 7.3 打印九九乘法表

嵌套循环的经典应用：

```java
for (int i = 1; i <= 9; i++) {
    for (int j = 1; j <= i; j++) {    // j 从 1 到 i
        System.out.print(j + "x" + i + "=" + (i * j) + "\t");
    }
    System.out.println();
}
```

输出：
```
1x1=1
1x2=2  2x2=4
1x3=3  2x3=6  3x3=9
...
1x9=9  2x9=18 ... 9x9=81
```

解释：
- 外层 i 是"行"，从 1 到 9。
- 内层 j 从 1 到 i（第 i 行有 i 个算式）。
- `\t` 是制表符，让每列对齐。
- `i * j` 要用括号包起来，否则会变成字符串拼接出错（`"=" + i * j` 在 Java 里运算优先级可能导致问题）。

## 7.4 冒泡排序（重点）

冒泡排序是嵌套循环最经典的算法。思路：相邻两个元素比较，顺序错了就交换，每轮把最大的"冒泡"到末尾。

### 算法演示

以 `[5, 1, 4, 2, 8]` 为例，第一轮：
- 比较 5 和 1，5>1，交换 → `[1, 5, 4, 2, 8]`
- 比较 5 和 4，5>4，交换 → `[1, 4, 5, 2, 8]`
- 比较 5 和 2，5>2，交换 → `[1, 4, 2, 5, 8]`
- 比较 5 和 8，5<8，不交换 → `[1, 4, 2, 5, 8]`

第一轮结束后，最大的 8 已经到最后。第二轮把次大的冒到倒数第二……共 n-1 轮。

### 代码

```java
int[] arr = {5, 1, 4, 2, 8};
int n = arr.length;
for (int i = 0; i < n - 1; i++) {              // 外层：n-1 轮
    for (int j = 0; j < n - i - 1; j++) {      // 内层：每轮比较到 n-i-1
        if (arr[j] > arr[j + 1]) {             // 相邻比较
            int temp = arr[j];                 // 交换（用临时变量）
            arr[j] = arr[j + 1];
            arr[j + 1] = temp;
        }
    }
}
```

### 关键细节解释

- **外层 `n - 1` 轮**：n 个数，最多需要 n-1 轮就能排好（最后一轮只剩一个数，不用排）。
- **内层 `n - i - 1`**：每轮结束后，最大的已经到末尾，下一轮不用再比较它。第 i 轮时，末尾 i 个已排好，所以内层只到 `n - i - 1`。
- **交换用临时变量**：`temp = a; a = b; b = temp;`——不能写 `a = b; b = a;`，这样 a 已经被覆盖，b 拿不到原来的 a。

### 优化：提前退出

如果某一轮没有发生任何交换，说明已经排好了，可以提前结束：

```java
for (int i = 0; i < n - 1; i++) {
    boolean swapped = false;
    for (int j = 0; j < n - i - 1; j++) {
        if (arr[j] > arr[j + 1]) {
            int temp = arr[j];
            arr[j] = arr[j + 1];
            arr[j + 1] = temp;
            swapped = true;
        }
    }
    if (!swapped) break;    // 没交换，已排好
}
```

## 7.5 完整示例：读入数组并排序

```java
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }
        // 冒泡排序
        for (int i = 0; i < n - 1; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (arr[j] > arr[j + 1]) {
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
        // 输出
        for (int i = 0; i < n; i++) {
            System.out.print(arr[i] + " ");
        }
    }
}
```

输入 `5 5 1 4 2 8`，输出 `1 2 4 5 8`。

## 常见错误

1. **内外层用同一个变量名**：`for (int i...) { for (int i...) }`——内层会覆盖外层，逻辑混乱。**内外层变量名要不同**，常用 i、j。
2. **内层循环次数写错**：冒泡排序内层写成 `j < n` 会多比较已排好的部分，浪费但不报错；写成 `j < n - i` 多比一次但通常不越界。**正确是 `n - i - 1`**。
3. **交换不用临时变量**：`arr[j] = arr[j+1]; arr[j+1] = arr[j];`——第二句时 arr[j] 已经是 arr[j+1] 的值了，交换失败。**必须用 temp**。
4. **打印时 println 每个元素**：导致每个数一行。要同一行用 `print` 加空格，最后再 `println` 换行。
5. **i*j 拼接字符串没加括号**：`"=" + i * j` 在 Java 里会先算 `+` 还是 `*`？实际 `*` 优先级高，但容易和字符串拼接混淆，**建议养成加括号的习惯**：`"=" + (i * j)`。

## 本章要点

- 嵌套循环：外层每走一步，内层完整跑一轮；总次数 = 外层次数 × 内层次数。
- 打印图案：外层管行数，内层管每行内容，每行末尾 `println` 换行。
- 九九乘法表：外层 i（1-9），内层 j（1 到 i），`j x i = i*j`。
- 冒泡排序：相邻比较交换，每轮把最大值冒到末尾；外层 n-1 轮，内层 n-i-1 次。
- 交换三变量：`temp = a; a = b; b = temp;`，必须用临时变量。
- 内外层变量名要区分（i、j），别重名。

## 动手试试

1. 打印 n 行的倒三角星号图（n 从键盘读入）。
2. 打印九九乘法表（参考 7.3）。
3. 读入 n 个数，用冒泡排序从小到大排好后输出。

""", "冒泡排序"),

    ("第 8 章：递归", """# 第 8 章：递归

## 引入：故事里的故事

你听过这个童谣吗？"从前有座山，山里有座庙，庙里有个老和尚在讲故事，讲的什么？从前有座山，山里有座庙……"——故事里套着同样的故事，永远讲不完（如果不被打断）。这就是**递归**的核心思想：**自己调用自己**。

再看一个数学例子：问 5 的阶乘（5!）是多少？
- 5! = 5 × 4!
- 4! = 4 × 3!
- 3! = 3 × 2!
- 2! = 2 × 1!
- 1! = 1（这是终点）

把大问题拆成"同类型的小问题"，直到遇到一个能直接给出答案的最小情况。这就是递归。

### 递归的两个必备部分

1. **递归出口（base case / 基准情形）**：不再递归、直接返回的最简单情况。没有它，递归会无限进行，程序崩溃。
2. **递归步骤**：把问题缩小一点，调用自己解决更小的子问题，然后组合结果。

## 8.1 阶乘：递归入门

```java
public static long factorial(int n) {
    if (n <= 1) return 1;            // 递归出口：1! = 1, 0! = 1
    return n * factorial(n - 1);     // 递归步骤：n! = n * (n-1)!
}
```

### 执行过程（以 factorial(5) 为例）

```
factorial(5)
= 5 * factorial(4)
= 5 * (4 * factorial(3))
= 5 * (4 * (3 * factorial(2)))
= 5 * (4 * (3 * (2 * factorial(1))))
= 5 * (4 * (3 * (2 * 1)))       ← factorial(1) 命中出口，返回 1
= 5 * (4 * (3 * 2))             ← 开始往回算
= 5 * (4 * 6)
= 5 * 24
= 120
```

**两阶段**：
1. **递（往下挖）**：factorial(5) 调 factorial(4) 调 factorial(3)……一直调到 factorial(1) 命中出口。
2. **归（往上回）**：从 factorial(1)=1 开始，一层层把结果乘回来，最终得到 120。

### 为什么用 long？

阶乘增长极快：13! 就超过 int 的最大值（约 21 亿）。所以求阶乘要用 `long`（能到约 9×10^18，到 20! 没问题）。更大就要用 BigInteger（这里不展开）。

## 8.2 斐波那契数列

斐波那契数列：1, 1, 2, 3, 5, 8, 13, 21, ...，规律是**每个数等于前两个数之和**。

数学定义：
- fib(1) = 1
- fib(2) = 1
- fib(n) = fib(n-1) + fib(n-2)  （n > 2）

递归实现非常直观：

```java
public static long fib(int n) {
    if (n == 1 || n == 2) return 1;          // 递归出口
    return fib(n - 1) + fib(n - 2);          // 递归步骤
}
```

### 注意：效率问题

这个写法虽然简单，但效率很低——计算 fib(40) 就要几百万次调用，因为大量重复计算（fib(5) 会重复算 fib(3) 多次）。实际工程中会用"记忆化"或循环来优化。但作为理解递归的例子，它很经典。

## 8.3 递归求和：1+2+...+n

```java
public static int sum(int n) {
    if (n == 1) return 1;             // 出口：sum(1) = 1
    return n + sum(n - 1);            // sum(n) = n + sum(n-1)
}
```

sum(5) = 5 + sum(4) = 5 + (4 + sum(3)) = ... = 5+4+3+2+1 = 15。

这和阶乘结构几乎一样，只是把乘法换成加法。**很多递归问题都是这种"n 和子问题组合"的模式**。

## 8.4 递归打印

递归不一定返回数值，也可以做动作：

```java
// 倒序打印 1 到 n
public static void printDesc(int n) {
    if (n == 0) return;            // 出口
    System.out.println(n);         // 先打印当前 n
    printDesc(n - 1);              // 再递归打印剩下的
}
```

调用 `printDesc(5)` 输出 5 4 3 2 1。

### 顺序的小秘密

如果把打印和递归的顺序换一下：

```java
public static void printAsc(int n) {
    if (n == 0) return;
    printAsc(n - 1);              // 先递归（先处理更小的）
    System.out.println(n);         // 递归回来后再打印
}
```

调用 `printAsc(5)` 输出 1 2 3 4 5（正序）！

**理解**：先递归再打印，意味着"先处理完更小的，再处理当前的"，所以最小的先输出。这个"先递后归"的顺序是递归的精髓，多想想。

## 8.5 递归的底层：调用栈

每次调用方法，Java 会在"调用栈"上放一帧（保存参数、局部变量、返回地址）。递归调用很多次，栈就越叠越高。出口返回时一层层弹出。

- **好处**：代码简洁，自然表达"分治"思想。
- **坏处**：递归太深会**栈溢出**（StackOverflowError）。Java 默认栈深度有限（几千到几万次）。所以递归不适合太深的场景。

### 递归 vs 循环

任何递归都能改成循环，反之亦然。怎么选？
- 问题有明显的"分层/分治"结构（如树、分形）→ 递归更直观。
- 简单的重复 → 循环更高效、不爆栈。

阶乘用循环也简单：`long r=1; for(int i=1;i<=n;i++) r*=i;`。递归在这里主要是教学意义。

## 8.6 完整示例：递归求阶乘

```java
import java.util.Scanner;

public class Main {
    public static long factorial(int n) {
        if (n <= 1) return 1;
        return n * factorial(n - 1);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        System.out.println(factorial(n));
    }
}
```

输入 5，输出 120。输入 20，输出 2432902008176640000（接近 long 上限）。

## 常见错误

1. **忘记递归出口**：`int f(int n) { return n * f(n-1); }` 没出口，无限递归直到 StackOverflowError。**写递归先想出口**。
2. **出口条件写错**：`if (n == 1) return 1;` 当 n 传 0 或负数时不会命中出口，仍然无限递归。所以阶乘出口用 `n <= 1` 更稳妥。
3. **递归步骤没有缩小**：`return f(n);` 没把问题变小，永远递归。**每次递归调用，问题规模必须变小**（如 n-1）。
4. **用 int 算阶乘**：13! 就溢出 int。阶乘用 `long`。
5. **重复计算没意识到**：朴素递归 fib(n) 对大 n 极慢，不是程序错误但会超时。

## 本章要点

- 递归 = 方法调用自己；必须有**递归出口**（基准情形）和**递归步骤**（缩小问题）。
- 执行分两阶段：**递**（往下调用）和**归**（往上返回结果）。
- 阶乘：`f(n) = n <= 1 ? 1 : n * f(n-1)`；用 `long` 防溢出。
- 斐波那契：`fib(n) = n<=2 ? 1 : fib(n-1)+fib(n-2)`（朴素递归效率低，有重复计算）。
- 递归太深会 StackOverflowError；任何递归都能改成循环。
- "先递归再处理"和"先处理再递归"顺序不同，结果可能相反。

## 动手试试

1. 用递归求 1+2+3+...+n 的和。
2. 用递归打印 1 到 n（正序，参考 8.4 的 printAsc）。
3. 思考：如何用递归判断一个字符串是否是回文（正读反读一样）？提示：比较首尾字符，中间部分递归判断。

""", "计算阶乘"),

    ("第 9 章：面向对象基础", """# 第 9 章：面向对象基础

## 引入：图纸和房子

想象一个建筑师设计了一栋房子的**图纸**，图纸上标明了房子有：客厅、卧室、厨房（这些是**属性**），以及能做的事：开门、关灯（这些是**方法**）。图纸本身不是房子，但工人可以按图纸**建出真正的房子**，还能建很多栋一样的。

**面向对象编程（OOP）** 里的核心概念完全对应：
- **类（class）** = 图纸，描述一类事物有什么属性和行为。
- **对象（object）** = 按图纸建出来的房子，是具体存在的实例。

举例：`Student` 类是图纸，描述"学生有姓名、成绩，能查询等级"。`Student s = new Student("小明", 95);` 就是按图纸建了一个具体的学生对象，名叫小明、成绩 95。

### 为什么需要面向对象？

之前我们用变量、数组、方法写程序，这是"面向过程"——按步骤办事。但现实世界的事物往往有"属性+行为"，把它们打包成"对象"更贴近现实，也更容易管理复杂程序。比如游戏里的角色有血量、攻击力（属性），能攻击、移动（方法），用对象描述最自然。

## 9.1 定义类

类 = 属性（成员变量）+ 行为（方法）。语法：

```java
class 类名 {
    // 成员变量（属性）
    类型 属性1;
    类型 属性2;

    // 构造方法（用来创建对象）
    类名(参数列表) {
        // 初始化属性
    }

    // 方法（行为）
    返回类型 方法名(参数列表) {
        // 方法体
    }
}
```

### 示例：Student 类

```java
class Student {
    // 成员变量（属性）
    String name;
    int score;

    // 构造方法
    Student(String name, int score) {
        this.name = name;        // this.name 是成员变量，name 是参数
        this.score = score;
    }

    // 方法（行为）
    String getGrade() {
        if (score >= 90) return "A";
        else if (score >= 80) return "B";
        else if (score >= 60) return "C";
        else return "D";
    }
}
```

逐部分解释：
- `class Student { ... }`：定义一个类，名字 Student（首字母大写是类名惯例）。
- `String name; int score;`：成员变量，描述学生有哪些属性。**没有 static**，它们属于每个对象。
- `Student(String name, int score) { ... }`：**构造方法**，名字和类名一样，没有返回类型。它的作用是创建对象时初始化属性。
- `this.name = name;`：`this` 指向"当前正在创建的对象"。`this.name` 是成员变量，`name`（右边）是构造方法的参数。当两者同名时，用 `this` 区分。
- `getGrade()`：一个方法，根据成绩返回等级。它能直接用成员变量 `score`（因为是同一个对象的属性）。

## 9.2 创建对象：new

类是图纸，要用 `new` 才能造出对象：

```java
Student s1 = new Student("小明", 95);
Student s2 = new Student("小红", 78);

System.out.println(s1.name);         // 小明  访问属性用 .
System.out.println(s2.score);        // 78
System.out.println(s1.getGrade());   // A    调用方法用 .
System.out.println(s2.getGrade());   // C
```

解释：
- `new Student("小明", 95)`：调用构造方法，在内存里创建一个 Student 对象，姓名设为小明、成绩设为 95。
- `Student s1 = ...`：把对象的引用存到变量 s1。
- `s1.name`：用 `.` 访问对象 s1 的 name 属性。
- `s1.getGrade()`：用 `.` 调用 s1 的方法。

**关键理解**：s1 和 s2 是两个**独立的对象**，各有各的 name 和 score，互不影响。就像两栋按同一图纸建的房子，里面的家具可以不同。

## 9.3 this 关键字

`this` 表示"当前对象"。最常用于构造方法里区分成员变量和参数同名的情况：

```java
class Student {
    String name;
    Student(String name) {
        this.name = name;     // this.name = 成员变量, name = 参数
    }
}
```

如果参数名不同（如 `Student(String n)`），可以不写 this：`name = n;`。但**习惯上参数名和成员变量同名，用 this 区分**，代码更清晰。

## 9.4 成员变量 vs 局部变量

- **成员变量**：在类里、方法外声明，属于对象，每个对象一份。没显式赋值时有默认值（int 0，String null，boolean false）。
- **局部变量**：在方法内声明，属于方法，方法执行完就消失。**没有默认值**，用前必须赋值。

```java
class Student {
    int score;                    // 成员变量，默认 0
    void test() {
        int x;                    // 局部变量，没默认值
        // System.out.println(x); // 报错！可能尚未初始化
        x = 5;
        System.out.println(score + x);   // score 是成员变量，能用
    }
}
```

## 9.5 方法：对象的行为

类里的方法（不带 static）属于对象，调用前必须先有对象：

```java
class Student {
    String name;
    int score;

    Student(String name, int score) {
        this.name = name;
        this.score = score;
    }

    // 普通方法：属于对象
    boolean isPass() {
        return score >= 60;
    }

    void introduce() {
        System.out.println("我叫 " + name + "，成绩 " + score);
    }
}

// 使用：
Student s = new Student("小明", 95);
s.introduce();           // 我叫 小明，成绩 95
System.out.println(s.isPass());   // true
```

注意：方法里可以直接用自己的成员变量 `name`、`score`，因为它们属于同一个对象。

## 9.6 完整示例

```java
import java.util.Scanner;

class Student {
    String name;
    int score;

    Student(String name, int score) {
        this.name = name;
        this.score = score;
    }

    String getGrade() {
        if (score >= 90) return "A";
        else if (score >= 80) return "B";
        else if (score >= 60) return "C";
        else return "D";
    }

    void introduce() {
        System.out.println(name + " 成绩 " + score + " 等级 " + getGrade());
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        Student[] students = new Student[n];      // 对象数组
        for (int i = 0; i < n; i++) {
            String name = sc.next();
            int score = sc.nextInt();
            students[i] = new Student(name, score);
        }
        for (int i = 0; i < n; i++) {
            students[i].introduce();
        }
    }
}
```

输入：
```
2
小明 95
小红 78
```
输出：
```
小明 成绩 95 等级 A
小红 成绩 78 等级 C
```

注意 `Student[] students` 是对象数组，每个元素是一个 Student 对象，需要分别 `new`。

## 常见错误

1. **类名首字母小写**：`class student` 虽然能编译但不合规范。**类名首字母大写**（Student、Car），变量和方法首字母小写（student、getGrade）。
2. **构造方法名和类名不一致**：类叫 Student，构造方法写成 `Student2(...)`——它就不是构造方法了，只是普通方法。**构造方法名必须和类名完全相同**。
3. **构造方法写了返回类型**：`public void Student(...)` 加了 void 就变成普通方法了！**构造方法没有返回类型**（连 void 都不写）。
4. **忘了 new 直接用**：`Student s; s.introduce();`——s 是 null，报空指针错。必须 `new` 创建。
5. **this 用错**：在 static 方法（如 main）里用 `this` 会报错——static 方法属于类，不属于对象，没有 this。

## 本章要点

- 类 = 图纸（描述属性和行为），对象 = 按图纸建的房子（具体实例）。
- 类有成员变量（属性）、构造方法（创建并初始化对象）、普通方法（行为）。
- 构造方法名 = 类名，无返回类型；`new 类名(...)` 创建对象。
- `this` 指当前对象，常用于区分成员变量和同名参数。
- 成员变量有默认值，局部变量没有；访问属性/方法用 `.`。
- 对象数组要逐个 `new`。

## 动手试试

1. 定义一个 `Circle` 类，有半径属性，构造方法接收半径，有方法 `double area()` 返回面积（π r²）。在 main 里创建半径为 3 的圆并打印面积。
2. 定义 `Book` 类，有书名、价格、库存三个属性，构造方法初始化，有方法 `void printInfo()` 打印信息。创建两本书并打印。
3. 给上面的 `Student` 类加一个方法 `boolean isPass()`，成绩 ≥ 60 返回 true。在 main 里判断几个学生是否及格。

""", None),

    ("第 10 章：集合框架", """# 第 10 章：集合框架

## 引入：更灵活的容器

第 4 章学的数组有个大缺点：**长度固定**，创建后不能加也不能减。但实际需求经常是"不知道有多少数据"——比如读入若干成绩直到结束、动态添加学生。Java 提供了**集合框架**，是一组更灵活的"容器"类。这一章学两个最常用的：`ArrayList`（动态数组）和 `HashMap`（键值对映射）。

## 10.1 ArrayList：长度可变的数组

你可以把 ArrayList 想象成**会自动变长的数组**——像一根能伸缩的橡皮筋，往里加东西就变长，拿走东西就变短。它和数组的区别：
- 数组长度固定，ArrayList 长度**自动可变**。
- 数组用 `[]` 访问，ArrayList 用 `get(i)`、`add(x)` 等方法。
- 只能装**对象类型**（Integer、String），不能直接装基本类型 int（要用 Integer）。

### 创建 ArrayList

```java
import java.util.ArrayList;        // 必须导入

ArrayList<Integer> list = new ArrayList<>();    // 装整数的列表
ArrayList<String> names = new ArrayList<>();    // 装字符串的列表
```

解释：
- `<Integer>` 是**泛型**，表示这个列表装的是 Integer 类型。
- **为什么是 Integer 不是 int？** 因为 ArrayList 只能装对象，`int` 是基本类型不是对象。Java 提供了对应的包装类：`Integer`（对应 int）、`Double`（double）、`Boolean`（boolean）。Java 会自动在 int 和 Integer 之间转换（自动装箱/拆箱），你不用操心。
- `<>`（钻石符号）：右边的 `<>` 让 Java 自动推断类型，省得再写一遍 `<Integer>`。

### 常用方法

```java
ArrayList<Integer> list = new ArrayList<>();
list.add(10);              // 末尾添加元素 → [10]
list.add(20);              // → [10, 20]
list.add(30);              // → [10, 20, 30]
list.get(0);               // 10  取第 0 个
list.get(2);               // 30  取第 2 个
list.size();               // 3   元素个数（注意是方法，带括号）
list.set(1, 99);           // 把第 1 个改成 99 → [10, 99, 30]
list.remove(0);            // 删除第 0 个 → [99, 30]
list.contains(30);         // true  是否包含 30
list.isEmpty();            // false 是否为空
```

**对比数组**：
| 操作 | 数组 | ArrayList |
|------|------|-----------|
| 长度 | `arr.length`（属性） | `list.size()`（方法） |
| 取元素 | `arr[i]` | `list.get(i)` |
| 改元素 | `arr[i] = x` | `list.set(i, x)` |
| 加元素 | 不支持（长度固定） | `list.add(x)` |
| 长度可变 | 否 | 是 |

### 遍历

```java
ArrayList<Integer> list = new ArrayList<>();
list.add(10); list.add(20); list.add(30);

// 方式 1：索引遍历
for (int i = 0; i < list.size(); i++) {
    System.out.println(list.get(i));
}

// 方式 2：for-each
for (int x : list) {
    System.out.println(x);
}
```

注意用 `list.size()`（方法）而不是 `length`。

### 完整示例：读入未知个数的数

```java
import java.util.ArrayList;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        ArrayList<Integer> list = new ArrayList<>();
        while (sc.hasNextInt()) {       // 只要还有整数就继续读
            list.add(sc.nextInt());
        }
        int sum = 0;
        for (int x : list) {
            sum += x;
        }
        System.out.println("共 " + list.size() + " 个数，和为 " + sum);
    }
}
```

`sc.hasNextInt()` 判断是否还有整数可读，适合不知道个数的输入场景。

## 10.2 HashMap：键值对映射

HashMap 就像一本**字典**：你按"词条"（key）查"释义"（value）。比如学生成绩表，用姓名查分数：给 "小明" 返回 95。它的核心是**键值对（key-value）**，每个 key 唯一对应一个 value。

### 为什么需要 HashMap？

如果用数组存"姓名→分数"，查找某个人的分数得挨个遍历，n 个人要查 n 次。HashMap 用哈希算法，**查找几乎是瞬间**（O(1)），不管有多少条数据。

### 创建和基本操作

```java
import java.util.HashMap;

HashMap<String, Integer> map = new HashMap<>();   // key 是 String，value 是 Integer
map.put("小明", 95);        // 添加/更新键值对
map.put("小红", 78);
map.put("小刚", 88);

map.get("小明");            // 95  按 key 取 value
map.get("不存在");          // null  key 不存在返回 null

map.containsKey("小红");    // true  是否包含某个 key
map.remove("小刚");         // 删除某个 key
map.size();                 // 2   键值对个数
```

解释：
- `<String, Integer>` 是泛型，表示 key 类型是 String，value 类型是 Integer。
- `put(key, value)`：添加一对；如果 key 已存在，会**覆盖**旧值。
- `get(key)`：按 key 取 value；key 不存在返回 `null`（不报错）。
- `containsKey(key)`：判断 key 是否存在。

### 遍历 HashMap

HashMap 没有索引，遍历用 entrySet：

```java
HashMap<String, Integer> map = new HashMap<>();
map.put("小明", 95);
map.put("小红", 78);

for (Map.Entry<String, Integer> entry : map.entrySet()) {
    String name = entry.getKey();        // 取 key
    int score = entry.getValue();        // 取 value
    System.out.println(name + ": " + score);
}
```

需要 `import java.util.Map;`。注意：HashMap 遍历的**顺序不保证**（不是按插入顺序也不是按 key 排序），如果需要排序要用 TreeMap。

### 完整示例：成绩统计

```java
import java.util.HashMap;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        HashMap<String, Integer> scores = new HashMap<>();
        for (int i = 0; i < n; i++) {
            String name = sc.next();
            int score = sc.nextInt();
            scores.put(name, score);        // 存入
        }
        String query = sc.next();            // 要查的人
        if (scores.containsKey(query)) {
            System.out.println(scores.get(query));
        } else {
            System.out.println("查无此人");
        }
    }
}
```

输入：
```
3
小明 95
小红 78
小刚 88
小明
```
输出 `95`。

## 10.3 什么时候用哪个？

| 容器 | 特点 | 适用场景 |
|------|------|---------|
| 数组 `int[]` | 长度固定，访问快 | 知道个数、不需要增删 |
| `ArrayList` | 长度可变，类似数组 | 需要频繁添加、遍历 |
| `HashMap` | 键值对，查找快 | 按 key 查 value（如姓名查成绩） |

经验法则：
- 数据个数固定 → 用数组。
- 需要动态增减 → 用 ArrayList。
- 需要"按某个标识查对应数据" → 用 HashMap。

## 常见错误

1. **ArrayList 写 `<int>` 而非 `<Integer>`**：`ArrayList<int>` 报错——泛型只能用对象类型。基本类型要用包装类：int→Integer、double→Double、char→Character、boolean→Boolean。
2. **`list.length` 写错**：ArrayList 用 `list.size()`（方法），数组才用 `arr.length`（属性）。
3. **`list[i]` 访问 ArrayList**：ArrayList 不能用 `[]`，要用 `list.get(i)`。
4. **HashMap 的 get 没判断 null**：`int s = map.get("不存在");` 会报空指针（null 转 int 时）。应先 `containsKey` 判断，或用对象类型接收。
5. **以为 HashMap 有顺序**：遍历顺序不可预测。需要顺序就用 LinkedHashMap（按插入序）或 TreeMap（按 key 排序）。

## 本章要点

- 集合框架提供比数组更灵活的容器；常用的是 ArrayList 和 HashMap。
- ArrayList = 动态数组，长度自动可变；用 `add`、`get`、`size`、`set`、`remove`。
- 泛型 `<类型>` 指定元素类型；基本类型用包装类（Integer、Double 等）。
- HashMap = 键值对字典，key 唯一，`put/get/containsKey`，查找快（O(1)）。
- `put` 相同 key 会覆盖旧值；`get` 不存在的 key 返回 null。
- 遍历 HashMap 用 `entrySet()`，顺序不保证。

## 动手试试

1. 读入 n 个整数存入 ArrayList，输出最大值和最小值之差。
2. 读入若干学生的姓名和成绩存入 HashMap，再读入若干查询姓名，输出对应成绩（不存在输出"查无此人"）。
3. 用 ArrayList 去重：读入 n 个数，去掉重复后输出（提示：用 `contains` 判断是否已存在）。

""", None),
]

# ── C 语言课程章节（10 章）──────────────────────────────
C_LESSONS = [
    ("第 1 章：C 语言入门", """# 第 1 章：C 语言入门

## 写在前面：什么是编程？

你用过计算器吗？你按数字、按运算符，它就给你结果。**编程**其实就是把一连串"按按钮"的指令提前写下来，让计算机照着执行。C 语言是一种"和计算机说话的语言"，它诞生于 1972 年，年纪比大多数同学的爸爸还大，但直到今天依然被用来写操作系统、单片机、游戏引擎。学 C 语言，就像学开车之前先学骑自行车——它会让你真正理解"计算机底层是怎么运转的"。

这一章我们先不追求复杂，目标只有一个：**让屏幕上出现一行字**。

## 1.1 第一个程序：Hello, World!

### 程序长什么样

```c
#include <stdio.h>

int main() {
    printf("Hello, World!\\n");
    return 0;
}
```

运行后屏幕会显示：

```
Hello, World!
```

### 逐行解释（这是初学者最该弄懂的）

- **`#include <stdio.h>`**：`#` 开头的叫"预处理指令"，可以理解为"开工前的准备"。`stdio` 是 **St**andar**d** **D**ata **I**nput **O**utput（标准输入输出）的缩写，`h` 是 header（头文件）。这一行的意思是："请把'负责输入输出的工具包'先准备好，我等下要用里面的 `printf`。"就像做饭前先把锅碗瓢盆摆好。
- **`int main()`**：`main` 是"主函数"，每一个 C 程序都**必须**有一个 `main`，程序总是从这里开始执行，就像每节课都从"上课"开始。`int` 表示这个函数执行完会还给操作系统一个整数（通常 0 表示"一切正常"）。
- **`{ ... }`**：大括号包起来的部分是函数的"身体"，里面是要做的事。
- **`printf("Hello, World!\\n");`**：`printf` 来自刚刚 include 的工具包，作用是"打印机"——把括号里的内容打印到屏幕。`"\\n"` 是一个特殊符号，意思是"换行"，就像打字时按一下回车。结尾的**分号**`;` 就像句号，每条指令都要以它结束。
- **`return 0;`**：把 0 还给操作系统，告诉它"我顺利跑完了，没有出错"。

### 为什么这么啰嗦？

你可能觉得："就想打印一句话，怎么要写这么多？" 这正是 C 语言的特点——它把权力交给你，连"换行"这种事也要你明确说出来。好处是一旦学会了，你对计算机的理解会比学其他语言的同学深得多。

## 1.2 让程序算点东西：变量

### 变量是什么？

把变量想象成**一个贴了标签的小盒子**。盒子里装东西（数据），标签是名字。你可以随时把盒子里的东西倒出来看，也可以换成别的东西。

```c
int age = 12;       // 一个叫 age 的盒子，里面放整数 12
age = 13;           // 把盒子里的东西换成 13
printf("%d\\n", age); // 打印盒子里的内容
```

### 类型：盒子的规格

C 是"强类型"语言，意思是**盒子要先声明能装什么种类的东西**：

| 类型名 | 装什么 | 例子 |
|--------|--------|------|
| `int` | 整数（没有小数点） | `int x = 10;` |
| `double` | 小数（带小数点） | `double pi = 3.14;` |
| `char` | 单个字符，用单引号 | `char c = 'A';` |

注意：`char` 只能放**一个**字符，`'A'` 可以，`'AB'` 不行。

### 格式符：printf 的"占位符"

`printf` 不会自动猜你要打印什么类型，你得告诉它：

```c
int a = 10;
double b = 3.14;
char c = 'X';
printf("a = %d\\n", a);     // %d 表示"这里放一个整数"
printf("b = %f\\n", b);     // %f 表示"这里放一个小数"
printf("c = %c\\n", c);     // %c 表示"这里放一个字符"
```

记住口诀：**整数 `%d`、小数 `%f`、字符 `%c`、字符串 `%s`**。

## 1.3 让用户从键盘输入：scanf

`printf` 是"打印机"往外吐字，`scanf` 则像**自动取款机读卡**——它从键盘读取你敲的内容，存进指定的盒子里。

```c
#include <stdio.h>

int main() {
    int a, b;
    scanf("%d %d", &a, &b);     // 从键盘读两个整数
    printf("%d\\n", a + b);      // 打印它们的和
    return 0;
}
```

### 那个神秘的 `&` 符号

注意 `scanf` 里写的是 `&a` 而不是 `a`。`&` 是"取地址"运算符，意思是"告诉 scanf 这个盒子在内存里的门牌号"，这样它才知道把读到的数字放进哪个盒子。**忘了写 `&` 是 C 初学者最最常见的错误**，我们稍后会专门讲。

你可以这样理解：scanf 是送快递的，你得告诉他"送到几号门"（地址），他才能把包裹（输入的数据）送对地方。`&a` 就是 a 这个盒子的门牌号。

### 输入时的格式

`scanf("%d %d", &a, &b)` 中间有一个空格，意思是输入时两个数字之间也要用空格隔开，比如输入：

```
3 5
```

程序就会输出 `8`。

## 1.4 完整可运行示例：计算两数之和

```c
#include <stdio.h>          // 引入输入输出工具包

int main() {                 // 程序从这里开始
    int a, b;                // 准备两个装整数的盒子
    scanf("%d %d", &a, &b);  // 从键盘读取两个整数，分别放进 a 和 b
    int sum = a + b;         // 把它们的和放进新盒子 sum
    printf("%d\\n", sum);      // 打印 sum 的值
    return 0;                // 告诉操作系统：正常结束
}
```

输入 `7 8`，输出 `15`。这就是你人生中第一个真正"有用"的程序！

## 常见错误

1. **忘记分号**：每条语句结尾必须有 `;`，漏掉会报错 `expected ';'`。
2. **`scanf` 忘记 `&`**：写成 `scanf("%d", a)` 而不是 `&a`，程序可能崩溃或读到垃圾值。这是新手第一大坑，请刻在脑子里。
3. **格式符用错**：用 `%d` 打印 `double`，或用 `%f` 打印 `int`，结果会不对。
4. **中文标点**：在代码里用了中文的分号`；`或引号`" "`，编译器不认识，会报一堆莫名其妙的错。请用英文输入法写代码。

## 本章要点

- 每个 C 程序都有 `int main()`，程序从这里开始执行。
- `#include <stdio.h>` 让我们能用 `printf` 和 `scanf`。
- 变量是"贴标签的盒子"，必须先声明类型再用。
- 格式符：`%d` 整数、`%f` 小数、`%c` 字符、`%s` 字符串。
- `scanf` 读取变量时**必须**加 `&` 取地址。
- 每条语句以分号 `;` 结束。

## 动手试试

1. 把第一个程序里的 `Hello, World!` 改成你自己的名字，运行看看。
2. 写一个程序，读入两个整数，打印它们的**差**（大数减小数）。
3. 想一想：如果 `scanf` 写成 `scanf("%d", a)`（漏了 `&`），会发生什么？查一查资料，理解为什么。
""", "两数之和"),

    ("第 2 章：条件判断", """# 第 2 章：条件判断

## 引入：人生处处是选择

你每天都会做很多"选择"：今天下雨，就带伞；不下雨，就不带。考试 90 分以上就是 A，否则就是 B。**条件判断**就是让程序学会"看情况办事"——在十字路口选一个方向走。C 语言用 `if`（如果）、`else if`（否则如果）、`else`（否则）来实现。

## 2.1 最简单的判断：if

### 长什么样

```c
#include <stdio.h>

int main() {
    int score;
    scanf("%d", &score);          // 读入一个成绩
    if (score >= 60) {            // 如果成绩 >= 60
        printf("及格了\\n");       // 就打印这句话
    }
    return 0;
}
```

### 逐行解释

- `if (score >= 60)`：括号里是一个**条件**，结果只有两种——"真"或"假"。`>=` 是"大于等于"的意思。当条件为真，花括号里的语句就执行；为假就跳过。
- 花括号 `{ }` 里的内容是"满足条件时要做的事"，可以写多条语句。

生活类比：if 就像门卫——"如果你有学生证（条件为真），就让你进（执行语句）；否则站着别动（跳过）"。

## 2.2 二选一：if-else

### 长什么样

```c
int n;
scanf("%d", &n);
if (n % 2 == 0) {          // 如果 n 除以 2 的余数是 0
    printf("even\\n");      // 是偶数
} else {                   // 否则
    printf("odd\\n");       // 是奇数
}
```

`%` 是"取余"运算符，`n % 2` 就是 n 除以 2 的余数。余数为 0 说明能被 2 整除，即偶数。

`else` 表示"否则"，当 if 条件为假时执行。`if` 和 `else` 就像岔路口的两个分支，**永远只走其中一条**。

## 2.3 多个分支：if - else if - else

### 成绩等级判断

```c
#include <stdio.h>

int main() {
    int score;
    scanf("%d", &score);

    if (score >= 90) {
        printf("A\\n");
    } else if (score >= 80) {
        printf("B\\n");
    } else if (score >= 60) {
        printf("C\\n");
    } else {
        printf("D\\n");
    }
    return 0;
}
```

### 执行顺序很重要

程序从上往下判断：先看 `score >= 90`，满足就打印 A，**然后跳出整个 if 结构**，不再往下看。如果不满足，才看 `score >= 80`，以此类推。所以即使成绩是 95，也只打印一次 A，不会"既打印 A 又打印 B"。

这就像排队领奖品：先问"你是不是 90 分以上？"是就领 A 等奖品走人；不是才继续往下问。

## 2.4 比较运算符和逻辑运算符

### 比较运算符

| 符号 | 含义 | 例子 |
|------|------|------|
| `==` | 等于 | `a == b` |
| `!=` | 不等于 | `a != b` |
| `>` | 大于 | `a > b` |
| `<` | 小于 | `a < b` |
| `>=` | 大于等于 | `a >= b` |
| `<=` | 小于等于 | `a <= b` |

### 逻辑运算符

用来把多个条件拼起来：

| 符号 | 含义 | 例子 | 说明 |
|------|------|------|------|
| `&&` | 并且（and） | `n > 0 && n < 100` | 两个都真才为真 |
| `||` | 或者（or） | `n < 0 || n > 100` | 任一为真就为真 |
| `!` | 非（not） | `!(n == 0)` | 取反 |

例子：判断一个数是否在 0 到 100 之间（含端点）。

```c
if (n >= 0 && n <= 100) {
    printf("在范围内\\n");
}
```

## 2.5 C 的"真"和"假"

C 语言里**没有真正的"布尔类型"**（C99 才引入 `_Bool`，但日常编程几乎不用）。C 的规则很简单：

- **0 表示假**
- **任何非 0 的值都表示真**（包括负数、包括 1、包括 999）

所以下面两种写法等价：

```c
if (n != 0) { ... }   // n 不等于 0
if (n) { ... }        // 同样意思：n 非 0 即为真
```

## 2.6 三目运算符：一行写完判断

有时候判断很简单，只想写在一行里，可以用 `条件 ? 真时的值 : 假时的值`：

```c
int n;
scanf("%d", &n);
printf("%s\\n", n % 2 != 0 ? "odd" : "even");
```

意思是："如果 `n % 2 != 0` 为真，就取 `"odd"`，否则取 `"even"`"。它就是浓缩版的 if-else，适合这种"二选一取值"的场景，但不适合写复杂逻辑。

## 常见错误

1. **把 `==` 写成 `=`**：`if (n = 5)` 不是判断"n 等不等于 5"，而是**把 5 赋值给 n**，然后因为 5 非 0 为真，条件永远成立！这是 C 最阴险的 bug 之一。判断相等一定要用两个等号 `==`。
2. **在 if 后面加分号**：`if (n > 0);` 后面的分号让 if 的"身体"变成空语句，下面的代码块无论条件真假都会执行。
3. **`&&` 写成 `&`**：`&` 是"按位与"，不是逻辑与。判断条件请用 `&&`。
4. **括号不配对**：if 后的 `(` 和 `)` 必须成对出现，少了会报错。

## 本章要点

- `if` 判断条件为真时执行，`else` 是"否则"，`else if` 提供更多分支。
- 比较用 `==`、`!=`、`>`、`<`、`>=`、`<=`；逻辑用 `&&`、`||`、`!`。
- C 里 0 为假，非 0 为真。
- 判断相等**必须**用 `==`，`=` 是赋值。
- 三目运算符 `条件 ? a : b` 适合简单的二选一。

## 动手试试

1. 写一个程序，读入一个整数，判断它是正数、负数还是零，分别打印。
2. 写一个程序，读入三个整数，打印其中最大的那个。（提示：用 if-else 比较。）
3. 想一想：`if (a = 0)` 这行代码会怎样？为什么这是一个永远为假的判断？
""", "判断奇偶"),

    ("第 3 章：循环", """# 第 3 章：循环

## 引入：重复的事交给机器

想象一个场景：老师让你把"我以后不再迟到"抄 100 遍。你肯定不愿意一行一行手写——要是有一台机器，按下按钮就自动重复 100 次，多好！**循环**就是程序里的"自动重复机器"。在 C 语言里，最常用的两种循环是 `for` 和 `while`。

## 3.1 for 循环：已知次数的重复

### 长什么样

```c
#include <stdio.h>

int main() {
    for (int i = 0; i < 5; i++) {     // 重复 5 次
        printf("第 %d 遍\\n", i);      // i 是当前是第几次
    }
    return 0;
}
```

运行后输出：

```
第 0 遍
第 1 遍
第 2 遍
第 3 遍
第 4 遍
```

### for 的三段式

`for` 括号里被两个分号分成三段：

```
for (初始化; 继续条件; 每轮更新) { ... }
```

- **初始化**：`int i = 0`，相当于"开始前先准备一个计数器，从 0 开始"。
- **继续条件**：`i < 5`，每轮开始前问一句"i 还小于 5 吗？"，是就继续，否则退出。
- **每轮更新**：`i++`，每轮结束后让 i 加 1（`i++` 就是 `i = i + 1` 的简写）。

生活类比：for 就像跑操场圈数。"从第 0 圈开始（初始化），不到 5 圈就继续跑（条件），每跑完一圈圈数加 1（更新）"。

### 改变范围和步长

```c
// 从 1 打印到 10
for (int i = 1; i <= 10; i++) {
    printf("%d ", i);
}
// 输出：1 2 3 4 5 6 7 8 9 10

// 只打印偶数
for (int i = 0; i <= 10; i += 2) {    // i 每次加 2
    printf("%d ", i);
}
// 输出：0 2 4 6 8 10
```

### 倒着数

```c
for (int i = 5; i >= 1; i--) {     // i-- 是 i = i - 1 的简写
    printf("%d ", i);
}
// 输出：5 4 3 2 1
```

## 3.2 while 循环：未知次数的重复

### 长什么样

```c
int n = 100;
while (n > 0) {        // 只要 n > 0 就一直做
    printf("%d\\n", n);
    n = n - 1;          // 别忘了让 n 变小，否则死循环
}
```

`while` 括号里只有一个条件：**条件为真就一直执行**，为假就退出。它没有"初始化"和"更新"的固定位置，所以这三件事你得自己写。

生活类比：while 像"只要没到目的地，就一直往前走"。你不在乎走多少步，只在乎条件。

### 什么时候用 while

- **次数已知**用 for 更清爽。
- **次数未知**（比如"一直读输入直到读到 0 为止"）用 while 更自然。

### 经典场景：读入到 0 停止

```c
int x, sum = 0;
scanf("%d", &x);
while (x != 0) {       // 只要读到的不是 0
    sum += x;           // 累加
    scanf("%d", &x);     // 继续读
}
printf("%d\\n", sum);
```

输入 `3 5 7 0` 会输出 `15`（3+5+7）。

## 3.3 do-while：先做再问

普通 while 是"先判断再做"，而 do-while 是"**先做一次，再判断要不要继续**"。

```c
int n;
do {
    scanf("%d", &n);
    printf("读到 %d\\n", n);
} while (n != 0);     // 注意结尾有分号
```

不管条件如何，**至少执行一次**。适合"先干一次再决定要不要再来"的场景。

## 3.4 break 和 continue：跳出与跳过

### break：提前跳车

```c
for (int i = 1; i <= 10; i++) {
    if (i == 5) {
        break;       // i 等于 5 时，立刻跳出整个循环
    }
    printf("%d ", i);
}
// 输出：1 2 3 4
```

break 像"按急停按钮"——立刻终止整个循环，不再继续。

### continue：这一轮跳过

```c
for (int i = 1; i <= 10; i++) {
    if (i % 2 == 0) {
        continue;    // 偶数：跳过这一轮的剩余语句
    }
    printf("%d ", i);  // 只打印奇数
}
// 输出：1 3 5 7 9
```

continue 像"这一圈不算，跳过它直接跑下一圈"。

## 3.5 实战：累加 1 到 100

```c
#include <stdio.h>

int main() {
    int sum = 0;                       // 用来存累加结果的盒子，先清零
    for (int i = 1; i <= 100; i++) {   // i 从 1 到 100
        sum = sum + i;                 // 把 i 加进 sum
    }
    printf("%d\\n", sum);               // 输出 5050
    return 0;
}
```

## 常见错误

1. **死循环**：忘写更新（`while (n > 0) { ... }` 里没有 `n--`），条件永远为真，程序停不下来，只能强制关闭。
2. **条件写错**：`for (int i = 0; i <= 5; i++)` 会循环 6 次（i = 0,1,2,3,4,5），如果你只想 5 次，应该写 `i < 5`。
3. **while 后加分号**：`while (n > 0);` 后面的分号让循环体是空语句，下面的代码块永远不执行。
4. **变量没初始化**：`int sum;` 不写 `= 0`，sum 里可能是垃圾值，结果不可预测。

## 本章要点

- `for` 适合**次数已知**的循环，三段式：初始化、条件、更新。
- `while` 适合**次数未知**的循环，条件为真就继续。
- `do-while` 至少执行一次。
- `break` 跳出整个循环，`continue` 跳过当前这一轮。
- 循环体里一定要有让条件"走向假"的更新，否则死循环。

## 动手试试

1. 用 for 打印 1 到 20 之间所有的偶数。
2. 用 while 读入若干整数，读到 0 停止，打印它们的平均值。
3. 想一想：下面这段代码会输出什么？为什么？
   ```c
   for (int i = 0; i < 5; i++);
       printf("%d ", i);
   ```
""", "数组求和"),

    ("第 4 章：数组", """# 第 4 章：数组

## 引入：从单个到批量

假设老师让你记全班 50 个同学的成绩。如果用普通变量，你得写 `int s1, s2, s3, ... s50;`，写到手酸。**数组**就是救星：它是一排**编了号的抽屉**，每个抽屉大小一样，名字统一，用编号区分。

```
arr[0]  arr[1]  arr[2]  arr[3]  arr[4]
 ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐
 │ 1 │   │ 2 │   │ 3 │   │ 4 │   │ 5 │
 └───┘   └───┘   └───┘   └───┘   └───┘
```

注意编号**从 0 开始**，这是 C（也是大多数编程语言）的铁律。50 个抽屉编号是 0 到 49。

## 4.1 声明数组

### 长什么样

```c
int arr[5];            // 声明 5 个装整数的抽屉
int scores[100];       // 100 个抽屉装成绩
char name[50];         // 50 个字符位置（用于字符串）
```

中括号里的数字是**抽屉数量**，必须在编译时确定。

### 声明时初始化

```c
int arr[5] = {1, 2, 3, 4, 5};   // 一次性给 5 个抽屉赋值
int b[5] = {0};                  // 第一个给 0，其余自动补 0（即全部为 0）
int c[] = {10, 20, 30};          // 编译器自动数出长度为 3
```

## 4.2 访问和修改

```c
int arr[5] = {10, 20, 30, 40, 50};
printf("%d\\n", arr[0]);     // 10（第 0 个抽屉）
printf("%d\\n", arr[4]);     // 50（最后一个）
arr[2] = 99;                 // 把第 2 个抽屉的内容改成 99
printf("%d\\n", arr[2]);     // 99
```

**中括号里的数字叫"下标"或"索引"**，从 0 开始。长度为 n 的数组，合法下标是 0 到 n-1。

## 4.3 从键盘读入 n 个数

```c
#include <stdio.h>

int main() {
    int n;
    scanf("%d", &n);            // 先读个数 n
    int arr[1000];              // 准备足够大的数组
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);   // 一个个读进数组
    }
    // 此时 arr[0] 到 arr[n-1] 已经填好
    return 0;
}
```

注意：`scanf("%d", &arr[i])` 里的 `&` 不能少——数组单个元素仍然是个普通变量，需要传地址。

## 4.4 遍历与求和

```c
int arr[5] = {1, 2, 3, 4, 5};
int sum = 0;
for (int i = 0; i < 5; i++) {
    sum += arr[i];              // 等价于 sum = sum + arr[i]
}
printf("和 = %d\\n", sum);       // 15
```

### 找最大值

```c
int arr[5] = {3, 7, 2, 9, 5};
int max = arr[0];               // 先假设第一个最大
for (int i = 1; i < 5; i++) {
    if (arr[i] > max) {
        max = arr[i];           // 发现更大的就更新
    }
}
printf("最大值 = %d\\n", max);    // 9
```

思路像"擂台赛"：第一个选手当擂主，后面的挨个上来比，谁赢了谁就当擂主，全部比完擂主就是最大值。

## 4.5 数组名是地址

C 语言有个特殊之处：**数组名本身代表首元素的地址**。所以下面两种写法等价：

```c
scanf("%s", s);        // s 是字符数组名，已经是地址，不加 &
scanf("%d", &arr[0]);  // 显式取第一个元素地址
```

但读单个元素时仍要 `&arr[i]`，因为 `arr[i]` 是一个具体的值，不是地址。这点容易混淆，记住规则：**数组名整体当地址用，单个元素 `arr[i]` 还是值，需要 `&`**。

## 常见错误

1. **数组越界**：声明 `int arr[5]` 却访问 `arr[5]` 或 `arr[10]`。C **不会**像 Python 那样报错，而是悄悄读写相邻内存，可能程序崩溃（段错误），也可能"看起来正常"但数据被破坏。这是最危险的 bug。
2. **越界写覆盖**：往越界位置写数据，可能把别的变量改了，导致程序出现莫名其妙的 bug。
3. **忘记 `&`**：`scanf("%d", arr[i])` 漏了 `&`，编译可能只警告，运行时崩溃。
4. **用变量定长度（旧标准）**：`int arr[n];` 在 C99 之前不允许（需要 VLA），保险起见开大数组如 `int arr[100000];`。

## 本章要点

- 数组是"一排编了号的抽屉"，下标从 **0** 开始。
- 长度为 n 的数组，合法下标范围是 `0` 到 `n-1`。
- 声明 `int arr[大小]`，访问 `arr[下标]`。
- 数组名单独使用时代表首元素地址，所以 `scanf("%s", s)` 不加 `&`。
- 越界访问不会报错但极危险，**自己保证下标不越界**。

## 动手试试

1. 读入 n 个整数，倒序输出它们（先打印最后一个，最后打印第一个）。
2. 读入 n 个整数，打印它们的平均值（注意用 `double` 避免 5 / 2 = 2 的问题）。
3. 想一想：如果数组大小是 10，你访问了 `arr[10]`，会发生什么？为什么"不报错"反而比"报错"更可怕？
""", "数组最大值"),

    ("第 5 章：字符串", """# 第 5 章：字符串

## 引入：C 里没有"字符串"这个类型

Python 有 `str`，Java 有 `String`，但 **C 语言没有专门的字符串类型**！那怎么办？C 用一排字符（`char` 数组）来表示字符串，并约定**用 `\\0` 这个特殊字符表示"字符串到此结束"**。这就是为什么字符串这一章如此重要——你必须理解 C 是怎么"手工"管理字符串的。

生活类比：C 的字符串像**一串手拉手的小朋友**，最后一个小朋友身后站着一位"结束标志员"（`\\0`），告诉大家"队列到这里为止"。

## 5.1 字符数组与 \\0 结尾

### 声明并初始化

```c
char s[10] = "hello";   // 字符数组存字符串
```

它在内存里实际长这样：

```
s[0] s[1] s[2] s[3] s[4] s[5]  s[6..9]
 'h'  'e'  'l'  'l'  'o'  '\\0'  ...
```

`"hello"` 是 5 个字符，但实际占用了 **6 个位置**，因为 C 自动在末尾补了一个 `\\0`。所以声明 `char s[10]` 装得下最多 9 个有效字符 + 1 个 `\\0`。

### 为什么需要 \\0？

因为 C 不知道字符串多长。每次要用字符串（比如打印它），程序就从第一个字符开始往后看，**直到遇到 `\\0` 才停下来**。如果没有 `\\0`，它会一直往后读，读到乱七八糟的内存，输出垃圾甚至崩溃。

## 5.2 输入和输出

### 用 scanf 读

```c
char s[100];
scanf("%s", s);          // 注意：s 不加 &，因为数组名本身是地址
printf("%s\\n", s);       // 输出读到的字符串
```

**重要陷阱**：`scanf("%s", s)` 读到**空格、制表符、换行**就停止。所以输入 `hello world` 只会读到 `hello`。

### 用 gets / fgets 读整行

如果想读一整行（包括空格），用 `fgets`：

```c
char s[100];
fgets(s, 100, stdin);    // 最多读 99 个字符 + \\0
```

`fgets` 会保留末尾的换行符 `\\n`。不推荐用老的 `gets`，因为它不检查长度，容易溢出。

### 输出

`printf("%s", s)` 会从 `s[0]` 一直打印到 `\\0` 为止。也可以逐字符用 `putchar`：

```c
for (int i = 0; s[i] != '\\0'; i++) {
    putchar(s[i]);
}
```

## 5.3 字符串长度：strlen

```c
#include <stdio.h>
#include <string.h>        // 用字符串函数必须 include 它

int main() {
    char s[] = "hello";
    int len = strlen(s);   // 长度 5（不含 \\0）
    printf("%d\\n", len);
    return 0;
}
```

`strlen` 返回的是**有效字符个数**，**不包括**末尾的 `\\0`。`"hello"` 的 strlen 是 5，但实际占内存 6 个字节。

## 5.4 字符串反转：完整例子

```c
#include <stdio.h>
#include <string.h>

int main() {
    char s[1000];
    scanf("%s", s);               // 读一个单词
    int n = strlen(s);            // 算出长度
    for (int i = n - 1; i >= 0; i--) {   // 从最后一个字符往前
        putchar(s[i]);
    }
    putchar('\\n');                 // 最后换行
    return 0;
}
```

输入 `abcde` 输出 `edcba`。注意循环从 `n-1` 开始（最后一个有效字符），到 0 结束，**不要碰 `\\0`**。

## 5.5 常用字符串函数

需要 `#include <string.h>`：

| 函数 | 作用 | 例子 |
|------|------|------|
| `strlen(s)` | 字符串长度 | `strlen("abc")` → 3 |
| `strcmp(a, b)` | 比较两个字符串 | 相等返回 0 |
| `strcpy(dst, src)` | 把 src 复制到 dst | `strcpy(s, "hi")` |
| `strcat(dst, src)` | 把 src 拼到 dst 后面 | `strcat(s, "!")` |
| `strchr(s, c)` | 在 s 中找字符 c | 返回地址或 NULL |

**比较字符串不能用 `==`**！`s == "hello"` 比较的是地址，不是内容。要用 `strcmp(s, "hello") == 0` 判断相等。

## 常见错误

1. **忘记 `\\0` 结尾**：自己一个字符一个字符地填字符数组，没在末尾放 `\\0`，结果 `printf` 或 `strlen` 越读越远。
2. **数组太小**：声明 `char s[5]` 却读 `hello`（5 个字符 + `\\0` 需要 6 字节），发生越界写。
3. **`scanf` 读带空格的字符串**：用 `%s` 读 `hello world` 只得到 `hello`。读整行用 `fgets`。
4. **用 `==` 比字符串**：`if (s == "yes")` 永远不会成立（比的是地址）。要用 `strcmp`。
5. **忘记 `#include <string.h>`**：用了 `strlen` 但没引入头文件，编译报错。

## 本章要点

- C 没有字符串类型，用 `char` 数组 + `\\0` 表示字符串。
- 字符串末尾必须有 `\\0`，否则函数会一直读到越界。
- `scanf("%s", s)` 遇空格停止，读整行用 `fgets(s, 大小, stdin)`。
- `strlen` 返回有效长度（不含 `\\0`）。
- 比较字符串用 `strcmp`，**不能**用 `==`。
- 用字符串函数要 `#include <string.h>`。

## 动手试试

1. 读入一个单词（不含空格），打印它的长度。
2. 读入一个单词，把它**反转**后输出。
3. 想一想：`char s[5] = "hello";` 这行代码有什么问题？为什么应该写成 `char s[6]`？
""", "字符串反转"),

    ("第 6 章：函数", """# 第 6 章：函数

## 引入：菜谱与函数

你吃过方便面吗？包装上有"菜谱"——烧水、放面、煮 3 分钟、放调料、拌匀。如果你每次煮面都要从头描述这些步骤，太啰嗦了。**函数**就是程序里的"菜谱"：你把一段会重复使用的步骤打包起来，起个名字，以后想用就"喊一声名字"，不必每次重写。

生活类比：函数像**榨汁机**。你把"苹果"和"糖"（参数）丢进去，它吐出"苹果汁"（返回值）。中间怎么榨，你不用关心，你只关心丢什么进去、得到什么出来。

## 6.1 函数长什么样

### 一个简单例子

```c
#include <stdio.h>

// 定义一个函数：求两个整数的和
int add(int a, int b) {
    return a + b;
}

int main() {
    int result = add(3, 5);      // 调用函数
    printf("%d\\n", result);       // 输出 8
    return 0;
}
```

### 拆解函数的四个部分

```
返回类型  函数名(参数类型 参数名, ...) {
    int     add   (int a, int b)        {
```

- **返回类型** `int`：函数吐出来的是个什么类型的东西。`int` 表示整数。如果不返回任何东西，写 `void`。
- **函数名** `add`：你给它起的名字，调用时用它。
- **参数列表** `(int a, int b)`：丢进函数的原材料，每个参数要有类型和名字。
- **函数体** `{ return a + b; }`：花括号里是具体怎么做。`return` 把结果送出来，函数就结束了。

### 调用函数

`add(3, 5)` 就是"喊一声名字，把 3 和 5 丢进去"。它会返回 8，你可以把返回值赋给变量、直接打印、或参与运算。

## 6.2 为什么需要函数

### 避免重复

```c
// 没有函数：算三组平方和要写三遍
printf("%d\\n", 3*3 + 4*4);
printf("%d\\n", 5*5 + 6*6);
printf("%d\\n", 7*7 + 8*8);

// 有函数：写一遍，用三遍
int sumSquares(int x, int y) {
    return x * x + y * y;
}
printf("%d\\n", sumSquares(3, 4));
printf("%d\\n", sumSquares(5, 6));
printf("%d\\n", sumSquares(7, 8));
```

### 让程序更清晰

复杂程序拆成多个函数，每个函数只做一件事，像积木一样拼起来，读起来轻松，改起来也方便。

## 6.3 参数按值传递

C 默认是**按值传递**——函数拿到的是参数的**复印件**，不是原件。修改形参不会影响外面。

```c
void tryChange(int x) {
    x = 100;          // 只改了复印件
}

int main() {
    int a = 5;
    tryChange(a);
    printf("%d\\n", a);  // 还是 5，没变
    return 0;
}
```

就像你把作业复印一份给同学，同学在复印件上乱涂，你的原件不受影响。

### 想真改怎么办？用指针

```c
void realChange(int *p) {
    *p = 100;          // 通过地址改"原件"
}

int main() {
    int a = 5;
    realChange(&a);    // 把 a 的地址传进去
    printf("%d\\n", a);  // 100
    return 0;
}
```

这里用到指针（下一章详讲），思路是：把"门牌号"传给函数，函数顺着门牌号找到原件，直接改。这正是 `scanf` 要加 `&` 的原因——它要修改你的变量，所以需要地址。

## 6.4 函数声明与定义分离

如果函数定义写在 `main` 后面，编译器从上往下读，遇到 `add(3,5)` 时还不认识 `add`，会报警告。解决办法是**先声明（原型）后定义**：

```c
#include <stdio.h>

int add(int a, int b);   // 函数原型：告诉编译器"有这个函数"

int main() {
    printf("%d\\n", add(3, 5));
    return 0;
}

int add(int a, int b) {   // 真正的定义
    return a + b;
}
```

声明只写"长什么样"（返回类型、名字、参数类型），不写函数体，结尾加分号。定义才写完整的函数体。一般把声明放在文件开头，定义放在后面或别的文件里。

## 6.5 没有 return 的函数：void

```c
void greet() {
    printf("Hello!\\n");
    // 没有 return，因为不需要返回东西
}

int main() {
    greet();     // 直接调用，不接返回值
    return 0;
}
```

`void` 表示"空"，意思是这个函数不返回任何东西。它只是"做事"（比如打印），不"吐出"结果。

## 常见错误

1. **函数定义在调用之后**：编译器还没看到函数就调用，会警告或报错。要么调换顺序，要么先写原型声明。
2. **忘记 return**：声明返回 `int` 但函数体里没写 `return`，会返回垃圾值。
3. **参数类型不匹配**：函数要 `int`，你传 `double`，可能丢精度或编译警告。
4. **以为能修改形参影响实参**：默认按值传递，改不了原变量。要改原件必须用指针。
5. **return 之后还写代码**：`return` 一执行函数立刻结束，后面写的代码永远不执行。

## 本章要点

- 函数 = 菜谱，把一段逻辑打包成可复用的"黑盒"。
- 函数有四部分：返回类型、函数名、参数列表、函数体。
- C 默认**按值传递**，形参是实参的复印件，修改形参不影响实参。
- 要修改外部变量，必须传它的**地址**（用指针）。
- 函数声明（原型）放在前，定义可以放后面。
- `void` 表示不返回东西。

## 动手试试

1. 写一个函数 `int max(int a, int b)`，返回两个数中较大的那个。在 main 里读入两个数调用它并打印。
2. 写一个函数 `void printStars(int n)`，打印 n 个星号。在 main 里调用它打印 5 个星号。
3. 想一想：下面这个函数能改变 `a` 的值吗？为什么？
   ```c
   void change(int x) { x = 999; }
   ```
""", None),

    ("第 7 章：嵌套循环", """# 第 7 章：嵌套循环

## 引入：循环里套循环

普通循环像"绕操场跑 5 圈"。**嵌套循环**像"跑 5 圈，每跑一圈做 10 个俯卧撑"——外层每走一步，内层完整跑一遍。这是处理"二维问题"（表格、图案、矩阵）的利器。

生活类比：嵌套循环像**走座位表点名**。外层循环逐行（i），内层循环在该行逐列（j）。全班 30 人坐 5 行 6 列，外层 5 次、内层 6 次，共点名 30 次。

## 7.1 双层循环打印坐标

### 长什么样

```c
#include <stdio.h>

int main() {
    for (int i = 0; i < 3; i++) {           // 外层：行
        for (int j = 0; j < 3; j++) {       // 内层：列
            printf("(%d,%d) ", i, j);
        }
        printf("\\n");                        // 一行结束，换行
    }
    return 0;
}
```

输出：

```
(0,0) (0,1) (0,2)
(1,0) (1,1) (1,2)
(2,0) (2,1) (2,2)
```

### 执行过程

- 外层 `i = 0`：内层 j 从 0 跑到 2，打印三个坐标，然后换行。
- 外层 `i = 1`：内层**完整再跑一遍**。
- 外层 `i = 2`：内层再跑一遍。

关键点：**内层循环完整跑一轮，外层才前进一步**。总次数 = 外层次数 × 内层次数，这里 3 × 3 = 9 次。

## 7.2 打印图案：直角三角形

```c
#include <stdio.h>

int main() {
    int n = 5;
    for (int i = 1; i <= n; i++) {          // 第 i 行
        for (int j = 1; j <= i; j++) {      // 打印 i 个星号
            printf("*");
        }
        printf("\\n");
    }
    return 0;
}
```

输出：

```
*
**
***
****
*****
```

**关键思路**：第 i 行要打印 i 个星号，所以内层循环的上限设成 `i`，让内层次数随行号变化。

## 7.3 打印九九乘法表

```c
#include <stdio.h>

int main() {
    for (int i = 1; i <= 9; i++) {
        for (int j = 1; j <= i; j++) {
            printf("%d*%d=%d ", j, i, i * j);
        }
        printf("\\n");
    }
    return 0;
}
```

输出：

```
1*1=1
1*2=2 2*2=4
1*3=3 2*3=6 3*3=9
...
```

每行打印的项数随 i 变化，行号既是"被乘数"也控制内层范围。

## 7.4 冒泡排序：经典应用

### 思路

冒泡排序像"水里的气泡"——大的数字像大气泡，会一步步浮到最后。每一轮从头到尾两两比较，如果前一个比后一个大，就交换，这样一轮下来最大的就到了末尾。下一轮就少比一个。

### 代码

```c
#include <stdio.h>

int main() {
    int n;
    scanf("%d", &n);
    int a[1000];
    for (int i = 0; i < n; i++) {
        scanf("%d", &a[i]);
    }

    // 冒泡排序
    for (int i = 0; i < n; i++) {                 // 外层：共 n 轮
        for (int j = 0; j < n - i - 1; j++) {     // 内层：每轮少比 i 个
            if (a[j] > a[j + 1]) {                // 前面大于后面
                int t = a[j];                     // 交换三步
                a[j] = a[j + 1];
                a[j + 1] = t;
            }
        }
    }

    for (int i = 0; i < n; i++) {
        printf("%d ", a[i]);
    }
    printf("\\n");
    return 0;
}
```

### 为什么内层是 `n - i - 1`？

因为第 i 轮结束时，最大的 i+1 个数已经"沉"到最后 i+1 个位置，下一轮不用再比较它们。所以内层循环上限是 `n - i - 1`。

### 交换为什么需要临时变量？

`a[j] = a[j+1]` 会先把 `a[j]` 覆盖掉，原值就丢了。所以得先用临时变量 `t` 把 `a[j]` 的值保存下来。这是 C（不像 Python 有 `a, b = b, a` 的语法）的规矩：交换两个值要用三个变量。

## 常见错误

1. **忘记换行**：内层循环结束后不写 `printf("\\n")`，所有内容挤在一行。
2. **内层范围搞错**：冒泡排序内层写成 `j < n` 而不是 `n - i - 1`，结果不会出错但会多做无用的比较。
3. **交换不用临时变量**：`a[j] = a[j+1]; a[j+1] = a[j];` 结果两个都变成同一个值。
4. **内外层用同一个变量**：内层外层都用 `i`，逻辑混乱，永远不会正常循环。

## 本章要点

- 嵌套循环：外层走一步，内层完整跑一轮。总次数 = 外层次数 × 内层次数。
- 打印图案：外层控制行，内层控制每行内容。
- 冒泡排序：每轮把最大的"浮"到末尾，内层范围 `n - i - 1`。
- 交换两个值要用临时变量。
- 内层循环结束后记得换行（如果要按行打印）。

## 动手试试

1. 打印一个 n×n 的正方形星号阵（n 行 n 列全是 `*`）。
2. 打印九九乘法表（参考 7.3，但尝试打印完整的 9 行 9 列版，而不是三角形）。
3. 想一想：下面这段代码会打印多少个 `x`？
   ```c
   for (int i = 0; i < 4; i++)
       for (int j = 0; j < 3; j++)
           printf("x");
   ```
""", "冒泡排序"),

    ("第 8 章：递归", """# 第 8 章：递归

## 引入：函数自己叫自己

**递归**就是"函数在自己内部调用自己"。听起来很玄，其实生活里到处都是：你站在队伍里想知道自己排第几，你问前面的人"你排第几"，他再问前面的人……直到问到第一个人（他知道自己排第 1），然后答案一层层传回来。

生活类比：递归像**俄罗斯套娃**。打开一个娃，里面是个更小的娃，再打开……直到最小的那个不能再打开（这就是"出口"），然后一层层合上。

## 8.1 递归的两个核心

写递归必须有两部分，缺一不可：

1. **递归出口（base case）**：什么时候停下来。没有出口，函数会无限调用自己，最终栈溢出崩溃。
2. **递归步骤**：把问题变小一点，再交给"自己"处理。每次调用，问题规模必须**向出口靠近**。

## 8.2 阶乘：递归的经典例子

### 什么是阶乘

`n! = n × (n-1) × (n-2) × ... × 2 × 1`，比如 `5! = 5×4×3×2×1 = 120`。约定 `0! = 1`、`1! = 1`。

### 用递归怎么想

观察：`5! = 5 × 4!`，`4! = 4 × 3!`……也就是 `n! = n × (n-1)!`。这就是递归步骤——把 n! 的问题变成 (n-1)! 的问题。当 n 是 0 或 1 时，结果是 1，这就是出口。

### 代码

```c
#include <stdio.h>

long long factorial(int n) {
    if (n <= 1) return 1;             // 出口：0! 和 1! 都是 1
    return n * factorial(n - 1);      // 步骤：n! = n × (n-1)!
}

int main() {
    int n;
    scanf("%d", &n);
    printf("%lld\\n", factorial(n));    // 注意 long long 用 %lld
    return 0;
}
```

### 执行过程（n=3 时）

```
factorial(3)
  → 3 * factorial(2)
         → 2 * factorial(1)
                → 1        （出口）
         → 2 * 1 = 2
  → 3 * 2 = 6
```

调用一层层深入，直到撞上出口，再一层层返回结果。每深入一层，n 都变小，所以必然能到达出口。

### 为什么用 `long long`

阶乘增长非常快：`13!` 就超过 `int` 的范围（约 21 亿）。所以用 `long long`（最大约 922 亿亿），打印时格式符是 `%lld`。

## 8.3 斐波那契数列

### 定义

斐波那契数列：`1, 1, 2, 3, 5, 8, 13, 21, ...`，规则是每个数等于前两个数之和：

```
fib(1) = 1
fib(2) = 1
fib(n) = fib(n-1) + fib(n-2)   （n > 2）
```

### 代码

```c
#include <stdio.h>

int fib(int n) {
    if (n <= 2) return 1;                  // 出口：前两项都是 1
    return fib(n - 1) + fib(n - 2);        // 步骤：前两项之和
}

int main() {
    int n;
    scanf("%d", &n);
    printf("%d\\n", fib(n));
    return 0;
}
```

### 注意：递归斐波那契效率很低

`fib(5)` 会算 `fib(4) + fib(3)`，`fib(4)` 又算 `fib(3) + fib(2)`，`fib(3)` 被算了两次。n 越大重复越严重，n=40 就会慢得明显。学习递归用它没问题，实际工程会用循环或"记忆化"优化。

## 8.4 递归 vs 循环

任何递归都能改写成循环，反之亦然。怎么选？

- **递归**：思路清晰、贴近问题定义（像数学公式），适合树形、分治问题。
- **循环**：效率高、没栈溢出风险，适合简单重复。

| 方面 | 递归 | 循环 |
|------|------|------|
| 可读性 | 像数学公式，清晰 | 有时要写复杂状态 |
| 效率 | 调用有开销，可能重复计算 | 高 |
| 风险 | 太深会栈溢出 | 不会 |

## 常见错误

1. **忘记写递归出口**：函数无限调用自己，最终栈溢出（程序崩溃，报 `Segmentation fault` 或 `Stack overflow`）。
2. **递归步骤不向出口靠近**：`return n * factorial(n)`（不是 `n-1`），n 永远不变，永远到不了出口。
3. **大数不用 `long long`**：算阶乘 `13!` 就 `int` 溢出，结果变成负数或乱码。
4. **参数顺序搞错**：写 `fib(n - 2) + fib(n - 1)` 不会出错，但容易在更复杂的递归里写错。

## 本章要点

- 递归 = 函数调用自己，必须有两部分：**出口**和**递归步骤**。
- 每次递归调用，问题规模必须向出口靠近。
- 阶乘：`n! = n × (n-1)!`，出口 `n <= 1` 返回 1。
- 斐波那契：`fib(n) = fib(n-1) + fib(n-2)`，出口 `n <= 2` 返回 1。
- 大数要用 `long long`，打印用 `%lld`。
- 递归比循环易读但效率低，太深会栈溢出。

## 动手试试

1. 用递归求 1+2+3+...+n 的和。（提示：`sum(n) = n + sum(n-1)`，出口 `n == 1` 返回 1。）
2. 用递归打印从 1 到 n 的所有整数。
3. 想一想：如果写 `int f(int n) { return f(n); }`，会发生什么？为什么？
""", "计算阶乘"),

    ("第 9 章：指针", """# 第 9 章：指针

## 引入：门牌号与房子

学 C 语言，"指针"是绕不过去的一关。别怕，它的核心其实很简单。

生活类比：城市里有很多**房子**（变量），每个房子都有**门牌号**（地址）。你找人，要么直接去他家（用变量名），要么告诉他门牌号让他自己找（用指针）。**指针就是"门牌号"**——它存的不是数据本身，而是数据"住在哪里"。

```
内存地址    内存内容        变量名
  1004  ┌──────────┐
        │   ...    │
  1000  │   10     │   ←  x（这里住着整数 10）
        └──────────┘
```

如果 `x` 住在地址 1000，那么"指向 x 的指针"就是一张写着"1000"的纸条。

## 9.1 取地址 `&` 和解引用 `*`

### 两个最重要的符号

- `&` 变量名：**取地址**，得到这个变量的"门牌号"。
- `*` 指针：**解引用**，顺着门牌号找到那个房子，取出里面的内容。

### 长什么样

```c
#include <stdio.h>

int main() {
    int x = 10;
    int *p = &x;          // p 是"指向 int 的指针"，存 x 的地址
    printf("%d\\n", *p);   // 顺着 p 找到 x，输出 10
    *p = 99;              // 通过 p 修改 x 的内容
    printf("%d\\n", x);    // 99，x 被改了
    return 0;
}
```

### 逐行解释

- `int *p = &x;`：声明一个"指向 int 的指针"变量 `p`，把 `x` 的地址赋给它。`int *` 是类型，意思是"指向 int 的指针"。
- `*p`：顺着 p 里存的地址找到那个变量，得到它的值。这就是"解引用"。
- `*p = 99;`：通过指针间接修改 `x`。从此 x 不再是 10，变成 99。

### `*` 在不同位置含义不同

新手最容易混淆 `*` 的两个意思：

- 声明时（`int *p;`）：`*` 是"我是个指针"的标志。
- 使用时（`*p = 99;`）：`*` 是"顺着地址找到那个变量"。

记住口诀：**声明时是身份，使用时是动作**。

## 9.2 为什么需要指针

你可能会问：直接用 `x` 不就行了，干嘛绕一圈？答案在上一章——**让函数能修改外部变量**。

### 例子：写一个交换函数

C 默认按值传递，函数里改的是复印件：

```c
void swapWrong(int a, int b) {     // 收到的是复印件
    int t = a; a = b; b = t;        // 只交换了复印件
}

int main() {
    int x = 3, y = 5;
    swapWrong(x, y);
    printf("%d %d\\n", x, y);        // 还是 3 5，没交换
    return 0;
}
```

### 用指针就能真改

```c
void swap(int *a, int *b) {         // 接收地址
    int t = *a;
    *a = *b;
    *b = t;
}

int main() {
    int x = 3, y = 5;
    swap(&x, &y);                    // 把门牌号传进去
    printf("%d %d\\n", x, y);         // 5 3，真的交换了
    return 0;
}
```

思路：把"门牌号"传给函数，函数顺着门牌号找到原房子，直接改。这正是 `scanf` 要加 `&` 的原因——`scanf` 要修改你的变量，所以需要它的地址。

## 9.3 指针与数组：天生一对

C 里有个重要事实：**数组名本身就是首元素的地址**。

```c
int arr[5] = {10, 20, 30, 40, 50};
int *p = arr;               // arr 自动退化成 &arr[0]
printf("%d\\n", *p);          // 10（首元素）
printf("%d\\n", *(p + 2));    // 30（第 2 个元素）
```

### 指针加减的"聪明"之处

`p + 2` 不是地址加 2 个字节，而是**自动按元素大小偏移**。如果 `int` 是 4 字节，`p + 2` 实际跳了 8 字节，正好到第 3 个元素。所以下面两行等价：

```c
arr[2]        // 用下标
*(p + 2)      // 用指针算
```

C 内部其实就把 `arr[i]` 翻译成 `*(arr + i)`。数组下标是指针的语法糖。

## 9.4 用指针遍历数组

```c
int arr[5] = {1, 2, 3, 4, 5};
for (int *p = arr; p < arr + 5; p++) {
    printf("%d ", *p);
}
// 输出：1 2 3 4 5
```

`p++` 让指针前进一个元素的位置，每次循环 `*p` 取当前元素。等价于用下标 `arr[i]`，但更"底层"。

## 9.5 看地址长什么样

可以用 `%p` 打印指针（地址）：

```c
int x = 10;
printf("%p\\n", (void*)&x);   // 输出类似 0x7ffeec1a3b1c
```

不同机器地址不同，但都是这种十六进制形式。

## 常见错误

1. **指针没初始化就用**：`int *p; *p = 10;`，p 指向随机地址，写入会段错误。声明指针时要么赋初值，要么先赋 NULL。
2. **返回局部变量地址**：函数返回一个局部变量的指针，函数结束后那块内存被回收，再用就是野指针。
3. **混淆 `&` 和 `*`**：`&` 是取地址（拿到门牌号），`*` 是解引用（顺着门牌号找内容）。
4. **越界访问**：指针加减跳过了数组范围，继续读写就越界了，C 不检查。
5. **类型不匹配**：`double *p = &intVar;` 类型不对，解引用会读到错误数据。

## 本章要点

- 指针是"门牌号"，存的是变量的地址，不是变量本身。
- `&` 取地址，`*` 解引用（顺着地址取内容）。
- `int *p` 声明指针，`*p` 使用指针。
- 函数要修改外部变量必须传地址（这就是 `scanf` 要 `&` 的原因）。
- 数组名就是首元素地址，`arr[i]` 等价于 `*(arr + i)`。
- 指针没初始化就用是常见崩溃原因。

## 动手试试

1. 声明一个 `int` 变量，用指针修改它的值为 100，再打印变量确认。
2. 写一个 `void addOne(int *p)` 函数，把 p 指向的变量加 1。在 main 里调用它。
3. 想一想：为什么下面这个函数不能改变 main 里的 `x`？
   ```c
   void addOne(int x) { x = x + 1; }
   ```
""", None),

    ("第 10 章：结构体", """# 第 10 章：结构体

## 引入：把信息打包

假设你要管理学生档案：每个学生有姓名、年龄、成绩、班级……。如果用一堆普通变量，得写 `char name1[50], name2[50], ...; int age1, age2, ...;`，乱成一锅粥。**结构体（struct）**就是把这些相关信息**打包在一起**，变成一张"档案卡"——一个学生用一张卡，整整齐齐。

生活类比：结构体像**一张档案卡**。卡上有姓名栏、年龄栏、成绩栏，每个栏目叫一个"成员"。一张卡代表一个学生，一摞卡就是全班。

```
┌─────────────┐
│ 学生档案卡   │
├─────────────┤
│ 姓名: Alice  │  ← 成员 name
│ 年龄: 12     │  ← 成员 age
│ 成绩: 95     │  ← 成员 score
└─────────────┘
```

## 10.1 定义结构体

### 长什么样

```c
struct Student {
    char name[50];     // 成员1：姓名（字符串）
    int age;           // 成员2：年龄
    int score;         // 成员3：成绩
};
```

注意结尾的**分号**！结构体定义的花括号后必须有 `;`，漏了会报错。

### 这只是"设计图"

定义 `struct Student` 只是告诉编译器"档案卡长什么样"，**还没真正造出一张卡**。就像建筑师画好图纸，但还没动工。要真正使用，得声明一个"具体的学生"。

## 10.2 声明和使用结构体变量

### 创建一张卡

```c
struct Student s1 = {"Alice", 12, 95};   // 创建并初始化
struct Student s2;                       // 先创建
strcpy(s2.name, "Bob");                   // 再填内容
s2.age = 13;
s2.score = 88;
```

### 用 `.` 访问成员

结构体变量后面加点 `.` 再写成员名，就能读写那个成员：

```c
printf("%s\\n", s1.name);        // Alice
printf("%d\\n", s1.score);      // 95
s1.score = 100;                  // 修改成绩
printf("%d\\n", s1.score);       // 100
```

`.` 就像"翻开档案卡的某一栏"。

## 10.3 完整可运行示例

```c
#include <stdio.h>
#include <string.h>          // 用 strcpy 需要 include

struct Student {
    char name[50];
    int age;
    int score;
};

int main() {
    struct Student s;
    strcpy(s.name, "Alice");   // 给字符串成员赋值要用 strcpy，不能直接 =
    s.age = 12;
    s.score = 95;
    printf("%s %d岁 成绩 %d\\n", s.name, s.age, s.score);
    return 0;
}
```

### 为什么字符串不能直接赋值

`s.name = "Alice"` 在 C 里**不行**！因为 `name` 是数组，数组名是地址常量，不能赋值。要复制字符串要用 `strcpy(s.name, "Alice")`，它把右边的字符一个一个复制进 `name` 数组。

## 10.4 结构体数组：管理全班

实际场景里你不会只管一个学生。结构体数组就是"一摞档案卡"。

### 读入并打印多个学生

```c
#include <stdio.h>

struct Student {
    char name[50];
    int score;
};

int main() {
    int n;
    scanf("%d", &n);
    struct Student students[100];         // 100 张卡

    for (int i = 0; i < n; i++) {
        scanf("%s %d", students[i].name, &students[i].score);
        // name 是数组名，本身就是地址，不加 &
        // score 是普通 int，必须加 &
    }

    for (int i = 0; i < n; i++) {
        printf("%s: %d\\n", students[i].name, students[i].score);
    }
    return 0;
}
```

### 注意 `&` 的区别

`students[i].name` 是字符数组名，本身是地址，所以不加 `&`。
`students[i].score` 是普通 int，必须加 `&` 取地址。
这规律和普通数组一样：**数组名当地址用，单个变量要 `&`**。

## 10.5 结构体指针与 `->`

如果用指针指向结构体，访问成员要用 `->` 而不是 `.`：

```c
struct Student s = {"Alice", 12, 95};
struct Student *p = &s;          // p 指向 s
printf("%s\\n", p->name);        // 用 -> 访问成员
printf("%d\\n", (*p).score);     // 也可以这样写，等价于 p->score
```

`p->name` 是 `(*p).name` 的简写。记住口诀：**指针用箭头 `->`，变量用点 `.`**。

## 10.6 结构体做函数参数

函数接收结构体时，默认也是**按值传递**（复印一张卡给函数）。修改复印件不影响原件。要修改原件就传指针。

```c
void printStudent(struct Student s) {      // 收到复印件
    printf("%s: %d\\n", s.name, s.score);
}

void addBonus(struct Student *p) {         // 收到地址
    p->score += 5;                          // 直接改原件
}
```

## 常见错误

1. **定义结构体忘加分号**：`struct Student { ... };` 结尾必须有 `;`。
2. **字符串成员直接赋值**：`s.name = "Alice"` 不行，要用 `strcpy`。
3. **混用 `.` 和 `->`**：变量用 `.`，指针用 `->`，搞反会报错。
4. **结构体数组越界**：`struct Student arr[10];` 但访问 `arr[10]`，越界访问 C 不检查。
5. **scanf 忘记 `&`**：结构体成员里只有 char 数组名不加 `&`，其他成员都要加。

## 本章要点

- 结构体是"档案卡"，把多个相关变量打包成一个整体。
- 先定义类型 `struct Student { ... };`，再声明变量 `struct Student s;`。
- 用 `变量名.成员名` 访问成员；指针用 `->`。
- 字符串成员赋值要用 `strcpy`，不能直接用 `=`。
- 结构体数组管理多条记录，是组织数据的利器。
- 结构体做函数参数默认按值传递，要改原件就传指针。

## 动手试试

1. 定义一个 `struct Point` 有两个 `int` 成员 x 和 y，读入一个点并打印。
2. 定义一个 `struct Student` 包含姓名和成绩，读入 n 个学生，打印成绩最高的那个学生的姓名。
3. 想一想：为什么 `s.name = "Bob"` 不行，而 `strcpy(s.name, "Bob")` 可以？查一查 `strcpy` 的工作原理。
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
