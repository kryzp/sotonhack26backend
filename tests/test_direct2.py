from app.database import engine, init_db
from app.game_service import create_game
from sqlmodel import Session

# Ensure DB is initialized
init_db()

with Session(engine) as session:
    try:
        game = create_game(session, 3, "team", "medium", "Test1", "Test2")
        print("Success:", game)
    except Exception as e:
        import traceback
        traceback.print_exc()
