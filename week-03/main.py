from fastapi import FastAPI, HTTPException, status
from typing import List
from schemas import Product, ProductCreate, ProductUpdate
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Waluigi's Inventory Empire",
    root_path="/api"
)
db = []
counter = 1

@app.post("/items/products/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate):
    global counter
    
    if not product.name or product.name.strip() == "":
        raise HTTPException(
            status_code=400, 
            detail="Имя товара не может быть пустым! Ва-а-а!"
        )
    
    if hasattr(product, 'price') and product.price < 0:
        raise HTTPException(
            status_code=400, 
            detail="Отрицательная цена?"
        )
    
    try:
        new = Product(id=counter, **product.model_dump())
        db.append(new)
        counter += 1
        return new
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Что-то пошло не так... даже для Валлуиджи! Ошибка: {str(e)}"
        )

@app.get("/items/products/", response_model=List[Product])
async def get_products():
    if not db:
        return []
    return db

@app.get("/items/products/{pid}", response_model=Product)
async def get_product(pid: int):
    if pid <= 0:
        raise HTTPException(
            status_code=400, 
            detail="Отрицательный ID? Ва-а-а!"
        )
    
    for p in db:
        if p.id == pid:
            return p
    
    raise HTTPException(
        status_code=404, 
        detail=f"Товар с ID {pid} исчез, как будто его Баузер украл!"
    )

@app.put("/items/products/{pid}", response_model=Product)
async def update_product(pid: int, product_update: ProductUpdate):
    
    if pid <= 0:
        raise HTTPException(
            status_code=400, 
            detail="Ва-а-а! ID должен быть положительным числом!"
        )
    
    update_data = product_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Нет ничего для обновления! Ва-ха-ха!"
        )
    
    for i, p in enumerate(db):
        if p.id == pid:
            try:
                if 'name' in update_data and (not update_data['name'] or update_data['name'].strip() == ""):
                    raise ValueError("Имя товара не может быть пустым!")
                
                if 'price' in update_data and update_data['price'] < 0:
                    raise ValueError("Цена не может быть отрицательной!")
                
                for field, value in update_data.items():
                    setattr(p, field, value)
                return p
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Ва-а-а! Ошибка при обновлении: {str(e)}"
                )
    
    raise HTTPException(
        status_code=404, 
        detail=f"Товар с ID {pid} не найден! Ва-ха-ха! Может, его Марио съел?"
    )

@app.delete("/items/products/{pid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(pid: int):
    
    if pid <= 0:
        raise HTTPException(
            status_code=400, 
            detail="Ва-а-а! Нельзя удалить товар с таким ID!"
        )
    
    for i, p in enumerate(db):
        if p.id == pid:
            deleted_item = db.pop(i)
            print(f"Ва-ха-ха! Товар '{deleted_item.name}' удалён! Ещё один проигрыш Марио!")
            return
    
    raise HTTPException(
        status_code=404, 
        detail=f"Товар с ID {pid} и так уже исчез! Ва-ха-ха!"
    )

@app.exception_handler(Exception)
async def waluigi_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": f"Ва-а-а! Что-то пошло не так! {str(exc)}"},
    )