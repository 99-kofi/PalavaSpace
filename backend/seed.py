import asyncio
import json
from prisma import Prisma

async def main() -> None:
    prisma = Prisma()
    await prisma.connect()

    # Load personas
    with open("personas.json", "r") as f:
        personas_data = json.load(f)

    # Create default room
    room = await prisma.room.upsert(
        where={'slug': 'street-vibes'},
        data={
            'create': {
                'slug': 'street-vibes',
                'name': 'Street Vibes Room',
                'topic': 'General Palava',
            },
            'update': {
                'name': 'Street Vibes Room',
            }
        }
    )

    # Create personas and link to room
    for p in personas_data:
        await prisma.persona.upsert(
            where={'id': p['id']}, # Simple check if exists
            data={
                'create': {
                    'id': p['id'],
                    'name': p['name'],
                    'language': p['language'],
                    'style': p['style'],
                    'slangLevel': p['slang_level'],
                    'aggression': p['aggression'],
                    'topics': ",".join(p['topics']),
                    'bio': p['bio'],
                },
                'update': {
                    'name': p['name'],
                }
            }
        )
        
        # Link persona to room (many-to-many relationship)
        # Note: In prisma-client-py, managing m2m usually involves specific methods.
        # For simplicity in this script, we assume the room/persona exist.
        await prisma.room.update(
            where={'id': room.id},
            data={
                'agents': {
                    'connect': [{'id': p['id']}]
                }
            }
        )

    await prisma.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
