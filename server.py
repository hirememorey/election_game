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
            
            # Here, you would parse the incoming data to determine the action
            # For now, we'll just log it. This is where you'll build out
            # the handling for player actions sent from the client.
            print(f"Received from client: {data}")

            # Example: action processing (to be fully implemented)
            # action = parse_action_from_data(data)
            # game.process_human_action(action)
            # ai_logs = game._run_ai_turns()
            
            # new_state = game.get_state_for_client()
            # new_state['log'].extend(ai_logs)
            # await websocket.send_json(new_state)

    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected.")
        del sessions[client_id]
    except Exception as e:
        print(f"An error occurred with client {client_id}: {e}")
        if client_id in sessions:
            del sessions[client_id] 