from fastapi.responses import PlainTextResponse
import time, uuid, re, uvicorn, os
from fastapi import FastAPI
from datetime import datetime, timezone
from threading import Thread
from itertools import islice

# initialize FastAPI app
app = FastAPI()

# enable local network
host = "0.0.0.0"  

# inherit from environment variable
port = int(os.environ["PORT"])

def get_current_timestamp():
    # iso format
    # separator "T" rqeuired
    # express time up to milliseconds
    # use UTC, with "Z" instead of "+00:00"
    current_timestamp = re.sub('\+00:00', 'Z', datetime.now(timezone.utc).isoformat(timespec="milliseconds"))

    # generate a random string using UUID
    random_string = str(uuid.uuid4())

    # return formatted string
    return f"{current_timestamp}: {random_string}"

def get_pings():
    # load pings from persistent volume
    fname = 'ping-pong.txt'
    fdir = os.path.join('/', 'usr', 'src', 'app', 'files')
    fpath = os.path.join(fdir, fname)

    # return 0 if not exist
    if fname not in os.listdir(fdir):
        return 0

    # read pings from file
    with open(fpath, 'r') as f:
        return int(f.read())

# dummy endpoint 
@app.get("/now/reader", response_class=PlainTextResponse)
def read_root():
    return f"{get_current_timestamp()}.\nPing / Pongs : {get_pings()}"

# thread job - watch file output and print
def log_output_read():
    fname = 'timestamp.txt'
    fdir = os.path.join('/', 'usr', 'src', 'app', 'files')
    fpath = os.path.join(fdir, fname)

    # create file if not exist
    if fname not in os.listdir(fdir):
        with open(fpath, 'w'):
            pass

    last_read_line = 0
    while True:
        with open(fpath, 'r') as f:
            # read only newly appended lines, up to 100 new lines at a time
            for line in islice(f, last_read_line, last_read_line + 100):
                print(line.strip())
                last_read_line += 1
        time.sleep(0.5)

# thread job - run the server
def run_server(host, port):
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    # initialize two threads, one for logging output and one for running the server
    thread1 = Thread(target=log_output_read)
    thread2 = Thread(target=run_server, args=(host, port))

    # Start both threads
    thread1.start()
    thread2.start()
