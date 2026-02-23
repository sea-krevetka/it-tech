from fastapi import FastAPI, HTTPException, Query, Path, status
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid

# Метаданные для тегов
tags_metadata = [
    {
        "name": "Books",
        "description": "Операции с книгами в библиотеке. ВА-ХА! Управляйте книжными сокровищами!"
    },
    {
        "name": "Health",
        "description": "Проверка работоспособности сервера"
    }
]

app = FastAPI(
    title="API Грибной Библиотеки (Other Service)",
    description="""
    Добро пожаловать в Грибную Библиотеку! 🍄
    
    Это **дополнительный сервис** для демонстрации работы API Gateway.
    
    Возможности:
    - 📚 Просмотр всех книжных сокровищ
    - ➕ Добавление новой книжной добычи  
    - 🔍 Поиск конкретных книг (если сможешь!)
    - ✏️ Обновление книжной мудрости
    - 🗑️ Удаление книг (осторожно!)
    
    Эндпоинты:
    - `GET /other/books` - Посмотреть все книги
    - `POST /other/books` - Добавить новую книгу
    - `GET /other/books/{id}` - Найти книгу по ID
    - `PUT /other/books/{id}` - Обновить книгу
    - `DELETE /other/books/{id}` - Удалить книгу
    - `GET /other/health` - Проверить статус сервера
    
    Все эндпоинты доступны через API Gateway по пути `/api/other/...`
    """,
    version="1.0.0",
    openapi_tags=tags_metadata,
    root_path="/api"  # Корневой путь для gateway
)


class BookCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Название книжного свитка",
        example="Преступление и наказание"
    )
    author: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Кто этот умный тип?",
        example="Фёдор Достоевский"
    )
    publication_year: int = Field(
        ...,
        ge=1000,
        le=2100,
        description="Когда эта штука появилась? ВА-ХА!",
        example=1866
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Новая книга про трубопроводы",
                "author": "Валуиджи",
                "publication_year": 2024
            }
        }


class BookUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Новое название книжного свитка",
        example="Обновленное название"
    )
    author: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Новый автор книги",
        example="Обновленный автор"
    )
    publication_year: Optional[int] = Field(
        None,
        ge=1000,
        le=2100,
        description="Новый год публикации",
        example=2024
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Обновленное название книги",
                "author": "Новый автор",
                "publication_year": 2024
            }
        }


class BookResponse(BookCreate):
    id: str = Field(
        ...,
        description="Уникальный идентификатор книги",
        example="550e8400-e29b-41d4-a716-446655440000"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "1",
                "title": "Преступление и наказание",
                "author": "Фёдор Достоевский",
                "publication_year": 1866
            }
        }


# База данных в памяти
books_db = []

# Начальные данные
sample_books = [
    {
        "id": "1",
        "title": "Преступление и наказание",
        "author": "Фёдор Достоевский",
        "publication_year": 1866
    },
    {
        "id": "2",
        "title": "Мастер и Маргарита",
        "author": "Михаил Булгаков",
        "publication_year": 1967
    },
    {
        "id": "3",
        "title": "1984",
        "author": "Джордж Оруэлл",
        "publication_year": 1949
    },
    {
        "id": "4",
        "title": "Война и мир",
        "author": "Лев Толстой",
        "publication_year": 1869
    },
    {
        "id": "5",
        "title": "Идиот",
        "author": "Фёдор Достоевский",
        "publication_year": 1869
    }
]

books_db.extend(sample_books)


@app.get(
    "/other/",
    summary="Корневой эндпоинт",
    description="""
    Добро пожаловать в Грибную Библиотеку! 🍄
    
    Это дополнительный сервис (other-service). 
    Все запросы проходят через API Gateway.
    
    Доступные эндпоинты:
    - `GET /other/books` - список всех книг
    - `POST /other/books` - добавить книгу
    - `GET /other/books/{id}` - книга по ID
    - `PUT /other/books/{id}` - обновить книгу
    - `DELETE /other/books/{id}` - удалить книгу
    - `GET /other/health` - проверка здоровья
    """,
    response_description="Приветственное сообщение и информация об API",
    tags=["Books"]
)
async def root():
    """
    Корневой эндпоинт API Грибной Библиотеки (other-service).
    """
    return {
        "message": "ВА-ХА! Добро пожаловать в Грибную Библиотеку! (Other Service)",
        "service": "other-service",
        "docs": "/docs",
        "redoc": "/redoc",
        "note": "Доступ через API Gateway: http://localhost/api/other/",
        "endpoints": {
            "GET /other/books": "Посмотреть все мои книжные сокровища",
            "POST /other/books": "Добавить новую книжную добычу",
            "GET /other/books/{id}": "Найти конкретную книгу (если сможешь!)",
            "PUT /other/books/{id}": "Обновить книжную мудрость",
            "DELETE /other/books/{id}": "Удалить книгу (осторожно!)",
            "GET /other/health": "Проверить здоровье сервера"
        }
    }


@app.get(
    "/other/books",
    response_model=List[BookResponse],
    tags=["Books"],
    summary="Получить список всех книг",
    description="""
    ## Получение списка всех книг 📚
    
    Возвращает полный список всех книг, доступных в Грибной Библиотеке.
    
    ### Параметры:
    - `author` (опционально): Фильтр по имени автора
    
    ### Примеры:
    - `GET /other/books` - получить все книги
    - `GET /other/books?author=Достоевский` - получить книги Достоевского
    """,
    response_description="Список всех книг в библиотеке"
)
async def get_all_books(
    author: Optional[str] = Query(
        None,
        description="Фильтр по автору книги",
        example="Фёдор Достоевский"
    )
):
    """
    Получить список всех книг с возможностью фильтрации по автору.
    
    Args:
        author (str, optional): Имя автора для фильтрации
        
    Returns:
        List[BookResponse]: Список книг, соответствующих фильтру
    """
    if author:
        filtered_books = [
            book for book in books_db 
            if author.lower() in book["author"].lower()
        ]
        return filtered_books
    return books_db


@app.post(
    "/other/books",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Books"],
    summary="Добавить новую книгу",
    description="""
    Добавление новой книги в библиотеку.
    
    Создает новую запись о книге.
    
    ### Требования к данным:
    - `title`: Обязательное поле, от 1 до 200 символов
    - `author`: Обязательное поле, от 1 до 100 символов  
    - `publication_year`: Обязательное поле, от 1000 до 2100 года
    """,
    responses={
        201: {"description": "Книга успешно создана"},
        422: {"description": "Ошибка валидации данных"}
    }
)
async def create_book(book: BookCreate):
    """
    Создать новую книгу в библиотеке.
    
    Args:
        book (BookCreate): Данные новой книги
        
    Returns:
        BookResponse: Созданная книга с присвоенным ID
    """
    new_id = str(uuid.uuid4())[:8]  # Короткий ID для примера
    
    new_book = BookResponse(
        id=new_id,
        title=book.title,
        author=book.author,
        publication_year=book.publication_year
    )
    
    books_db.append(new_book.model_dump())
    
    return new_book


@app.get(
    "/other/books/{book_id}",
    response_model=BookResponse,
    tags=["Books"],
    summary="Получить книгу по ID",
    description="""
    Получение информации о конкретной книге по её ID.
    
    Параметры пути:
    - `book_id`: Уникальный идентификатор книги
    """,
    responses={
        200: {"description": "Успешный ответ с данными книги"},
        404: {"description": "Книга с указанным ID не найдена"}
    }
)
async def get_book_by_id(
    book_id: str = Path(
        ...,
        description="Уникальный идентификатор книги",
        example="1"
    )
):
    """
    Получить книгу по её уникальному идентификатору.
    
    Args:
        book_id (str): ID книги для поиска
        
    Returns:
        BookResponse: Найденная книга
        
    Raises:
        HTTPException: 404 если книга не найдена
    """
    for book in books_db:
        if book["id"] == book_id:
            return book
    
    raise HTTPException(
        status_code=404,
        detail=f"ВА-ХА... Книга с ID '{book_id}' куда-то запропастилась!"
    )


@app.put(
    "/other/books/{book_id}",
    response_model=BookResponse,
    tags=["Books"],
    summary="Обновить информацию о книге",
    description="""
    Обновление информации о существующей книге.
    
    Поддерживает частичное обновление (можно обновлять только нужные поля).
    """,
    responses={
        200: {"description": "Книга успешно обновлена"},
        404: {"description": "Книга с указанным ID не найдена"}
    }
)
async def update_book(
    book_update: BookUpdate,
    book_id: str = Path(
        ...,
        description="ID книги для обновления",
        example="1"
    )
):
    """
    Обновить информацию о существующей книге.
    
    Args:
        book_id (str): ID книги для обновления
        book_update (BookUpdate): Данные для обновления
        
    Returns:
        BookResponse: Обновленная книга
    """
    for index, book in enumerate(books_db):
        if book["id"] == book_id:
            update_data = book_update.model_dump(exclude_unset=True)
            
            # Обновляем только переданные поля
            for field, value in update_data.items():
                books_db[index][field] = value
            
            return books_db[index]
    
    raise HTTPException(
        status_code=404,
        detail=f"ВА-ХА... Книга с ID '{book_id}' не найдена для обновления!"
    )


@app.delete(
    "/other/books/{book_id}",
    tags=["Books"],
    summary="Удалить книгу",
    description="""
    Удаление книги из библиотеки по её ID.
    
    Внимание! Это действие необратимо!
    """,
    responses={
        200: {"description": "Книга успешно удалена"},
        404: {"description": "Книга с указанным ID не найдена"}
    }
)
async def delete_book(
    book_id: str = Path(
        ...,
        description="ID книги для удаления",
        example="1"
    )
):
    """
    Удалить книгу из библиотеки.
    
    Args:
        book_id (str): ID книги для удаления
        
    Returns:
        dict: Сообщение об удалении и данные удаленной книги
    """
    for index, book in enumerate(books_db):
        if book["id"] == book_id:
            deleted_book = books_db.pop(index)
            return {
                "message": f"Книга '{deleted_book['title']}' успешно удалена! ВА-ХА!",
                "deleted_book": deleted_book
            }
    
    raise HTTPException(
        status_code=404,
        detail=f"ВА-ХА... Книга с ID '{book_id}' не найдена для удаления!"
    )


@app.get(
    "/other/health",
    tags=["Health"],
    summary="Проверить статус сервера",
    description="""
    Проверка работоспособности сервера.
    
    Возвращает:
    - Статус сервера
    - Общее количество книг в библиотеке
    - Информацию о сервисе
    """,
    response_description="Статус сервера и статистика"
)
async def health_check():
    """
    Проверить работоспособность сервера.
    
    Returns:
        dict: Статус сервера и количество книг
    """
    return {
        "status": "healthy",
        "service": "other-service",
        "total_books": len(books_db),
        "message": "ВА-ХА! Other service работает как часы!"
    }


@app.get(
    "/other/stats",
    tags=["Books"],
    summary="Статистика библиотеки",
    description="""
    Получение статистики по библиотеке.
    
    Возвращает:
    - Общее количество книг
    - Уникальных авторов
    - Диапазон годов публикации
    """,
    response_description="Статистика библиотеки"
)
async def get_stats():
    """
    Получить статистику по библиотеке.
    
    Returns:
        dict: Статистическая информация
    """
    if not books_db:
        return {
            "total_books": 0,
            "unique_authors": 0,
            "year_range": None,
            "message": "Библиотека пуста! ВА-ХА!"
        }
    
    authors = set(book["author"] for book in books_db)
    years = [book["publication_year"] for book in books_db]
    
    return {
        "total_books": len(books_db),
        "unique_authors": len(authors),
        "year_range": {
            "min": min(years),
            "max": max(years)
        },
        "message": "ВА-ХА! Вот такая статистика!"
    }


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("OTHER SERVICE - Грибная Библиотека")
    print("=" * 50)
    print("Запуск на порту 8142...")
    print("Доступ через API Gateway: http://localhost/api/other/")
    print("Документация: http://localhost:8142/docs")
    print("=" * 50)
    uvicorn.run(
        "other_service:app",
        host="0.0.0.0",
        port=8142,
        reload=True,
        log_level="info"
    )