from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Query, HTTPException
from starlette import status

import database as db

from models import FlashcardResponse, FlashcardCreate, FlashcardUpdate, MessageResponse, StatsResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('🚀 Запуск приложения ...')
    await db.init_db()
    print('✅ База данных готова')

    yield

    print('🛑 Приложение остановлено')

app = FastAPI(
    title='🇮🇴 Англйиские карточки',
    description="""
    ### API для изучения англйиских слов
    
    Это приложение позволяет:
    - создавать карточки
    - изучать карточки
    ...
    """,
    version='1.0.0',
    lifespan=lifespan,
)


@app.get(
    "/cards",
    response_model=list[FlashcardResponse],
    tags=["Карточки"],
    summary="Получить все карточки",
    description="Возвращает список всех карточек с возможностью фильтрации по части слова",
)

async def get_all_cards(
        english: Optional[str] = Query(
            default=None,
            description="Фильтр по части английского слова (не регистрозависимый)",
            examples=["hello"],
        ),
        russian: Optional[str] = Query(
            default=None,
            description="Фильтр по части русского слова (не регистрозависимый)",
            examples=["привет"],
        )):

        return await db.get_all_cards(english, russian)


@app.get(
    "/cards/random",
    response_model=FlashcardResponse,
    tags=["Тренировка"],
    summary="Случайная карточка",
    description="Возвращает случайную карточку для тренировки"
)

async def get_random_card():
    card = await db.get_random_card()

    if card is None:
        raise HTTPException(
            status_code=404,
            detail="Нет доступных карточек. Сначала добвьте карточку"
        )

    return card

@app.get(
    "/cards/{card_id}",
    response_model=FlashcardResponse,
    tags=["Карточки"],
    summary="Полуучить карточку по ID",
    description="Возвращает карточку по ID"
)

async def get_card_by_id(card_id: int):
    card = await db.get_card_by_id(card_id)

    if card is None:
        raise HTTPException(
            status_code=404,
            detail=f"Карточка с ID {card_id} не найдена"
        )
    return card


@app.get(
    '/cards/category/{category}',
    response_model=list[FlashcardResponse],
    tags=["Карточки"],
    summary="Карточки по категориям",
    description="Возвращает все карточки указанной категории"
)

async def get_all_cards_by_category(category: str):
    cards = await db.get_card_by_category(category)

    if not cards:
        raise HTTPException(
            status_code=404,
            detail=f"Карточки с категорией {category} не найдены"
        )

    return cards


@app.post(
    '/cards',
    response_model=FlashcardResponse,
    status_code=201,
    tags=["Карточки"],
    summary="Добавить карточку",
    description="Создает новую карточку со словом и переводом"
)

async def create_card(card_data: FlashcardCreate):
    return await db.create_card(
        english=card_data.english,
        russian=card_data.russian,
        category=card_data.category
    )


@app.put(
    '/cards/{card_id}',
    response_model=FlashcardResponse,
    tags=["Карточки"],
    summary="Обновить карточку",
    description="Обновить карточку"
)

async def update_card(card_id: int, card_data: FlashcardUpdate):
    existing = await db.get_card_by_id(card_id)
    if existing is None:
        raise HTTPException(
            status_code=404,
            detail=f"Карточка с ID {card_id} не найдена"
        )

    updated = await db.update_card(
        card_id=card_id,
        english=card_data.english,
        russian=card_data.russian,
        category=card_data.category
    )

    return updated


@app.delete(
    '/cards/{card_id}',
    response_model=MessageResponse,
    tags=["Карточки"],
    summary="Удалить карточку",
    description="Удалить существующую карточку"
)
async def delete_card(card_id: int):
    deleted = await db.delete_card(card_id)

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail=f'Карточка с ID {card_id} не найдена'
        )

    return {"message": f"Карточка с {deleted['english']} успешно удалена"}


@app.get(
    "/stats",
    response_model=StatsResponse,
    tags=["Статистика"],
    summary="Статистика карточек",
    description="Возвращает общую статистику по карточкам"
)
async def get_stats():
    return await db.get_stats()


if __name__ == '__main__':
    import uvicorn

    print("🚀 Запуск сервера...")
    print('Документация: http://localhost:8000/docs')
    print('ReDoc: http://localhost:8000/redoc')

    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000
    )