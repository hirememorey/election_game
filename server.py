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

        while not game.is_game_over():
            data = await websocket.receive_text()
            action_data = json.loads(data)

            # Process the received action.
            logs = game.process_action(action_data)
            
            # If the action was from the human, now we run the AI turns.
            if game.is_human_turn():
                 # It's human's turn again, send state and wait for action.
                new_state = game.get_state_for_client()
                new_state['log'] = logs
                await websocket.send_json(new_state)
                continue

            # It's AI's turn to act.
            # After a human action, or a 'continue', run AI turns until it's the human's turn again.
            while not game.is_human_turn() and not game.is_game_over():
                ai_logs = game.run_ai_turn()
                logs.extend(ai_logs)

                # Send the state after the AI's turn and wait for 'continue'.
                new_state = game.get_state_for_client()
                new_state['log'] = logs
                await websocket.send_json(new_state)

                # If it's now the human's turn, break this loop and wait for their action.
                if game.is_human_turn() or game.is_game_over():
                    break
                
                # Wait for a 'continue' message from the client.
                continue_data = await websocket.receive_text()
                continue_action = json.loads(continue_data)
                if continue_action.get("action_type") != "continue":
                    # Handle cases where we don't get a continue.
                    # For now, we'll just log it. A more robust implementation
                    # could send an error to the client.
                    print(f"Warning: Expected 'continue' action, but got: {continue_action}")
                    # We will still continue the loop.
                
                logs = [] # Clear logs for the next AI turn


    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected.")
        sessions.pop(client_id, None) # Use pop for safe removal
    except Exception as e:
        print(f"An error occurred with client {client_id}: {e}")
        sessions.pop(client_id, None) # Use pop for safe removal

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001) 