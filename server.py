from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect
from game_session import GameSession
import json
from fastapi.responses import FileResponse
from typing import Dict, Any

app = FastAPI()

# Serve static files from the "static" directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    """Serves the main HTML page."""
    return FileResponse('static/index.html')

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print(f"New client connected, starting new game: {websocket.client}")
    # Create a new game session for this client
    session = GameSession()
    session.start_game()

    try:
        while not session.is_game_over():
            # Send the current game state to the client
            state_data = session.get_state_for_client()
            await websocket.send_json(state_data)

            if state_data.get("awaiting_ai_acknowledgement"):
                # If we are waiting for acknowledgement, we don't need to do anything
                # but wait for the next message from the client.
                pass
            
            # Wait for an action from the client
            action_data = await websocket.receive_json()

            # Process the action
            try:
                session.process_action(action_data)
            except Exception as e:
                print(f"Error processing action: {e}")
                # Send an error message to the client
                await websocket.send_json({"error": str(e)})
            
            # If the game is over, send final scores and close
            if session.is_game_over():
                final_scores = session.engine.get_final_scores(session.state)
                await websocket.send_json({"game_over": True, "scores": final_scores})
                break

    except WebSocketDisconnect:
        print(f"Client {websocket.client} disconnected.")
    except Exception as e:
        print(f"An error occurred in the websocket: {e}")
        await websocket.send_json({"error": str(e)})
    finally:
        print("INFO:     connection closed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001) 