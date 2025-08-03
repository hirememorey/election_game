from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from game_session import GameSession
import json

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse('static/index.html')

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session = GameSession()
    session.start_game()
    
    try:
        # Send initial state
        state_data = session.get_state_for_client()
        await websocket.send_text(json.dumps(state_data))

        while not session.is_game_over():
            # Wait for human action
            action_data = await websocket.receive_text()
            session.process_human_action(json.loads(action_data))
            
            # Send state update after human action
            current_state = session.get_state_for_client()
            await websocket.send_text(json.dumps(current_state))

            # Run AI turns until it's the human's turn again
            while not session.is_human_turn() and not session.is_game_over():
                session.process_ai_turn()
                state_data = session.get_state_for_client()
                
                # Add flag to signal the client to wait for acknowledgement
                state_data['awaiting_acknowledgement'] = True
                await websocket.send_text(json.dumps(state_data))
                
                # Wait for acknowledgement from the client
                await websocket.receive_text()

        # Game is over, send final scores and close
        final_state = session.get_state_for_client()
        final_state['game_over'] = True
        final_state['scores'] = session.engine.get_final_scores(session.state)
        await websocket.send_text(json.dumps(final_state))

    except WebSocketDisconnect:
        print(f"Client {websocket.client} disconnected.")
    except Exception as e:
        print(f"An error occurred: {e}")
        # Optionally send an error message to the client
        try:
            await websocket.send_text(json.dumps({"error": str(e)}))
        except RuntimeError:
            print("Could not send error message, connection already closed.")
    finally:
        print("WebSocket connection handler finished.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001) 