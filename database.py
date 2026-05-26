import aiosqlite
from typing import Optional, List, Dict


class Database:
    def __init__(self, path: str = "chatbot.db"):
        self.path = path

    async def init(self):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS qa_pairs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL DEFAULT '일반',
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    keywords TEXT NOT NULL DEFAULT '',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    async def create_qa(self, category: str, question: str, answer: str, keywords: str) -> int:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                "INSERT INTO qa_pairs (category, question, answer, keywords) VALUES (?, ?, ?, ?)",
                (category, question, answer, keywords),
            )
            await db.commit()
            return cursor.lastrowid

    async def update_qa(self, id: int, category: str, question: str, answer: str, keywords: str):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """UPDATE qa_pairs
                   SET category=?, question=?, answer=?, keywords=?, updated_at=CURRENT_TIMESTAMP
                   WHERE id=?""",
                (category, question, answer, keywords, id),
            )
            await db.commit()

    async def delete_qa(self, id: int):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("DELETE FROM qa_pairs WHERE id=?", (id,))
            await db.commit()

    async def get_qa(self, id: int) -> Optional[Dict]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM qa_pairs WHERE id=?", (id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def list_qa(self, category: Optional[str] = None, search: Optional[str] = None) -> List[Dict]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            if search:
                return await self._search(db, search)
            if category:
                cursor = await db.execute(
                    "SELECT * FROM qa_pairs WHERE category=? ORDER BY created_at DESC",
                    (category,),
                )
            else:
                cursor = await db.execute("SELECT * FROM qa_pairs ORDER BY created_at DESC")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def search_qa(self, query: str, limit: int = 8) -> List[Dict]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            return await self._search(db, query, limit)

    async def _search(self, db: aiosqlite.Connection, query: str, limit: int = 50) -> List[Dict]:
        terms = [t.strip() for t in query.split() if t.strip()]
        if not terms:
            cursor = await db.execute(
                "SELECT * FROM qa_pairs ORDER BY created_at DESC LIMIT ?", (limit,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

        seen_ids: set = set()
        all_rows: List[Dict] = []

        for term in terms:
            pattern = f"%{term}%"
            cursor = await db.execute(
                "SELECT * FROM qa_pairs WHERE question LIKE ? OR answer LIKE ? OR keywords LIKE ?",
                (pattern, pattern, pattern),
            )
            rows = await cursor.fetchall()
            for row in rows:
                d = dict(row)
                if d["id"] not in seen_ids:
                    all_rows.append(d)
                    seen_ids.add(d["id"])

        def score(qa: Dict) -> int:
            s = 0
            for term in terms:
                tl = term.lower()
                if tl in qa["question"].lower():
                    s += 3
                if tl in qa["answer"].lower():
                    s += 1
                if tl in qa["keywords"].lower():
                    s += 2
            if query.lower() in qa["question"].lower():
                s += 5
            return s

        all_rows.sort(key=score, reverse=True)
        return all_rows[:limit]

    async def list_categories(self) -> List[str]:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                "SELECT DISTINCT category FROM qa_pairs ORDER BY category"
            )
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def count(self) -> int:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM qa_pairs")
            row = await cursor.fetchone()
            return row[0] if row else 0
