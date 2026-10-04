"""种子脚本：受控知识点体系 + 演示数据（MOCK=1 下可完整演示闭环）。

用法：
    cd backend && source .venv/bin/activate
    python scripts/seed_demo.py            # 幂等：已有则跳过
    python scripts/seed_demo.py --reset     # 清空后重建（演示用）
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.contexts.assignment.models import Assignment, TestCase
from app.contexts.assignment.repository import SQLAlchemyAssignmentRepo
from app.contexts.assignment.service import AssignmentService
from app.contexts.diagnose.models import Misconception
from app.contexts.diagnose.repository import SQLAlchemyMisconceptionRepo
from app.contexts.evaluation.models import Evaluation
from app.contexts.evaluation.repository import SQLEvaluationRepo
from app.contexts.evaluation.schemas import CaseResult
from app.contexts.evaluation.service import EvaluationService
from app.contexts.mastery.models import (
    AssignmentKnowledgePoint,
    KnowledgePoint,
    MasteryEvent,
    StudentMastery,
)
from app.contexts.mastery.repository import SQLAlchemyMasteryRepo
from app.contexts.mastery.service import MasteryService, OvercomeMarkerProtocol
from app.contexts.organization.models import Class, Course, Enrollment
from app.contexts.organization.repository import SQLOrganizationRepo
from app.contexts.organization.service import OrganizationService
from app.contexts.submission.models import Submission
from app.contexts.submission.repository import SQLAlchemySubmissionRepo
from app.contexts.submission.service import SubmissionService
from app.contexts.user.models import User
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password

# ── 受控知识点体系（入门编程，语言无关）──────────────────────────────
KNOWLEDGE_POINTS = [
    ("loop-boundary", "循环边界条件", "循环", 1),
    ("loop-termination", "循环终止条件", "循环", 2),
    ("nested-loop", "多重循环控制", "循环", 3),
    ("array-index", "数组索引", "数组", 10),
    ("array-boundary", "数组越界", "数组", 11),
    ("off-by-one", "差一错误", "数组", 12),
    ("array-traversal", "数组遍历", "数组", 13),
    ("function-return", "函数返回值", "函数", 20),
    ("function-param", "函数参数传递", "函数", 21),
    ("recursion-exit", "递归出口", "递归", 30),
    ("recursion-state", "递归状态传递", "递归", 31),
    ("input-parse", "输入解析", "IO", 40),
    ("output-format", "输出格式", "IO", 41),
    ("type-conversion", "类型转换", "逻辑", 50),
    ("boolean-logic", "布尔逻辑", "逻辑", 51),
    ("edge-case", "边界输入", "边界", 60),
    ("empty-input", "空输入处理", "边界", 61),
    ("string-slice", "字符串切片", "字符串", 70),
    ("string-concat", "字符串拼接", "字符串", 71),
    ("variable-scope", "变量作用域", "逻辑", 80),
]


def seed_knowledge_points(db) -> dict[str, int]:
    code_to_id: dict[str, int] = {}
    for code, name, category, order in KNOWLEDGE_POINTS:
        existing = db.query(KnowledgePoint).filter(KnowledgePoint.code == code).first()
        if existing:
            code_to_id[code] = existing.id
            continue
        kp = KnowledgePoint(code=code, name=name, category=category, sort_order=order)
        db.add(kp)
        db.flush()
        code_to_id[code] = kp.id
    db.commit()
    print(f"  knowledge_points: {len(code_to_id)} 个")
    return code_to_id


def _seed_users(db) -> dict[str, User]:
    """教师 1 + 学生 2（A/B 同分不同诊断）。"""
    users: dict[str, User] = {}
    specs = [
        ("teacher1", "teacher", "教师张"),
        ("studentA", "student", "学生A"),
        ("studentB", "student", "学生B"),
    ]
    for username, role, display in specs:
        u = db.query(User).filter(User.username == username).first()
        if not u:
            u = User(
                username=username,
                password_hash=hash_password("123456"),
                role=role,
                display_name=display,
            )
            db.add(u)
            db.flush()
        users[username] = u
    db.commit()
    print(f"  users: {len(users)} 个（teacher1/123456, studentA/123456, studentB/123456）")
    return users


def _seed_course(db, teacher: User) -> tuple[Course, Class]:
    course = db.query(Course).filter(Course.code == "CS101").first()
    if not course:
        course = Course(teacher_id=teacher.id, name="入门编程", code="CS101")
        db.add(course)
        db.flush()
    klass = db.query(Class).filter(Class.course_id == course.id).first()
    if not klass:
        klass = Class(course_id=course.id, name="2026秋季班")
        db.add(klass)
        db.flush()
    db.commit()
    return course, klass


def _seed_assignment(
    db, teacher: User, course: Course, kp_codes: dict[str, int]
) -> tuple[Assignment, Assignment]:
    """两个作业：A 考循环边界，B 考输入解析。"""
    a1 = db.query(Assignment).filter(Assignment.title == "数组求和（练循环边界）").first()
    if not a1:
        a1 = Assignment(
            teacher_id=teacher.id,
            course_id=course.id,
            title="数组求和（练循环边界）",
            description="给定 n 个整数，输出它们的和。",
            lang="python",
            scoring_rubric="正确性 80% + 边界 20%",
            reference_code="print(sum(map(int, input().split())))",
            status="published",
            kind="formal",
        )
        a1.test_cases = [
            TestCase(name="基本", input="3\n1 2 3", expected_output="6", order=0),
            TestCase(name="单元素", input="1\n5", expected_output="5", order=1),
            TestCase(name="空数组", input="0", expected_output="0", is_hidden=True, order=2),
            TestCase(name="负数", input="3\n-1 -2 -3", expected_output="-6", is_hidden=True, weight=2, order=3),
        ]
        db.add(a1)
        db.flush()
    # Q 矩阵：循环边界 + 边界输入
    for code in ("loop-boundary", "edge-case"):
        kpid = kp_codes[code]
        if not db.query(AssignmentKnowledgePoint).filter_by(assignment_id=a1.id, knowledge_point_id=kpid).first():
            db.add(AssignmentKnowledgePoint(assignment_id=a1.id, knowledge_point_id=kpid, weight=1.0))

    a2 = db.query(Assignment).filter(Assignment.title == "读取两个数（练输入解析）").first()
    if not a2:
        a2 = Assignment(
            teacher_id=teacher.id,
            course_id=course.id,
            title="读取两个数（练输入解析）",
            description="输入两个空格分隔的整数，输出它们的差（第一个减第二个）。",
            lang="python",
            scoring_rubric="正确性 100%",
            reference_code="a, b = map(int, input().split()); print(a - b)",
            status="published",
            kind="formal",
        )
        a2.test_cases = [
            TestCase(name="基本", input="5 3", expected_output="2", order=0),
            TestCase(name="减为负", input="3 5", expected_output="-2", order=1),
            TestCase(name="零", input="0 0", expected_output="0", is_hidden=True, order=2),
            TestCase(name="大数", input="100 1", expected_output="99", is_hidden=True, order=3),
            TestCase(name="同数", input="7 7", expected_output="0", is_hidden=True, order=4),
        ]
        db.add(a2)
        db.flush()
    for code in ("input-parse", "type-conversion"):
        kpid = kp_codes[code]
        if not db.query(AssignmentKnowledgePoint).filter_by(assignment_id=a2.id, knowledge_point_id=kpid).first():
            db.add(AssignmentKnowledgePoint(assignment_id=a2.id, knowledge_point_id=kpid, weight=1.0))

    db.commit()
    return a1, a2


def _seed_submissions_and_mastery(
    db, course: Course, klass: Class, a1: Assignment, a2: Assignment,
    studentA: User, studentB: User,
) -> None:
    """学生 A：循环边界误区（差一错误）；学生 B：输入解析误区。
    两人都 60 分但误区不同，体现"同分不同诊断"。"""
    enrollments = [
        (klass.id, studentA.id),
        (klass.id, studentB.id),
    ]
    for class_id, sid in enrollments:
        if not db.query(Enrollment).filter_by(class_id=class_id, student_id=sid).first():
            db.add(Enrollment(class_id=class_id, student_id=sid))
    db.commit()

    # 学生 A：边界处理不当（空数组时 arr[i-1] 越界），通过 3/5 权重 = 60分
    code_a = "n = int(input()); arr = list(map(int, input().split())); s = 0\nfor i in range(n): s += arr[i-1]\nprint(s)"
    # 学生 B：输入解析错误（arr 未读第二行），边界用例恰好通过，3/5 权重 = 60分
    code_b = "n = int(input()); s = 0\nprint(s)"

    for student, assignment, code, failed_case_idx in [
        (studentA, a1, code_a, 2),  # 空数组 IndexError
        (studentB, a2, code_b, 0),  # 输入解析错
    ]:
        sub = db.query(Submission).filter_by(user_id=student.id, assignment_id=assignment.id).first()
        if not sub:
            sub = Submission(
                user_id=student.id,
                assignment_id=assignment.id,
                code=code,
                lang="python",
                status="pending",
                score=0,
            )
            db.add(sub)
            db.commit()
        # 跑评测
        from app.contexts.evaluation import runner
        results = runner.run(code, "python", assignment.test_cases)
        # 入库评测结果
        db.query(Evaluation).filter_by(submission_id=sub.id).delete()
        for r in results:
            db.add(Evaluation(
                submission_id=sub.id,
                case_id=r.case_id,
                passed=r.passed,
                stdout=r.stdout,
                stderr=r.stderr,
                timed_out=r.timed_out,
                elapsed_ms=r.elapsed_ms,
            ))
        total_w = sum(tc.weight for tc in assignment.test_cases) or 1
        passed_w = sum(tc.weight for tc, r in zip(assignment.test_cases, results) if r.passed)
        score = round(passed_w / total_w * 100)
        sub.score = score
        sub.status = "done"
        db.commit()
        print(f"  {student.username} → {assignment.title}: score={score}")

        # 记录掌握度
        org_svc = OrganizationService(SQLOrganizationRepo(db))
        assign_svc = AssignmentService(SQLAlchemyAssignmentRepo(db), None, org_svc)  # type: ignore
        eval_svc = EvaluationService(SQLEvaluationRepo(db))
        sub_svc = SubmissionService(SQLAlchemySubmissionRepo(db), assign_svc, eval_svc, org_svc)

        class _M(OvercomeMarkerProtocol):
            def __init__(self, d): self._r = SQLAlchemyMisconceptionRepo(d)
            def mark_overcome(self, u, k): return self._r.mark_open_overcome(u, k)

        mastery_svc = MasteryService(
            repo=SQLAlchemyMasteryRepo(db),
            evaluation_svc=eval_svc,
            submission_svc=sub_svc,
            assignment_svc=assign_svc,
            org_svc=org_svc,
            overcome_marker=_M(db),
        )
        mastery_svc.record_submission(sub.id)
        print(f"    mastery recorded for {student.username}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="清空 mastery/cheating/variant 等后重建")
    args = parser.parse_args()

    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        if args.reset:
            for model in [MasteryEvent, StudentMastery, AssignmentKnowledgePoint, KnowledgePoint]:
                db.query(model).delete()
            db.commit()
            print("已清空 mastery + 知识点表（--reset）")

        print("开始种子...")
        kps = seed_knowledge_points(db)
        users = _seed_users(db)
        course, klass = _seed_course(db, users["teacher1"])
        a1, a2 = _seed_assignment(db, users["teacher1"], course, kps)
        _seed_submissions_and_mastery(db, course, klass, a1, a2, users["studentA"], users["studentB"])
        print("种子完成。")
        print("  登录：teacher1/123456（教师）、studentA/123456、studentB/123456")
        print(f"  课程 CS101 / 班级 2026秋季班")
        print(f"  作业1: {a1.title}（学生A 60分，循环边界误区）")
        print(f"  作业2: {a2.title}（学生B 60分，输入解析误区）")
    finally:
        db.close()


if __name__ == "__main__":
    main()
