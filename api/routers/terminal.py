import asyncio
import os
import shutil
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.concurrency import run_in_threadpool
from api.dependencies import logger, root_dir

router = APIRouter(prefix="/api/ws", tags=["Terminal"])

@router.websocket("/terminal")
async def websocket_terminal(websocket: WebSocket):
    await websocket.accept()
    logger.info("Terminal WebSocket connected")
    
    # Determine shell (PowerShell on Windows, bash/sh on others)
    shell = "powershell.exe" if os.name == 'nt' else "bash"
    
    # Create subprocess
    # Note: On Windows without a PTY, this is not a perfect terminal emulation 
    # (e.g. no colors, no raw mode), but sufficient for basic commands.
    
    process = await asyncio.create_subprocess_shell(
        shell,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=str(root_dir)
    )

    async def read_stream(stream):
        """Reads from stdout/stderr and sends to WebSocket."""
        try:
            while True:
                # Read chunks to support partial output without waiting for newline
                data = await stream.read(1024)
                if not data:
                    break
                # xterm.js expects string data (usually), or binary. 
                # We'll decode to utf-8 for simplicity, handling errors.
                text = data.decode('cp437' if os.name == 'nt' else 'utf-8', errors='replace')
                # Replace Windows newlines if needed, though xterm handles \r\n
                await websocket.send_text(text)
        except Exception as e:
            logger.error(f"Stream read error: {e}")

    # Start reader task
    reader_task = asyncio.create_task(read_stream(process.stdout))

    try:
        while True:
            # Receive input from client (xterm.js sends keystrokes)
            data = await websocket.receive_text()
            
            if process.stdin:
                # Write to process stdin
                # Need to encode. PowerShell expects local codepage usually.
                process.stdin.write(data.encode('cp437' if os.name == 'nt' else 'utf-8'))
                await process.stdin.drain()
                
    except WebSocketDisconnect:
        logger.info("Terminal WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket loop error: {e}")
    finally:
        # Cleanup
        reader_task.cancel()
        if process.returncode is None:
            process.terminate()
            await process.wait()
