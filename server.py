from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect
from game_session import GameSession
import json
from fastapi.responses import FileResponse

app = FastAPI()

# A simple dictionary to hold game sessions for each client.
# This is suitable for a single-player game where each connection is a new game.
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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = f"{websocket.client.host}:{websocket.client.port}"
    
    # Create a new game session for each new connection.
    game = GameSession()
    game.start_game()
    sessions[client_id] = game
    print(f"New client connected, starting new game: {client_id}")
    
    try:
        # Send the initial game state.
        initial_state = game.get_state_for_client()
        await websocket.send_json(initial_state)

        while True:
            data = await websocket.receive_text()
            action_data = json.loads(data)
            
            # The game session now handles the full turn cycle (human + all AIs).
            logs = game.process_human_action(action_data)
            
            # Send the final state back to the client after all turns are complete.
            new_state = game.get_state_for_client()
            new_state['log'] = logs
            await websocket.send_json(new_state)

    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected.")
        if client_id in sessions:
            del sessions[client_id]
    except Exception as e:
        print(f"An error occurred with client {client_id}: {e}")
        if client_id in sessions:
            del sessions[client_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001) 