import os
from typing import AsyncGenerator

import anthropic

from database import Database

async_client = anthropic.AsyncAnthropic()
MODEL = "claude-sonnet-4-6"

_SYSTEM_BASE = """당신은 시스템 문의 사항에 대한 해결 방법과 조치 가이드를 제공하는 전문 지원 챗봇입니다.

아래의 Q&A 데이터베이스를 기반으로 사용자의 질문에 정확하고 도움이 되는 답변을 제공하세요.

**답변 원칙:**
1. 참고 데이터를 기반으로 구체적이고 단계별 조치 방법을 안내하세요
2. 관련 Q&A가 있다면 해당 내용을 중심으로 답변하세요
3. 데이터에 없는 내용은 추측하지 말고 담당 부서에 문의하도록 안내하세요
4. 마크다운 형식으로 가독성 있게 작성하세요
5. 한국어로 답변하세요"""


def _build_context(results: list) -> str:
    if not results:
        return "※ 등록된 Q&A 데이터가 없습니다. 관리자 페이지에서 Q&A를 먼저 등록해주세요."
    parts = []
    for r in results:
        entry = f"**[{r['category']}]**\nQ: {r['question']}\nA: {r['answer']}"
        if r.get("keywords"):
            entry += f"\n키워드: {r['keywords']}"
        parts.append(entry)
    return "\n\n---\n\n".join(parts)


async def stream_answer(question: str, db: Database) -> AsyncGenerator[str, None]:
    results = await db.search_qa(question, limit=8)
    context = _build_context(results)
    system_text = f"{_SYSTEM_BASE}\n\n## 참고 Q&A 데이터베이스\n\n{context}"

    async with async_client.messages.stream(
        model=MODEL,
        max_tokens=2048,
        system=[
            {
                "type": "text",
                "text": system_text,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": question}],
    ) as stream:
        async for text in stream.text_stream:
            yield text
