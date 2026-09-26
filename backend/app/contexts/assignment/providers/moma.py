from __future__ import annotations

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.contexts.ai.providers.moma import llm
from app.contexts.assignment.exceptions import GenerationError
from app.contexts.assignment.schemas import AssignmentResult, TestCaseResult
from app.core.config import settings

_SYSTEM = (
    "你是编程命题专家。根据教师一句话生成一道编程题，"
    "含题面、若干测试用例（含隐藏用例与权重）、评分细则、参考实现。只输出 JSON。"
)

_parser = PydanticOutputParser(pydantic_object=AssignmentResult)
_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _SYSTEM + "\n\n{format_instructions}"),
        ("user", "{input}"),
    ]
)


class AssignmentGenerator:
    async def generate(self, prompt: str) -> AssignmentResult:
        if settings.MOCK:
            return self._mock()
        try:
            chain = _PROMPT | llm() | _parser
            return await chain.ainvoke(
                {"input": prompt, "format_instructions": _parser.get_format_instructions()}
            )
        except Exception as e:
            raise GenerationError(f"命题失败: {e}")

    @staticmethod
    def _mock() -> AssignmentResult:
        return AssignmentResult(
            title="两数之和",
            description="给定两个整数 a 和 b，输出它们的和。",
            lang="python",
            test_cases=[
                TestCaseResult(input="1 2", expected_output="3"),
                TestCaseResult(input="-1 5", expected_output="4", is_hidden=True),
            ],
            scoring_rubric="正确性 80% + 边界 20%",
            reference_code="print(sum(map(int, input().split())))",
        )
