from fastapi.responses import PlainTextResponse
import uvicorn, os
from fastapi import FastAPI

# initialize FastAPI app
app = FastAPI()

# enable local network
host = "0.0.0.0"  

# inherit from environment variable
port = int(os.environ["PORT"])

# keep track of how many requests were made
app.state.n_requests = 0

# pingpong endpoint 
@app.get("/pingpong", response_class=PlainTextResponse)
def pingpong():
    # increment locally stored value
    app.state.n_requests += 1

    # return accumulated number of requests
    return f"Pong {app.state.n_requests}"

@app.get("/get_pings", response_class=PlainTextResponse)
def get_pings():
    return f"{app.state.n_requests}"

if __name__ == "__main__":
    # run server
    uvicorn.run(app, host=host, port=port)
