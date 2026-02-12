from typing import Dict, List, Set, Optional, Callable
from .ai_engine import ai_engine


class Room:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.active_connections: Set = set()
        self.agents: List[dict] = []
        self.history: List[dict] = []
        self.current_topic: str = "General Palava"
        self.broadcast_method: Optional[Callable] = None

    def connect(self, connection):
        self.active_connections.add(connection)
        print(f"Room {self.room_id}: User {connection} connected. Total: {len(self.active_connections)}")

    def disconnect(self, connection):
        if connection in self.active_connections:
            self.active_connections.remove(connection)
            print(f"Room {self.room_id}: User {connection} disconnected. Remaining: {len(self.active_connections)}")


    async def add_agent(self, agent_data: dict):
        self.agents.append(agent_data)
        await self.broadcast({
            "sender": "system",
            "content": f"{agent_data['name']} don join the palava!",
            "type": "info"
        })

    async def broadcast(self, message: dict):
        self.history.append(message)
        if self.broadcast_method:
            self.broadcast_method(message)
        else:
            print(f"Room {self.room_id}: No broadcast method set. History updated.")

    async def trigger_agent_response(self, agent: dict):
        print(f"Room {self.room_id}: Triggering response for {agent['name']}...")
        response_text, reasoning_details = await ai_engine.generate_response(agent, self.history, self.current_topic)
        print(f"Room {self.room_id}: Received response for {agent['name']}: {response_text[:50]}...")
        await self.broadcast({
            "sender": agent["id"],
            "sender_name": agent["name"],
            "content": response_text,
            "reasoning_details": reasoning_details,
            "type": "chat"
        })



import json

class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}

    def get_or_create_room(self, room_id: str) -> Room:
        if room_id not in self.rooms:
            self.rooms[room_id] = Room(room_id)
        return self.rooms[room_id]

room_manager = RoomManager()
