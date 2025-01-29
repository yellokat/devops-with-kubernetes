from fastapi.responses import PlainTextResponse
import time, uuid, re, uvicorn, os, requests
from fastapi import FastAPI
from datetime import datetime, timezone
from threading import Thread

# initialize FastAPI app
app = FastAPI()

# enable local network
host = "0.0.0.0"  

# inherit from environment variable
port = int(os.environ["PORT"])
ping_pong_service_host:str = os.environ["DWK_PING_PONG_SVC_SERVICE_HOST"]
ping_pong_service_port:int = int(os.environ["DWK_PING_PONG_SVC_SERVICE_PORT"])
MESSAGE = os.environ["MESSAGE"]

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

def get_pings() -> str:
    # fetch pings from endpoint
    pings = requests.get(f'http://{ping_pong_service_host}:{ping_pong_service_port}/get_pings')
    return pings.text

# dummy endpoint 
@app.get("/now/writer", response_class=PlainTextResponse)
def read_root():
    with open(os.path.join('config', 'information.txt'), 'r') as f:
        text_from_file = f.readline()
    stringbuilder = ""
    stringbuilder += f"file content: {text_from_file}"
    stringbuilder += f"env variable: MESSAGE={MESSAGE}\n"
    stringbuilder += f"{get_current_timestamp()}.\n"
    stringbuilder += f"Ping / Pongs : {get_pings()}"
    return stringbuilder

# thread job - infinitely write to file every 5 seconds
def log_output_write():
    fname = 'timestamp.txt'
    fdir = os.path.join('/', 'usr', 'src', 'app', 'files')
    fpath = os.path.join(fdir, fname)

    # create file if not exist
    if fname not in os.listdir(fdir):
        with open(fpath, 'w'):
            pass

    # append current timestamp to file every 5 seconds
    while(True):
        with open(fpath, "a") as f:
            f.write(get_current_timestamp() + "\n")
        time.sleep(5)

# thread job - run the server
def run_server(host, port):
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    # initialize two threads, one for logging output and one for running the server
    thread1 = Thread(target=log_output_write)
    thread2 = Thread(target=run_server, args=(host, port))

    # Start both threads
    thread1.start()
    thread2.start()
