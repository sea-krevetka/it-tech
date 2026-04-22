import asyncio
import json
import websockets
from typing import Set, Dict

# Хранилище комнат и участников
# Структура: {room_id: {websocket: username}}
rooms: Dict[str, Dict[websockets.WebSocketServerProtocol, str]] = {}

async def handler(websocket: websockets.WebSocketServerProtocol):
    """Обработчик WebSocket соединений"""
    current_room = None
    username = None
    
    try:
        async for message in websocket:
            data = json.loads(message)
            msg_type = data.get("type")
            
            if msg_type == "join":
                # Клиент присоединяется к комнате
                current_room = data.get("room", "default")
                username = data.get("username", f"User_{id(websocket) % 1000}")
                
                # Добавляем в комнату
                if current_room not in rooms:
                    rooms[current_room] = {}
                rooms[current_room][websocket] = username
                
                print(f"✅ {username} присоединился к комнате '{current_room}'")
                
                # Отправляем подтверждение самому пользователю
                await websocket.send(json.dumps({
                    "type": "joined",
                    "username": username,
                    "room": current_room,
                    "users": list(rooms[current_room].values())
                }))
                
                # Уведомляем ВСЕХ остальных участников о новом пользователе
                await broadcast_to_room(current_room, {
                    "type": "user_joined",
                    "username": username,
                    "users": list(rooms[current_room].values())
                }, exclude=websocket)
                
            elif msg_type == "webrtc":
                # Пересылаем WebRTC сигналы (SDP, ICE candidates)
                target_username = data.get("target")
                signal = data.get("signal")
                
                if current_room and target_username:
                    # Отправляем сигнал конкретному пользователю
                    await send_to_user_in_room(current_room, target_username, {
                        "type": "webrtc",
                        "from": username,
                        "signal": signal
                    })
                    
            elif msg_type == "get_users":
                # Запрос списка пользователей
                if current_room and current_room in rooms:
                    await websocket.send(json.dumps({
                        "type": "users_list",
                        "users": list(rooms[current_room].values())
                    }))
                    
            elif msg_type == "leave":
                # Клиент покидает комнату
                if current_room and websocket in rooms.get(current_room, {}):
                    username = rooms[current_room][websocket]
                    del rooms[current_room][websocket]
                    
                    # Уведомляем остальных
                    await broadcast_to_room(current_room, {
                        "type": "user_left",
                        "username": username,
                        "users": list(rooms[current_room].values())
                    })
                    
                    print(f"👋 {username} покинул комнату '{current_room}'")
                    
    except websockets.exceptions.ConnectionClosed:
        print(f"🔌 Клиент отключился")
    finally:
        # Очистка при отключении
        if current_room and current_room in rooms and websocket in rooms[current_room]:
            username = rooms[current_room][websocket]
            del rooms[current_room][websocket]
            
            if rooms[current_room]:
                await broadcast_to_room(current_room, {
                    "type": "user_left",
                    "username": username,
                    "users": list(rooms[current_room].values())
                })
            
            print(f"👋 {username} покинул комнату '{current_room}'")


async def broadcast_to_room(room: str, message: dict, exclude=None):
    """Отправить сообщение всем в комнате, кроме указанного"""
    if room in rooms:
        disconnected = []
        for ws in rooms[room]:
            if ws != exclude:
                try:
                    await ws.send(json.dumps(message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected.append(ws)
        
        # Удаляем отключившихся
        for ws in disconnected:
            if ws in rooms[room]:
                del rooms[room][ws]


async def send_to_user_in_room(room: str, target_username: str, message: dict):
    """Отправить сообщение конкретному пользователю в комнате"""
    if room in rooms:
        for ws, username in rooms[room].items():
            if username == target_username:
                try:
                    await ws.send(json.dumps(message))
                    return True
                except:
                    return False
    return False


async def main():
    """Запуск WebSocket сервера"""
    print("=" * 60)
    print("WebRTC Signaling Server")
    print("project_code: bookings-s01")
    print("WebSocket: ws://localhost:8765")
    print("=" * 60)
    
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())