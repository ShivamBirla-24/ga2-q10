from fastapi import FastAPI, Request, Response, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid
from collections import defaultdict

app = FastAPI()

# 1. CORS Middleware: Strict policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app-f1panr.example.com", "https://exam.iitm.ac.in"], # Add exam domain
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Rate Limiting Storage
client_buckets = defaultdict(list)
B = 13  # Max requests
WINDOW = 10 # seconds

@app.middleware("http")
async def middleware_stack(request: Request, call_next):
    # A. RATE LIMITER
    client_id = request.headers.get("X-Client-Id", "anonymous")
    now = time.time()
    
    # Filter out old requests outside our 10s window
    client_buckets[client_id] = [t for t in client_buckets[client_id] if now - t < WINDOW]
    
    if len(client_buckets[client_id]) >= B:
        return Response("Too Many Requests", status_code=429)
    
    client_buckets[client_id].append(now)
    
    # B. REQUEST CONTEXT
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    
    # Process the request
    response = await call_next(request)
    
    # Set the header and return
    response.headers["X-Request-ID"] = req_id
    request.state.req_id = req_id
    return response

@app.get("/ping")
def ping(request: Request):
    return {
        "email": "25ds3000046@ds.study.iitm.ac.in",
        "request_id": request.state.req_id
    }
