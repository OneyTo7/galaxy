# -*- coding: utf-8 -*-
"""从 JSON 文件批量导入课程章节讲义。

章节内容存放在 scripts/lessons_data/<course_code>.json，
每个 JSON 是一个数组，元素格式：
  {"title": "第 X 章：标题", "content": "Markdown 正文", "assignment_title": "关联作业标题或null"}

用法：
    cd backend && source .venv/bin/activate
    MOCK=1 python scripts/seed_lessons_v2.py            # 幂等
    MOCK=1 python scripts/seed_lessons_v2.py --reset     # 清空后重建
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.contexts.assignment.models import Assignment
from app.contexts.lesson.models import Lesson
from app.contexts.organization.models import Course
from app.core.database import SessionLocal

DATA_DIR = Path(__file__).resolve().parent / "lessons_data"
COURSE_CODES = ["PY-101", "JAVA-101", "C-101", "ALGO-101"]


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
        for code in COURSE_CODES:
            json_path = DATA_DIR / f"{code}.json"
            if not json_path.exists():
                print(f"  跳过：{json_path} 不存在")
                continue

            course = db.query(Course).filter(Course.code == code).first()
            if not course:
                # 自动创建课程（如 ALGO-101 算法增强）
                from app.contexts.user.models import User
                from app.core.security import hash_password
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
                course_names = {
                    "PY-101": "Python 从入门到精通",
                    "JAVA-101": "Java 从入门到精通",
                    "C-101": "C 语言从入门到精通",
                    "ALGO-101": "算法增强（力扣热题 100）",
                }
                course = Course(
                    teacher_id=teacher.id,
                    name=course_names.get(code, code),
                    code=code,
                )
                db.add(course)
                db.commit()
                db.refresh(course)
                print(f"  创建课程: {course.name} ({code})")

            lessons = json.loads(json_path.read_text(encoding="utf-8"))
            for idx, item in enumerate(lessons):
                title = item["title"]
                content = item["content"]
                assignment_title = item.get("assignment_title")

                existing = db.query(Lesson).filter(
                    Lesson.course_id == course.id,
                    Lesson.title == title,
                ).first()
                if existing:
                    # 更新内容（--reset 时不会走到这里因为已清空）
                    existing.content = content
                    if assignment_title:
                        a = db.query(Assignment).filter(
                            Assignment.course_id == course.id,
                            Assignment.title == assignment_title,
                        ).first()
                        if a:
                            existing.assignment_id = a.id
                    db.commit()
                    continue

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

            print(f"  {code} ({course.name}): {len(lessons)} 章")
        print(f"\n完成！共创建/更新 {created} 个章节。")
    finally:
        db.close()


if __name__ == "__main__":
    main()
