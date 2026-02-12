import random
import asyncio
from typing import List, Optional
from .room_manager import Room

class Orchestrator:
    def __init__(self):
        self.active_conversations: List[str] = []

    async def decide_next_speaker(self, room: Room) -> Optional[dict]:
        """
        Decides who should speak next based on the recent history and agent traits.
        """
        if not room.agents:
            return None
        
        # Simple round-robin with occasional "interruption" (randomness)
        # In a real version, this would check aggression and ego traits.
        
        last_sender = None
        if room.history:
            last_sender = room.history[-1].get("sender")
        
        selectable_agents = [a for a in room.agents if a["id"] != last_sender]
        
        if not selectable_agents:
            # If only one agent, they can speak again (rare)
            selectable_agents = room.agents
            
        # 20% chance of a "chaos" injection (conflict)
        if random.random() < 0.2:
            # Pick the most aggressive agent
            selectable_agents.sort(key=lambda x: x.get("aggression", 0), reverse=True)
            return selectable_agents[0]
            
        return random.choice(selectable_agents)

    async def run_room_loop(self, room: Room):
        """
        Main loop for a room to keep the conversation going.
        """
        print(f"Orchestrator: Room {room.room_id} loop started.")
        while True:
            await asyncio.sleep(random.randint(5, 12)) 
            
            if not room.agents:
                print(f"Orchestrator [{room.room_id}]: No agents. Skipping.")
                continue
                
            next_agent = await self.decide_next_speaker(room)
            if next_agent:
                print(f"Orchestrator [{room.room_id}]: {next_agent['name']} selected to speak.")
                await room.trigger_agent_response(next_agent)
            else:
                print(f"Orchestrator [{room.room_id}]: No speaker selected.")




orchestrator = Orchestrator()
