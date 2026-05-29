import json
import os
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from database import Database
from rag import stream_answer

app = FastAPI(title="시스템 지원 챗봇")
templates = Jinja2Templates(directory="templates")
db = Database("chatbot.db")


@app.on_event("startup")
async def startup():
    await db.init()


class QAPair(BaseModel):
    category: str = "일반"
    question: str
    answer: str
    keywords: str = ""


class ChatMessage(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse(request, "chat.html")


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse(request, "admin.html")


@app.post("/api/chat/stream")
async def chat_stream(msg: ChatMessage):
    if not msg.message.strip():
        raise HTTPException(status_code=400, detail="메시지를 입력해주세요")

    if not os.environ.get("ANTHROPIC_API_KEY"):
        async def _key_error():
            yield f"data: {json.dumps({'text': '⚠️ ANTHROPIC_API_KEY 환경 변수가 설정되지 않았습니다.'})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(_key_error(), media_type="text/event-stream")

    async def generate():
        try:
            async for text in stream_answer(msg.message, db):
                yield f"data: {json.dumps({'text': text})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'text': f'오류가 발생했습니다: {str(e)}'})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/qa")
async def list_qa(category: Optional[str] = None, search: Optional[str] = None):
    return await db.list_qa(category=category, search=search)


@app.post("/api/qa", status_code=201)
async def create_qa(qa: QAPair):
    if not qa.question.strip() or not qa.answer.strip():
        raise HTTPException(status_code=400, detail="질문과 답변을 입력해주세요")
    new_id = await db.create_qa(qa.category, qa.question, qa.answer, qa.keywords)
    return {"id": new_id, "message": "Q&A가 등록되었습니다"}


@app.put("/api/qa/{qa_id}")
async def update_qa(qa_id: int, qa: QAPair):
    if not qa.question.strip() or not qa.answer.strip():
        raise HTTPException(status_code=400, detail="질문과 답변을 입력해주세요")
    if not await db.get_qa(qa_id):
        raise HTTPException(status_code=404, detail="Q&A를 찾을 수 없습니다")
    await db.update_qa(qa_id, qa.category, qa.question, qa.answer, qa.keywords)
    return {"message": "Q&A가 수정되었습니다"}


@app.delete("/api/qa/{qa_id}")
async def delete_qa(qa_id: int):
    if not await db.get_qa(qa_id):
        raise HTTPException(status_code=404, detail="Q&A를 찾을 수 없습니다")
    await db.delete_qa(qa_id)
    return {"message": "Q&A가 삭제되었습니다"}


@app.get("/api/categories")
async def list_categories():
    return await db.list_categories()


@app.get("/api/stats")
async def get_stats():
    total = await db.count()
    categories = await db.list_categories()
    return {"total": total, "category_count": len(categories)}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
