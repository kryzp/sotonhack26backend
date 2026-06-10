import asyncio
import httpx
from pydantic import BaseModel

async def main():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post("http://localhost:8000/games", json={
                "rounds": 3,
                "mode": "team",
                "difficulty": "medium",
                "team_left_name": "Test1",
                "team_right_name": "Test2"
            })
            print("Status:", resp.status_code)
            print("Response:", resp.text)
    except Exception as e:
        print("Error:", e)

asyncio.run(main())
