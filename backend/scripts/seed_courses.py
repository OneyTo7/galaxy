"""预设课程 + 题目种子脚本。

三套"从入门到精通"课程，每套 8-10 道题，按难度递增。
每题都打 Q 矩阵知识点标签，接入 BKT 掌握度系统。

用法：
    cd backend && source .venv/bin/activate
    MOCK=1 python scripts/seed_courses.py              # 幂等
    MOCK=1 python scripts/seed_courses.py --reset       # 清空预设课程后重建
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.contexts.assignment.models import Assignment, TestCase
from app.contexts.mastery.models import AssignmentKnowledgePoint, KnowledgePoint
from app.contexts.organization.models import Class, Course, Enrollment
from app.contexts.user.models import User
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password

# ── 题目定义 ──────────────────────────────────────────────
# 每道题：(title, description, lang, test_cases, scoring_rubric, reference_code, knowledge_point_codes)
# test_cases: [(name, input, expected_output, is_hidden, weight)]

PYTHON_COURSE = [
    ("两数之和", "输入两个空格分隔的整数，输出它们的和。", [
        ("基本", "5 3", "8", False, 1),
        ("负数", "-1 4", "3", True, 1),
        ("零", "0 0", "0", True, 1),
    ], "正确性 100%", "a, b = map(int, input().split())\nprint(a + b)", ["input-parse", "type-conversion"]),

    ("数组求和", "第一行输入 n，第二行输入 n 个空格分隔的整数，输出它们的和。", [
        ("基本", "3\n1 2 3", "6", False, 1),
        ("单元素", "1\n5", "5", False, 1),
        ("空数组", "0\n", "0", True, 1),
        ("负数", "3\n-1 -2 -3", "-6", True, 2),
    ], "正确性 80% + 边界 20%", "n = int(input())\narr = list(map(int, input().split())) if n > 0 else []\nprint(sum(arr))", ["loop-boundary", "empty-input"]),

    ("数组最大值", "第一行输入 n，第二行输入 n 个整数，输出最大值。", [
        ("基本", "3\n1 5 3", "5", False, 1),
        ("负数", "3\n-1 -5 -3", "-1", True, 1),
        ("单元素", "1\n7", "7", False, 1),
    ], "正确性 100%", "n = int(input())\narr = list(map(int, input().split()))\nprint(max(arr))", ["array-traversal", "edge-case"]),

    ("数组元素加倍", "第一行输入 n，第二行输入 n 个整数，每个元素乘以 2 后输出，空格分隔。", [
        ("基本", "3\n1 2 3", "2 4 6", False, 1),
        ("单元素", "1\n5", "10", False, 1),
        ("含零", "3\n0 1 2", "0 2 4", True, 1),
    ], "正确性 100%", "n = int(input())\narr = list(map(int, input().split()))\nprint(' '.join(str(x * 2) for x in arr))", ["loop-termination", "output-format"]),

    ("判断奇偶", "输入一个整数，奇数输出 odd，偶数输出 even。", [
        ("偶数", "4", "even", False, 1),
        ("奇数", "7", "odd", False, 1),
        ("零", "0", "even", True, 1),
    ], "正确性 100%", "n = int(input())\nprint('odd' if n % 2 else 'even')", ["boolean-logic", "type-conversion"]),

    ("字符串反转", "输入一个字符串，输出其反转。", [
        ("基本", "hello", "olleh", False, 1),
        ("单字符", "a", "a", False, 1),
        ("空串", "", "", True, 1),
    ], "正确性 100%", "s = input()\nprint(s[::-1])", ["string-slice", "empty-input"]),

    ("成绩等级判定", "输入一个 0-100 的分数，输出等级：>=90 为 A，>=80 为 B，>=60 为 C，否则 D。", [
        ("A", "95", "A", False, 1),
        ("B", "85", "B", False, 1),
        ("C", "65", "C", False, 1),
        ("D", "45", "D", False, 1),
        ("边界90", "90", "A", True, 1),
        ("边界60", "60", "C", True, 1),
    ], "正确性 100%", "s = int(input())\nif s >= 90: print('A')\nelif s >= 80: print('B')\nelif s >= 60: print('C')\nelse: print('D')", ["boolean-logic", "edge-case"]),

    ("冒泡排序", "第一行输入 n，第二行输入 n 个整数，输出升序排列，空格分隔。", [
        ("基本", "4\n3 1 4 2", "1 2 3 4", False, 1),
        ("已排序", "3\n1 2 3", "1 2 3", True, 1),
        ("逆序", "3\n3 2 1", "1 2 3", True, 1),
    ], "正确性 100%", "n = int(input())\narr = list(map(int, input().split()))\nfor i in range(n):\n  for j in range(n - i - 1):\n    if arr[j] > arr[j + 1]: arr[j], arr[j + 1] = arr[j + 1], arr[j]\nprint(' '.join(map(str, arr)))", ["nested-loop", "array-traversal"]),

    ("计算阶乘", "输入非负整数 n，输出 n 的阶乘。", [
        ("基本", "5", "120", False, 1),
        ("零", "0", "1", False, 1),
        ("较大", "10", "3628800", True, 2),
    ], "正确性 100%", "n = int(input())\nprint(1 if n == 0 else __import__('math').prod(range(1, n + 1)))", ["recursion-exit", "edge-case"]),

    ("矩阵转置", "第一行输入 m n，随后 m 行每行 n 个整数，输出转置矩阵（n 行 m 列），空格分隔。", [
        ("基本", "2 3\n1 2 3\n4 5 6", "1 4\n2 5\n3 6", False, 1),
        ("单行", "1 3\n1 2 3", "1\n2\n3", True, 1),
    ], "正确性 100%", "m, n = map(int, input().split())\nmat = [list(map(int, input().split())) for _ in range(m)]\nfor j in range(n):\n  print(' '.join(str(mat[i][j]) for i in range(m)))", ["nested-loop", "array-index"]),
]

JAVA_COURSE = [
    ("两数之和", "输入两个空格分隔的整数，输出它们的和。", [
        ("基本", "5 3", "8", False, 1),
        ("负数", "-1 4", "3", True, 1),
        ("零", "0 0", "0", True, 1),
    ], "正确性 100%", "import java.util.Scanner;\npublic class Main{public static void main(String[]a){Scanner s=new Scanner(System.in);System.out.println(s.nextInt()+s.nextInt());}}", ["input-parse", "type-conversion"]),

    ("数组求和", "第一行输入 n，第二行输入 n 个整数，输出和。", [
        ("基本", "3\n1 2 3", "6", False, 1),
        ("空数组", "0\n", "0", True, 1),
    ], "正确性 100%", "import java.util.Scanner;\npublic class Main{public static void main(String[]a){Scanner s=new Scanner(System.in);int n=s.nextInt();int sum=0;for(int i=0;i<n;i++)sum+=s.nextInt();System.out.println(sum);}}", ["loop-boundary", "empty-input"]),

    ("数组最大值", "第一行 n，第二行 n 个整数，输出最大值。", [
        ("基本", "3\n1 5 3", "5", False, 1),
        ("负数", "3\n-1 -5 -3", "-1", True, 1),
    ], "正确性 100%", "import java.util.Scanner;\npublic class Main{public static void main(String[]a){Scanner s=new Scanner(System.in);int n=s.nextInt();int max=Integer.MIN_VALUE;for(int i=0;i<n;i++){int x=s.nextInt();if(x>max)max=x;}System.out.println(max);}}", ["array-traversal", "edge-case"]),

    ("判断奇偶", "输入一个整数，奇数输出 odd，偶数输出 even。", [
        ("偶数", "4", "even", False, 1),
        ("奇数", "7", "odd", False, 1),
    ], "正确性 100%", "import java.util.Scanner;\npublic class Main{public static void main(String[]a){Scanner s=new Scanner(System.in);int n=s.nextInt();System.out.println(n%2!=0?\"odd\":\"even\");}}", ["boolean-logic", "type-conversion"]),

    ("字符串反转", "输入一个字符串，输出反转。", [
        ("基本", "hello", "olleh", False, 1),
        ("空串", "", "", True, 1),
    ], "正确性 100%", "import java.util.Scanner;\npublic class Main{public static void main(String[]a){Scanner s=new Scanner(System.in);String str=s.nextLine();System.out.println(new StringBuilder(str).reverse().toString());}}", ["string-slice", "empty-input"]),

    ("成绩等级判定", "输入 0-100 分数，>=90 为 A，>=80 为 B，>=60 为 C，否则 D。", [
        ("A", "95", "A", False, 1),
        ("D", "45", "D", False, 1),
        ("边界90", "90", "A", True, 1),
    ], "正确性 100%", "import java.util.Scanner;\npublic class Main{public static void main(String[]a){Scanner s=new Scanner(System.in);int n=s.nextInt();if(n>=90)System.out.println(\"A\");else if(n>=80)System.out.println(\"B\");else if(n>=60)System.out.println(\"C\");else System.out.println(\"D\");}}", ["boolean-logic", "edge-case"]),

    ("冒泡排序", "第一行 n，第二行 n 个整数，输出升序排列，空格分隔。", [
        ("基本", "4\n3 1 4 2", "1 2 3 4", False, 1),
        ("逆序", "3\n3 2 1", "1 2 3", True, 1),
    ], "正确性 100%", "import java.util.Scanner;\npublic class Main{public static void main(String[]a){Scanner s=new Scanner(System.in);int n=s.nextInt();int[]arr=new int[n];for(int i=0;i<n;i++)arr[i]=s.nextInt();for(int i=0;i<n;i++)for(int j=0;j<n-i-1;j++)if(arr[j]>arr[j+1]){int t=arr[j];arr[j]=arr[j+1];arr[j+1]=t;}for(int i=0;i<n;i++)System.out.print(arr[i]+(i<n-1?\" \":\"\"));}}", ["nested-loop", "array-traversal"]),

    ("计算阶乘", "输入非负整数 n，输出 n!。", [
        ("基本", "5", "120", False, 1),
        ("零", "0", "1", False, 1),
    ], "正确性 100%", "import java.util.Scanner;\npublic class Main{public static void main(String[]a){Scanner s=new Scanner(System.in);int n=s.nextInt();long r=1;for(int i=2;i<=n;i++)r*=i;System.out.println(r);}}", ["recursion-exit", "edge-case"]),
]

C_COURSE = [
    ("两数之和", "输入两个空格分隔的整数，输出它们的和。", [
        ("基本", "5 3", "8", False, 1),
        ("负数", "-1 4", "3", True, 1),
    ], "正确性 100%", "#include <stdio.h>\nint main(){int a,b;scanf(\"%d %d\",&a,&b);printf(\"%d\\n\",a+b);return 0;}", ["input-parse", "type-conversion"]),

    ("数组求和", "第一行输入 n，第二行输入 n 个整数，输出和。", [
        ("基本", "3\n1 2 3", "6", False, 1),
        ("空数组", "0\n", "0", True, 1),
    ], "正确性 100%", "#include <stdio.h>\nint main(){int n,sum=0;scanf(\"%d\",&n);for(int i=0;i<n;i++){int x;scanf(\"%d\",&x);sum+=x;}printf(\"%d\\n\",sum);return 0;}", ["loop-boundary", "empty-input"]),

    ("数组最大值", "第一行 n，第二行 n 个整数，输出最大值。", [
        ("基本", "3\n1 5 3", "5", False, 1),
        ("负数", "3\n-1 -5 -3", "-1", True, 1),
    ], "正确性 100%", "#include <stdio.h>\nint main(){int n;scanf(\"%d\",&n);int max=-2147483648;for(int i=0;i<n;i++){int x;scanf(\"%d\",&x);if(x>max)max=x;}printf(\"%d\\n\",max);return 0;}", ["array-traversal", "edge-case"]),

    ("判断奇偶", "输入一个整数，奇数输出 odd，偶数输出 even。", [
        ("偶数", "4", "even", False, 1),
        ("奇数", "7", "odd", False, 1),
    ], "正确性 100%", "#include <stdio.h>\nint main(){int n;scanf(\"%d\",&n);printf(\"%s\\n\",n%2?\"odd\":\"even\");return 0;}", ["boolean-logic", "type-conversion"]),

    ("字符串反转", "输入一个字符串，输出反转。", [
        ("基本", "hello", "olleh", False, 1),
        ("单字符", "a", "a", True, 1),
    ], "正确性 100%", "#include <stdio.h>\n#include <string.h>\nint main(){char s[1000];scanf(\"%s\",s);int n=strlen(s);for(int i=n-1;i>=0;i--)putchar(s[i]);putchar('\\n');return 0;}", ["string-slice", "array-index"]),

    ("成绩等级判定", "输入 0-100 分数，>=90 为 A，>=80 为 B，>=60 为 C，否则 D。", [
        ("A", "95", "A", False, 1),
        ("D", "45", "D", False, 1),
        ("边界60", "60", "C", True, 1),
    ], "正确性 100%", "#include <stdio.h>\nint main(){int n;scanf(\"%d\",&n);if(n>=90)printf(\"A\\n\");else if(n>=80)printf(\"B\\n\");else if(n>=60)printf(\"C\\n\");else printf(\"D\\n\");return 0;}", ["boolean-logic", "edge-case"]),

    ("冒泡排序", "第一行 n，第二行 n 个整数，输出升序排列，空格分隔。", [
        ("基本", "4\n3 1 4 2", "1 2 3 4", False, 1),
        ("逆序", "3\n3 2 1", "1 2 3", True, 1),
    ], "正确性 100%", "#include <stdio.h>\nint main(){int n;scanf(\"%d\",&n);int a[100];for(int i=0;i<n;i++)scanf(\"%d\",&a[i]);for(int i=0;i<n;i++)for(int j=0;j<n-i-1;j++)if(a[j]>a[j+1]){int t=a[j];a[j]=a[j+1];a[j+1]=t;}for(int i=0;i<n;i++)printf(\"%d%c\",a[i],i<n-1?' ':'\\n');return 0;}", ["nested-loop", "array-traversal"]),

    ("计算阶乘", "输入非负整数 n，输出 n!。", [
        ("基本", "5", "120", False, 1),
        ("零", "0", "1", False, 1),
    ], "正确性 100%", "#include <stdio.h>\nint main(){int n;long long r=1;scanf(\"%d\",&n);for(int i=2;i<=n;i++)r*=i;printf(\"%lld\\n\",r);return 0;}", ["recursion-exit", "edge-case"]),
]

COURSES = [
    ("Python 从入门到精通", "PY-101", "python", PYTHON_COURSE),
    ("Java 从入门到精通", "JAVA-101", "java", JAVA_COURSE),
    ("C 语言从入门到精通", "C-101", "c", C_COURSE),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="清空预设课程后重建")
    args = parser.parse_args()

    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        # 找或创建教师
        teacher = db.query(User).filter(User.username == "teacher1").first()
        if not teacher:
            teacher = User(
                username="teacher1",
                password_hash=hash_password("123456"),
                role="teacher",
                display_name="教师张",
            )
            db.add(teacher)
            db.commit()
            db.refresh(teacher)

        # 获取知识点 code → id 映射
        kp_rows = db.query(KnowledgePoint).all()
        code_to_id = {k.code: k.id for k in kp_rows}
        if not code_to_id:
            print("错误：知识点表为空，请先运行 seed_demo.py 初始化知识点")
            return

        if args.reset:
            # 清空预设课程的作业 + Q矩阵
            for course in db.query(Course).filter(Course.code.in_(["PY-101", "JAVA-101", "C-101"])).all():
                db.query(Assignment).filter(Assignment.course_id == course.id).delete(synchronize_session=False)
                db.query(AssignmentKnowledgePoint).filter(
                    AssignmentKnowledgePoint.assignment_id.in_(
                        db.query(Assignment.id).filter(Assignment.course_id == course.id)
                    )
                ).delete(synchronize_session=False)
                db.query(Course).filter(Course.id == course.id).delete(synchronize_session=False)
            db.commit()
            print("已清空预设课程（--reset）")

        created_count = 0
        for course_name, course_code, course_lang, problems in COURSES:
            # 创建课程（幂等）
            course = db.query(Course).filter(Course.code == course_code).first()
            if not course:
                course = Course(teacher_id=teacher.id, name=course_name, code=course_code)
                db.add(course)
                db.commit()
                db.refresh(course)
                print(f"  课程: {course_name} ({course_code})")

            # 创建班级（幂等）
            klass = db.query(Class).filter(Class.course_id == course.id).first()
            if not klass:
                klass = Class(course_id=course.id, name=f"{course_code} 默认班")
                db.add(klass)
                db.commit()
                db.refresh(klass)

            for idx, (title, desc, cases, rubric, ref_code, kp_codes) in enumerate(problems):
                # 幂等：按标题查重
                existing = db.query(Assignment).filter(
                    Assignment.course_id == course.id,
                    Assignment.title == title,
                ).first()
                if existing:
                    continue

                a = Assignment(
                    teacher_id=teacher.id,
                    course_id=course.id,
                    title=title,
                    description=desc,
                    lang=course_lang,
                    scoring_rubric=rubric,
                    reference_code=ref_code,
                    status="published",
                    kind="formal",
                )
                a.test_cases = [
                    TestCase(
                        name=name,
                        input=inp,
                        expected_output=expected,
                        is_hidden=hidden,
                        weight=weight,
                        order=i,
                    )
                    for i, (name, inp, expected, hidden, weight) in enumerate(cases)
                ]
                db.add(a)
                db.commit()
                db.refresh(a)

                # 打 Q 矩阵标签
                for code in kp_codes:
                    kp_id = code_to_id.get(code)
                    if kp_id and not db.query(AssignmentKnowledgePoint).filter_by(
                        assignment_id=a.id, knowledge_point_id=kp_id
                    ).first():
                        db.add(AssignmentKnowledgePoint(
                            assignment_id=a.id,
                            knowledge_point_id=kp_id,
                            weight=1.0,
                        ))
                db.commit()
                created_count += 1
                print(f"    [{idx + 1}] {title} ({course_lang}, {len(cases)} 用例, 知识点: {', '.join(kp_codes)})")

        print(f"\n完成！共创建 {created_count} 道题目。")
        print("  登录 teacher1/123456 → 我的课程 可见三套课程")
        print("  学生选课后提交，诊断+掌握度+变式闭环自动运行")
    finally:
        db.close()


if __name__ == "__main__":
    main()
