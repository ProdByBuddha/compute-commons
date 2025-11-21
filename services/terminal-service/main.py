"""
Terminal Service for Compute Commons Dashboard

Provides WebSocket terminal access for authenticated users.
Runs shell commands in isolated containers with the cc CLI available.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
import pty
import subprocess
import json
from typing import Dict
import jwt
from datetime import datetime

app = FastAPI(title="Compute Commons Terminal Service")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active terminal sessions
sessions: Dict[str, dict] = {}

# JWT verification (Keycloak)
def verify_token(token: str) -> dict:
    """Verify Keycloak JWT token"""
    try:
        # In production, verify with Keycloak public key
        # For now, decode without verification (INSECURE - for demo only)
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


class TerminalSession:
    """PTY-based terminal session"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.master_fd = None
        self.slave_fd = None
        self.process = None
        self.running = False
    
    def start(self):
        """Start a new bash session"""
        # Create pseudoterminal
        self.master_fd, self.slave_fd = pty.openpty()
        
        # Start bash with cc CLI in PATH
        env = os.environ.copy()
        env['PS1'] = '$ '
        env['TERM'] = 'xterm-256color'
        env['PATH'] = f"{env.get('PATH', '')}:/app/cc-cli"  # Add cc CLI to PATH
        
        self.process = subprocess.Popen(
            ['/bin/bash', '--login'],
            stdin=self.slave_fd,
            stdout=self.slave_fd,
            stderr=self.slave_fd,
            env=env,
            preexec_fn=os.setsid
        )
        
        self.running = True
        
        # Print welcome message
        welcome = (
            "\033[1;36m╔════════════════════════════════════════════════════════════╗\033[0m\r\n"
            "\033[1;36m║\033[0m  \033[1;32mCompute Commons Shell\033[0m                               \033[1;36m║\033[0m\r\n"
            "\033[1;36m╚════════════════════════════════════════════════════════════╝\033[0m\r\n"
            "\r\n"
            f"Welcome, \033[1;33m{self.user_id}\033[0m!\r\n"
            "\r\n"
            "\033[1;33mAvailable commands:\033[0m\r\n"
            "  \033[36mcc chat\033[0m              - Conversational AI\r\n"
            "  \033[36mcc run \"cmd\"\033[0m         - Execute on H100\r\n"
            "  \033[36mcc agent deploy\033[0m      - Deploy agents\r\n"
            "  \033[36mcc merit\033[0m             - Merit score\r\n"
            "\r\n"
        )
        os.write(self.master_fd, welcome.encode())
    
    async def read_output(self):
        """Read output from terminal"""
        try:
            output = os.read(self.master_fd, 1024).decode('utf-8', errors='ignore')
            return output
        except Exception:
            return None
    
    def write_input(self, data: str):
        """Write input to terminal"""
        try:
            os.write(self.master_fd, data.encode())
        except Exception as e:
            print(f"Write error: {e}")
    
    def stop(self):
        """Stop terminal session"""
        self.running = False
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
        if self.master_fd:
            os.close(self.master_fd)
        if self.slave_fd:
            os.close(self.slave_fd)


@app.websocket("/ws/terminal")
async def terminal_endpoint(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for terminal access
    
    Query params:
        token: Keycloak JWT token
    """
    await websocket.accept()
    
    try:
        # Verify token
        payload = verify_token(token)
        user_id = payload.get('preferred_username', 'user')
        
        # Create terminal session
        session = TerminalSession(user_id)
        session_id = f"{user_id}_{datetime.now().timestamp()}"
        sessions[session_id] = session
        
        session.start()
        
        # Background task to read from terminal
        async def read_from_terminal():
            while session.running:
                output = await session.read_output()
                if output:
                    await websocket.send_json({
                        "type": "output",
                        "data": output
                    })
                await asyncio.sleep(0.01)
        
        # Start read task
        read_task = asyncio.create_task(read_from_terminal())
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                msg = json.loads(data)
                
                if msg.get('type') == 'command':
                    # Execute command
                    command = msg.get('data', '')
                    session.write_input(command + '\n')
                
                elif msg.get('type') == 'input':
                    # Raw input (for interactive programs)
                    session.write_input(msg.get('data', ''))
                
                elif msg.get('type') == 'resize':
                    # Terminal resize (TODO: implement)
                    pass
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"Error: {e}")
                break
        
        # Cleanup
        read_task.cancel()
        session.stop()
        del sessions[session_id]
        
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "data": str(e)
        })
        await websocket.close()


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_sessions": len(sessions)
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Compute Commons Terminal Service",
        "version": "1.0.0",
        "endpoints": {
            "terminal": "ws://localhost:8001/ws/terminal?token=<jwt>",
            "health": "/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
