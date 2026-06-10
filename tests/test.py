import asyncio
import httpx
import os

async def run_test():
    async with httpx.AsyncClient(base_url="http://localhost:5173/") as client:
        # Create game
        print("Creating game...")
        r = await client.post("/games", json={"rounds": 3, "mode": "team"})
        game = r.json()
        game_id = game["id"]
        print(f"Game created: {game_id}")
        
        # Start game
        print("Starting game...")
        r = await client.post(f"/games/{game_id}/start")
        print(r.status_code)
        
        # Play 3 rounds
        for i in range(3):
            print(f"--- ROUND {i+1} ---")
            
            # Next round
            r = await client.post(f"/games/{game_id}/next-round")
            rnd = r.json()
            print(f"Words: {rnd['word_one']} -> {rnd['word_two']}")
            
            # Open buzz
            await client.post(f"/games/{game_id}/rounds/current/open-buzz")
            
            # Buzz
            await client.post(f"/games/{game_id}/rounds/current/buzz", json={"player_id": "player1"})
            
            # Select side
            # alternate sides
            side = "left" if i % 2 == 0 else "right"
            await client.post(f"/games/{game_id}/rounds/current/select-side", json={"side": side})
            
            # Submit final answer
            await client.post(f"/games/{game_id}/rounds/current/final-answer", json={"answer": "mock answer"})
            
            # Validate
            r = await client.post(f"/games/{game_id}/rounds/current/validate")
            rnd = r.json()
            print(f"Validation results:")
            print(f"  Valid: {rnd['validation_valid']}")
            print(f"  Score: {rnd['validation_score']}")
            print(f"  Steps: {rnd['validation_steps']}")
            print(f"  Reason: {rnd['validation_reason']}")
            
            # Get game state
            r = await client.get(f"/games/{game_id}")
            game = r.json()
            print(f"Game State - Left: {game['team_left_score']}, Right: {game['team_right_score']}, Status: {game['status']}")
            if game['status'] == 'finished':
                print(f"WINNER: {game['winner']}")

if __name__ == "__main__":
    asyncio.run(run_test())
