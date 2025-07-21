from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect
from game_session import GameSession
import json
import asyncio

app = FastAPI()

# A simple dictionary to hold game sessions for each client
sessions = {}

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html")

async def run_ai_turns(game: GameSession, websocket: WebSocket):
    await asyncio.sleep(0.1) 
    while not game.is_human_turn() and not game.is_game_over():
        try:
            await asyncio.sleep(0.1) 
            logs = game.run_one_ai_action()
            new_state = game.get_state_for_client()
            new_state['log'] = logs
            await websocket.send_json(new_state)
        except Exception as e:
            error_message = f"Error during AI turn: {e}"
            print(error_message)
            # Send an error state to the client
            error_state = game.get_state_for_client()
            error_state['log'] = [error_message, "AI turn aborted. It is now the human's turn."]
            # It's better to reset to human turn to avoid getting stuck
            # This part needs a corresponding method in GameSession, e.g., force_next_turn()
            # For now, we just send the error and stop the AI loop.
            await websocket.send_json(error_state)
            break # Exit the AI loop

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