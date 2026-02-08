import aiosqlite
from datetime import datetime
from typing import Optional
from contextlib import contextmanager, asynccontextmanager

DATABASE_PATH = "flashcards.db"


@asynccontextmanager
async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row

    try:
        yield db
    finally:
        await db.close()


async def init_db():
    async with get_db() as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS `flashcards` (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        english TEXT NOT NULL,
        russian TEXT NOT NULL,
        category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        await db.commit()

        cursor = await db.execute("SELECT COUNT() FROM flashcards")
        count = (await cursor.fetchone())[0]

        if count == 0:
            await seed_data(db)


async def seed_data(db: aiosqlite.Connection) -> None:
    sample_cards = [
        ("Hello", "Привет", "greetings"),
        ("Goodbye", "Пока", "greetings"),
        ("Thank you", "Спасибо", "greetings"),
    ]

    await db.executemany("INSERT INTO flashcards (english, russian, category) VALUES (?, ?, ?)",
                         sample_cards
                         )
    await db.commit()
    print(f"✅ База данных инициализирована {len(sample_cards)} карточками")


# 1=1 возвращает True, если его не передать, то не будет падать
async def get_all_cards(
        english_filter: Optional[str] = None,
        russian_filter: Optional[str] = None,
) -> list[dict]:
    async with get_db() as db:
        query = "SELECT * FROM flashcards WHERE 1=1"
        params = []

        if english_filter:
            query += f" AND LOWER(english) LIKE ?"
            params.append(f'%{english_filter.lower()}%')

        if russian_filter:
            query += f" AND LOWER(russian) LIKE ?"
            params.append(f'%{russian_filter.lower()}%')

        query += f" ORDER BY created_at DESC"

        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()

        return [dict(row) for row in rows]

async def get_card_by_id(card_id: int) -> Optional[dict]:
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT * FROM flashcards WHERE id=?", (card_id,))
        row = await cursor.fetchone()

        return dict(row) if row else None


async def get_random_card() -> Optional[dict]:
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT * FROM flashcards ORDER BY RANDOM() LIMIT 1"
        )
        row = await cursor.fetchone()

        return dict(row) if row else None


async def get_card_by_category(category: str) -> list[dict]:
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT * FROM flashcards WHERE LOWER(category) = ? ORDER BY created_at DESC",
            (category.lower(),)
        )

        rows = await cursor.fetchall()

        return [dict(row) for row in rows]


async def create_card(english: str, russian: str, category: Optional[str]) -> dict:
    async with get_db() as db:
        cursor = await db.execute(
            "INSERT into flashcards (english, russian, category) VALUES (?, ?, ?)",
            (english.strip(), russian.strip(), category.strip() if category else None)
        )

        await db.commit()

        new_cursor = await db.execute(
            "SELECT * FROM flashcards WHERE id=?",
            (cursor.lastrowid,)
        )

        row = await new_cursor.fetchone()

        return dict(row)


async def update_card(card_id: int, english: Optional[str], russian: Optional[str], category: Optional[str]) -> Optional[dict]:
    async with get_db() as db:
        updates = []
        params = []

        if english is not None:
            updates.append("english= ?")
            params.append(english.strip())

        if russian is not None:
            updates.append("russian= ?")
            params.append(russian.strip())

        if category is not None:
            updates.append("category= ?")
            params.append(category.strip())

        if not updates:
            return await get_card_by_id(card_id)

        params.append(card_id)
        query = f"UPDATE flashcards SET {','.join(updates)} WHERE id=?"

        await db.execute(query, params)
        await db.commit()

        return await get_card_by_id(card_id)


async def delete_card(card_id: int) -> Optional[dict]:
    async with get_db() as db:
        card  = await get_card_by_id(card_id)

        if card:
            await db.execute("DELETE FROM flashcards WHERE id=?", (card_id,))
            await db.commit()

        return card



# ----------------------СТАТИСТИКА----------------------

async  def get_stats() -> dict:
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM flashcards"
        )
        total = (await cursor.fetchone())[0]

        cursor = await db.execute(
            """
            SELECT COALESCE(category, 'без категории') as cat, COUNT(*) as cnt
             FROM flashcards
            """)

        categories = {row[0]: row[1] for row in await cursor.fetchall()}

        cursor = await db.execute(
            "SELECT MAX(created_at) FROM flashcards"
        )

        last_added = (await cursor.fetchone())[0]

        return dict(total_cards=total, categories=categories, last_added=last_added)