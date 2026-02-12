import random
import asyncio
from typing import Optional
from .room_manager import Room
from config import Config

class Orchestrator:
    def __init__(self):
        self.topic_queue = asyncio.Queue()
    
    async def decide_next_speaker(self, room: Room) -> Optional[dict]:
        if not room.active_agents:
            return None
        
        last_msg = room.history[-1] if room.history else {}
        last_sender = last_msg.get("sender")
        last_content = last_msg.get("content", "").lower()
        
        # Priority 1: Smart Interjections (Mentions)
        mentions = []
        for agent in room.active_agents:
            if agent["name"].lower() in last_content and agent["id"] != last_sender:
                mentions.append(agent)
        
        if mentions:
            print(f"Orchestrator [{room.room_id}]: Mentions found! {mentions[0]['name']} is responding.")
            return random.choice(mentions)

        # Priority 2: Variety (Avoid the last 2 speakers)
        recent_senders = [msg.get("sender") for msg in room.history[-2:] if msg.get("sender")]
        selectable = [a for a in room.active_agents if a["id"] not in recent_senders]
        
        if not selectable:
            selectable = [a for a in room.active_agents if a["id"] != last_sender]
            
        if not selectable:
            selectable = room.active_agents
            
        return random.choice(selectable)

    async def trigger_topic_discussion(self, room: Room, topic: str):
        """Immediately triggers a burst of agent discussions about a new topic."""
        print(f"🔥 Orchestrator [{room.room_id}]: NEW TOPIC TRIGGERED - '{topic}'")
        
        # Get 3-5 random agents to discuss the topic
        burst_len = random.randint(3, 5)
        available_agents = room.active_agents.copy()
        random.shuffle(available_agents)
        
        for i in range(min(burst_len, len(available_agents))):
            agent = available_agents[i]
            print(f"🗣️ Orchestrator [{room.room_id}]: {agent['name']} weighing in on '{topic}'...")
            await room.trigger_agent_response(agent, topic)
            await asyncio.sleep(random.randint(2, 4))  # Quick succession

    async def run_room_loop(self, room: Room):
        print(f"Orchestrator: Loop started for {room.room_id}")
        while True:
            if not room.active_users:
                await asyncio.sleep(5)
                continue

            # 30% chance for a 'Burst' of rapid interaction
            is_burst = random.random() < 0.3
            
            if is_burst:
                burst_len = random.randint(2, 4)
                print(f"Orchestrator [{room.room_id}]: Entering BURST MODE ({burst_len} messages)")
                for _ in range(burst_len):
                    if not room.active_users: break 
                    next_agent = await self.decide_next_speaker(room)
                    if next_agent:
                        await room.trigger_agent_response(next_agent)
                        await asyncio.sleep(random.randint(2, 5)) 
            else:
                # Normal cooldown
                sleep_time = random.randint(*Config.CHAT_COOLDOWN)
                print(f"Orchestrator [{room.room_id}]: Normal turn. Waiting {sleep_time}s...")
                await asyncio.sleep(sleep_time)
                
                if room.active_users:
                    next_agent = await self.decide_next_speaker(room)
                    if next_agent:
                        await room.trigger_agent_response(next_agent)

orchestrator = Orchestrator()
