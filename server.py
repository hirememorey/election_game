from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect
from game_session import GameSession
import json

app = FastAPI()

# A simple dictionary to hold game sessions for each client
sessions = {}

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html")

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
            all_logs = game.process_human_action(action_data)
            
            # Send the new state back to the client
            new_state = game.get_state_for_client()
            new_state['log'] = all_logs # Make sure the log includes everything that happened
            await websocket.send_json(new_state)

    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected.")
        del sessions[client_id]
    except Exception as e:
        print(f"An error occurred with client {client_id}: {e}")
        if client_id in sessions:
            del sessions[client_id] 