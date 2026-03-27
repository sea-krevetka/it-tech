import requests
import json
from typing import Dict, Any, Optional


def build_payload(query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Формирует словарь для отправки GraphQL запроса.
    
    :param query: Текст запроса (query или mutation).
    :param variables: Словарь с переменными.
    :return: Словарь с ключами "query" и "variables".
    """
    payload = {"query": query}
    
    if variables:
        payload["variables"] = variables
    
    return payload


def graphql_request(url: str, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Выполняет GraphQL запрос к серверу.
    
    :param url: URL GraphQL эндпоинта
    :param query: GraphQL запрос
    :param variables: Переменные запроса
    :return: Ответ сервера в виде словаря
    """
    payload = build_payload(query, variables)
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"errors": [{"message": f"HTTP Error: {response.status_code}"}]}


def get_products(url: str) -> Dict[str, Any]:
    # получение списка вех продуктов 
    query = """
    query GetProducts {
        products {
            id
            name
            price
            description
            sku
            created_at
        }
    }
    """
    
    return graphql_request(url, query)


def get_product(url: str, product_id: str) -> Dict[str, Any]:
    # получение по id
    query = """
    query GetProduct($id: ID!) {
        product(id: $id) {
            id
            name
            price
            description
            sku
            created_at
        }
    }
    """
    
    variables = {"id": product_id}
    return graphql_request(url, query, variables)


def create_product(url: str, name: str, price: float, sku: str, description: Optional[str] = None) -> Dict[str, Any]:
    mutation = """
    mutation CreateProduct($input: CreateProductInput!) {
        createProduct(input: $input) {
            id
            name
            price
            sku
            description
            created_at
        }
    }
    """
    
    variables = {
        "input": {
            "name": name,
            "price": price,
            "sku": sku
        }
    }
    
    if description:
        variables["input"]["description"] = description
    
    return graphql_request(url, mutation, variables)


def update_product(url: str, product_id: str, name: Optional[str] = None, 
                   price: Optional[float] = None, description: Optional[str] = None) -> Dict[str, Any]:
    mutation = """
    mutation UpdateProduct($id: ID!, $input: UpdateProductInput!) {
        updateProduct(id: $id, input: $input) {
            id
            name
            price
            description
            sku
            updated_at
        }
    }
    """
    
    variables = {"id": product_id, "input": {}}
    
    if name:
        variables["input"]["name"] = name
    if price:
        variables["input"]["price"] = price
    if description:
        variables["input"]["description"] = description
    
    return graphql_request(url, mutation, variables)


def delete_product(url: str, product_id: str) -> Dict[str, Any]:
    mutation = """
    mutation DeleteProduct($id: ID!) {
        deleteProduct(id: $id)
    }
    """
    
    variables = {"id": product_id}
    return graphql_request(url, mutation, variables)


def handle_response(response: Dict[str, Any]) -> None:
    # обработка ответа от сервера 
    if "errors" in response:
        print("❌ Ошибки:")
        for error in response["errors"]:
            print(f"  - {error.get('message', 'Unknown error')}")
            if "locations" in error:
                print(f"    Позиция: {error['locations']}")
    
    if "data" in response:
        print("\n✅ Данные:")
        print(json.dumps(response["data"], indent=2, ensure_ascii=False))
    
    if not response.get("data") and not response.get("errors"):
        print("⚠️ Неизвестный формат ответа")
        print(response)


def main():
    url = "http://localhost:8000/graphql"
    
    print("=" * 60)
    print("GraphQL Клиент для управления продуктами")
    print(f"project_code: products-s01")
    print("=" * 60)
    
    print("\n1. Создаем новый продукт...")
    response = create_product(
        url=url,
        name="Ноутбук Waluigi Pro",
        price=99999.99,
        sku="WALUIGI-001",
        description="Сверхмощный ноутбук для захвата королевсв"
    )
    handle_response(response)
    
    if "data" in response and response["data"].get("createProduct"):
        product_id = response["data"]["createProduct"]["id"]
        
        print(f"\n2. Получаем продукт с ID {product_id}...")
        response = get_product(url, product_id)
        handle_response(response)
        
        print("\n3. Обновляем продукт...")
        response = update_product(
            url, 
            product_id, 
            price=89999.99,
            description="Ноутбук со скидкой (Ва-ха-ха!)"
        )
        handle_response(response)
        
        print("\n4. Удаляем продукт...")
        response = delete_product(url, product_id)
        handle_response(response)
    
    print("\n5. Получаем список всех продуктов...")
    response = get_products(url)
    handle_response(response)


if __name__ == "__main__":
    # build_payload
    print("Тестирование build_payload:")
    payload = build_payload(
        "query GetProduct($id: ID!) { product(id: $id) { name } }",
        {"id": "123"}
    )
    print(f"Результат: {json.dumps(payload, indent=2)}")
    
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Не удалось подключиться к серверу.")
        print("Убедитесь, что GraphQL сервер запущен на http://localhost:8000/graphql")
        print("Запустите сервер: uvicorn weeks/week-05/app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")