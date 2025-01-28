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

def save_pings_to_persistent_volume(pings:int):
    # save n_requests to persistent volume
    fname = 'ping-pong.txt'
    fdir = os.path.join('/', 'usr', 'src', 'app', 'files')
    fpath = os.path.join(fdir, fname)

    # create file if not exist
    if fname not in os.listdir(fdir):
        with open(fpath, 'w'):
            pass

    # write to file
    with open(fpath, "w") as f:
        f.write(f"{pings}")

# pingpong endpoint 
@app.get("/pingpong")
def read_root():
    # increment locally stored value
    app.state.n_requests += 1

    # save pings in volume
    save_pings_to_persistent_volume(app.state.n_requests)
    
    # return accumulated number of requests
    return f"Pong {app.state.n_requests}"

if __name__ == "__main__":
    # initialize number of pings to 0
    save_pings_to_persistent_volume(0)

    # run server
    uvicorn.run(app, host=host, port=port)
