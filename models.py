from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FlashcardCreate(BaseModel):
    english: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description='Слово или фраза на английском',
        examples=['Hello']
    )

    russian: str = Field(
        ...,
        min_length = 1,
        max_length = 200,
        description = 'Перевод на русский',
        examples = ['Привет']
    )

    category: Optional[str] = Field(
        default = None,
        max_length=50,
        description='Категория карточки (опционально)',
        examples=['Приветствие']
    )

    class Config:
        json_schema_extra = {
            "example": {
                'english': 'Hello',
                'russian': 'Привет',
                'category': 'greetings',
            }
        }


class FlashcardUpdate(BaseModel):
    english: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description='Слово или фраза на английском',
        examples=['Hello']
    )

    russian: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description='Перевод на русский',
        examples=['Привет']
    )

    category: Optional[str] = Field(
        default=None,
        max_length=50,
        description='Категория карточки (опционально)',
        examples=['Приветствие']
    )

class FlashcardResponse(BaseModel):
    id: int = Field(..., description='Уникальный идентификатор карточки')
    english: str = Field(..., description='Слово или фраза на английском')
    russian: str = Field(..., description='Перевод на русский')
    category: Optional[str] = Field(None, description='Категория карточки')
    created_at: datetime = Field(..., description='Дата и время создания')

    class Config:
        json_schema_extra = {
            "example": {
                'id': 1,
                'english': 'Hello',
                'russian': 'Привет',
                'category': 'greetings',
                'created_at': '2026-01-28T21:37:00'
            }
        }


class StatusResponse(BaseModel):
    total_cards: int = Field(..., description='Общее количество карточек')
    categories: dict[str, int] = Field(..., description='Количество карточек по категориям')
    last_added: Optional[datetime] = Field(None, description='Дата последнего добавления карточки')

    class Config:
        json_schema_extra = {
            "example": {
                'total_cards': 32,
                'categories': {
                    'greetings': 10,
                    'food': 20,
                    'restaurants': 30
                }
            }
        }


class MessageResponse(BaseModel):
    message: str = Field(..., description='Текст сообщения')

    class Config:
        json_schema_extra = {
            "example": {
                'message': 'Карточка успешна удалена'
            }
        }


class StatsResponse(BaseModel):
    total_cards: int = Field(..., description='Общее количество карточек')
    categories: dict[str, int] = Field(..., description="Количество карточек по категориям")
    last_added: datetime = Field(None, description="дата последнего добавления карточки")

    class Config:
        json_schema_extra = {
            "example": {
                'total_cards': 32,
                'categories': {
                    'greetings': 10,
                    'food': 20,
                },
                'last_added': '2026-01-28T21:37:00'

            }
        }