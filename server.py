from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect
from game_session import GameSession
import json
import asyncio
from fastapi.responses import FileResponse

app = FastAPI()

# A simple dictionary to hold game sessions for each client
sessions = {}

# Use an absolute path for the static directory
import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_dir, 'index.html'))

async def run_ai_turns(game: GameSession, websocket: WebSocket):
    """
    Process all AI turns until it's the human's turn again.
    This function will now process an entire AI turn at once and send a single update.
    """
    await asyncio.sleep(0.5)  # A small delay to allow the UI to settle.

    while not game.is_human_turn() and not game.is_game_over():
        try:
            # Process the full turn for the current AI player.
            logs = game.run_full_ai_turn()
            
            # Send a single update with all the logs from that turn.
            new_state = game.get_state_for_client()
            new_state['log'] = logs
            await websocket.send_json(new_state)

            # Add a delay between different AI players' turns for better UX.
            if not game.is_human_turn():
                await asyncio.sleep(1.0)

        except Exception as e:
            error_message = f"Error during AI turn: {e}"
            print(error_message)
            error_state = game.get_state_for_client()
            error_state['log'] = [error_message, "AI turn aborted. It is now the human's turn."]
            await websocket.send_json(error_state)
            break

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = websocket.client.host  # Use client IP as a simple identifier

    # Create a new game session for the new client
    game = GameSession()
    game.start_game()
    sessions[client_id] = game
    
    try:
        # Send the initial game state
        initial_state = game.get_state_for_client()
        await websocket.send_json(initial_state)

        while True:
            data = await websocket.receive_text()
            action_data = json.loads(data)
            
            # Process the human's action and get all the logs
            logs = game.process_human_action(action_data)
            
            # Send the new state back to the client
            new_state = game.get_state_for_client()
            new_state['log'] = logs # Make sure the log includes everything that happened
            await websocket.send_json(new_state)

            if not game.is_human_turn():
                asyncio.create_task(run_ai_turns(game, websocket))

    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected.")
        del sessions[client_id]
    except Exception as e:
        print(f"An error occurred with client {client_id}: {e}")
        if client_id in sessions:
            del sessions[client_id] 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001) 