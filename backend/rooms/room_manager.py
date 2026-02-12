from typing import Dict, List, Optional, Callable
import asyncio
from ai.personas import PERSONAS
from ai.prompt_builder import build_prompt
from ai.response_filter import clean_response, apply_street_vibe
from config import Config
import os
import json
import requests
from gradio_client import Client

class Room:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.active_agents: List[dict] = []
        self.history: List[dict] = []
        self.current_topic: str = "General Palava"
        self.energy: float = 0.5
        self.broadcast_method: Optional[Callable] = None
        self.active_users: set = set()

    def add_user(self, sid: str):
        self.active_users.add(sid)
        print(f"Room [{self.room_id}]: User {sid} joined. Total users: {len(self.active_users)}")

    def remove_user(self, sid: str):
        if sid in self.active_users:
            self.active_users.remove(sid)
            print(f"Room [{self.room_id}]: User {sid} left. Total users: {len(self.active_users)}")

    async def add_agent(self, agent_id: str):
        if agent_id in PERSONAS:
            agent = PERSONAS[agent_id]
            self.active_agents.append(agent)
            await self.broadcast({
                "sender": "system",
                "content": f"{agent['name']} don join de palava!",
                "type": "info"
            })

    async def broadcast(self, message: dict):
        self.history.append(message)
        if self.broadcast_method:
            print(f"Room [{self.room_id}]: Broadcasting message from {message.get('sender_name', message.get('sender'))}")
            # Strip reasoning_details for frontend
            clean_msg = {k: v for k, v in message.items() if k != 'reasoning_details'}
            self.broadcast_method(clean_msg)
        else:
            print(f"Room [{self.room_id}]: No broadcast method set. Message stored in history.")

    async def trigger_agent_response(self, agent: dict, topic_override: str = None):
        if not self.active_users:
            print(f"Room [{self.room_id}]: No active users. Skipping AI turn.")
            return

        from ai.engine import ai_engine
        
        # Use topic override if provided, otherwise use current topic
        topic = topic_override if topic_override else self.current_topic
        
        print(f"Room [{self.room_id}]: Generating AI response for {agent['name']} on topic: {topic}...")
        
        try:
            raw_text, engine_reasoning = await ai_engine.generate_response(
                persona=agent,
                context=self.history,
                topic=topic
            )
            
            # Clean and extract thinking vs response
            thinking, content = clean_response(raw_text, agent['name'])
            content = apply_street_vibe(content, agent)
            
            # Use engine reasoning if provided, otherwise use parsed thinking
            reasoning = engine_reasoning if engine_reasoning else thinking

            await self.broadcast({
                "sender": agent["id"],
                "sender_name": agent["name"],
                "content": content,
                "reasoning_details": reasoning,
                "type": "chat"
            })
            
        except Exception as e:
            print(f"Room [{self.room_id}]: AI Engine Error: {e}")

class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}

    def get_or_create_room(self, room_id: str) -> Room:
        if room_id not in self.rooms:
            self.rooms[room_id] = Room(room_id)
        return self.rooms[room_id]

room_manager = RoomManager()
