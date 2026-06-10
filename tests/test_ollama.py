import asyncio
from httpx import AsyncClient

async def run():
    async with AsyncClient(base_url="http://localhost:8000", timeout=60.0) as client:
        print("Creating game...")
        r = await client.post("/games", json={"rounds": 3, "mode": "team"})
        try:
            game = r.json()
        except Exception as e:
            print("Failed to decode json!", r.text)
            return
        
        print("Game created:", game.get("id"))
        game_id = game["id"]
        
        print("Starting game...")
        r2 = await client.post(f"/games/{game_id}/start")
        print("Start returned:", r2.status_code)
        
        print("Getting round 1...")
        r3 = await client.post(f"/games/{game_id}/next-round")
        rnd = r3.json()
        print(f"Round 1 words: {rnd.get('word_one')} connects to {rnd.get('word_two')}")

asyncio.run(run())
