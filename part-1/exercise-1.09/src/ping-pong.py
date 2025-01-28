import time, uuid, re, uvicorn, os
from fastapi import FastAPI
from datetime import datetime, timezone
from threading import Thread

# initialize FastAPI app
app = FastAPI()

# enable local network
host = "0.0.0.0"  

# inherit from environment variable
port = int(os.environ["PORT"])

# keep track of how many requests were made
app.state.n_requests = 0

# pingpong endpoint 
@app.get("/pingpong")
def read_root():
    # increment locally stored value
    app.state.n_requests += 1
    return {"message": f"Pinged {app.state.n_requests} times."}

if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port)
