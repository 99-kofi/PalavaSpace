import os
import asyncio
import threading
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
from config import Config
from rooms.room_manager import room_manager
from rooms.orchestrator import orchestrator
from moderation.filters import moderate

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/room/<room_id>")
def room(room_id):
    return render_template("room.html", room_id=room_id)

@socketio.on("join")
def on_join(data):
    room_id = data.get("room_id", Config.DEFAULT_ROOM)
    join_room(room_id)
    print(f"Client {request.sid} joined room: {room_id}")
    
    room = room_manager.get_or_create_room(room_id)
    room.add_user(request.sid)
    
    # Set the broadcast method for this room
    room.broadcast_method = lambda msg: socketio.emit("message", msg, room=room_id)
    
    emit("message", {
        "sender": "system",
        "content": "You don enter de arena! Vibes loading...",
        "type": "info"
    })

@socketio.on("disconnect")
def on_disconnect():
    print(f"Client {request.sid} disconnected.")
    # In a real app, we'd track what rooms they are in. 
    # For MVP, we check all active rooms and remove them.
    for room in room_manager.rooms.values():
        room.remove_user(request.sid)

@socketio.on("reaction")
def handle_reaction(data):
    room_id = data.get("room_id", Config.DEFAULT_ROOM)
    emoji = data.get("emoji")
    username = data.get("username", "Anonymous Paddy")
    if emoji:
        # Broadcast reaction to everyone in the room
        socketio.emit("reaction", {
            "emoji": emoji,
            "username": username
        }, room=room_id)

@socketio.on("trigger_topic")
def handle_topic(data):
    room_id = data.get("room_id", Config.DEFAULT_ROOM)
    topic = data.get("topic")
    if topic and moderate(topic):
        room = room_manager.get_or_create_room(room_id)
        room.current_topic = topic
        socketio.emit("message", {
            "sender": "system",
            "content": f"🔥 NEW TOPIC: {topic}",
            "type": "info"
        }, room=room_id)
        
        # Trigger immediate topic discussion in a background thread
        def trigger_discussion():
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(orchestrator.trigger_topic_discussion(room, topic))
            loop.close()
        
        import threading
        t = threading.Thread(target=trigger_discussion, daemon=True)
        t.start()

def start_background_tasks():
    async def run_loops():
        # Initialize default room with personas
        room = room_manager.get_or_create_room(Config.DEFAULT_ROOM)
        personas_to_add = [
            "area_chairman", "campus_big_boy", "auntie_akos", "kojo_streets",
            "hon_kobby", "susu_slay", "bra_mike", "mate_lapaz"
        ]
        for p_id in personas_to_add:
            await room.add_agent(p_id)
            
        # Start the loop
        await orchestrator.run_room_loop(room)

    def thread_wrapper():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_loops())
        loop.run_forever()

    t = threading.Thread(target=thread_wrapper, daemon=True)
    t.start()

if __name__ == "__main__":
    print("--- 🚀 STARTING PALAVASPACE SERVER ---")
    start_background_tasks()
    print("--- 🏟️ ARENA READY ON http://localhost:5050 ---")
    socketio.run(app, host='0.0.0.0', port=5050, debug=True, use_reloader=False)
