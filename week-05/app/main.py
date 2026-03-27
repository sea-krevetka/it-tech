import uuid
import datetime
from typing import List, Optional
from fastapi import FastAPI
import strawberry
from strawberry.fastapi import GraphQLRouter

# In-memory база данных
items_db = []

@strawberry.type
class Item:
    id: str
    name: str
    description: Optional[str]
    price: float
    sku: str
    created_at: str

@strawberry.input
class CreateItemInput:
    name: str
    description: Optional[str] = None
    price: float
    sku: str

@strawberry.type
class Query:
    @strawberry.field
    def items(self) -> List[Item]:
        return items_db
    
    @strawberry.field
    def item(self, id: str) -> Optional[Item]:
        for item in items_db:
            if item.id == id:
                return item
        return None

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_item(self, input: CreateItemInput) -> Item:
        new_item = Item(
            id=str(uuid.uuid4())[:8],
            name=input.name,
            description=input.description,
            price=input.price,
            sku=input.sku,
            created_at=datetime.datetime.now().isoformat()
        )
        items_db.append(new_item)
        return new_item

schema = strawberry.Schema(query=Query, mutation=Mutation)
app = FastAPI(title="GraphQL Items API")
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {"message": "GraphQL API работает! Заходите на /graphql"}