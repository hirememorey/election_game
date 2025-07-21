import asyncio
import os
import pty
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

app = FastAPI()

# Mount the static directory to serve index.html
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    # Redirect to the main page
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("INFO: WebSocket connection accepted.")

    master_fd, slave_fd = -1, -1
    process = None

    # Create a new pseudoterminal
    try:
        print("INFO: Attempting to open pseudoterminal...")
        master_fd, slave_fd = pty.openpty()
        print("INFO: Pseudoterminal opened successfully.")

        # Start the cli_game.py script as a subprocess connected to the pseudoterminal
        print("INFO: Starting cli_game.py subprocess...")
        process = await asyncio.create_subprocess_exec(
            "python3", "cli_game.py", "multi",
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            # Make the subprocess a new session leader
            preexec_fn=os.setsid
        )
        print(f"INFO: Subprocess started with PID: {process.pid}")

        # Bridge between the websocket and the pseudoterminal
        try:
            # Forward output from the pseudoterminal to the websocket
            async def forward_pty_to_ws():
                loop = asyncio.get_running_loop()
                reader = asyncio.StreamReader()
                protocol = asyncio.StreamReaderProtocol(reader)
                await loop.connect_read_pipe(lambda: protocol, os.fdopen(master_fd, 'rb', 0))

                while not reader.at_eof():
                    data = await reader.read(1024)
                    await websocket.send_text(data.decode())

            # Forward input from the websocket to the pseudoterminal
            async def forward_ws_to_pty():
                writer = os.fdopen(master_fd, 'wb', 0)
                while True:
                    data = await websocket.receive_text()
                    writer.write(data.encode())
                    writer.flush()

            # Run both forwarding tasks concurrently
            await asyncio.gather(forward_pty_to_ws(), forward_ws_to_pty())

        except WebSocketDisconnect:
            print("Client disconnected.")

    except Exception as e:
        error_message = f"ERROR: An exception occurred during subprocess setup: {e}"
        print(error_message)
        try:
            await websocket.send_text(error_message)
        except WebSocketDisconnect:
            pass # Client might have already disconnected

    finally:
        # When the connection is closed, terminate the game process
        if process and process.returncode is None:
            try:
                # Terminate the entire process group
                print(f"INFO: Terminating process group {os.getpgid(process.pid)}...")
                os.killpg(os.getpgid(process.pid), 15) # 15 = SIGTERM
                await process.wait()
                print("INFO: Process group terminated.")
            except ProcessLookupError:
                # Process might have already exited
                print("INFO: Process already exited.")
                pass

        if master_fd != -1:
            os.close(master_fd)
        if slave_fd != -1:
            os.close(slave_fd)
        print("INFO: Cleaned up file descriptors and closed connection.") 