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

    # Create a new pseudoterminal
    master_fd, slave_fd = pty.openpty()

    # Start the cli_game.py script as a subprocess connected to the pseudoterminal
    process = await asyncio.create_subprocess_exec(
        "python3", "cli_game.py", "multi",
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        # Make the subprocess a new session leader
        preexec_fn=os.setsid
    )

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
    finally:
        # When the connection is closed, terminate the game process
        if process.returncode is None:
            try:
                # Terminate the entire process group
                os.killpg(os.getpgid(process.pid), 15) # 15 = SIGTERM
                await process.wait()
            except ProcessLookupError:
                # Process might have already exited
                pass
        os.close(master_fd)
        os.close(slave_fd) 