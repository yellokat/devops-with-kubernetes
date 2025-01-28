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

# dummy endpoint 
@app.get("/now")
def read_root():
    return {"message": get_current_timestamp()}

# thread job - infinitely log output every 5 seconds
def log_output():
    while(True):
        # print current timestampt every 5 seconds
        print(get_current_timestamp())
        time.sleep(5)

# thread job - run the server
def run_server(host, port):
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    # initialize two threads, one for logging output and one for running the server
    thread1 = Thread(target=log_output)
    thread2 = Thread(target=run_server, args=(host, port))

    # Start both threads
    thread1.start()
    thread2.start()
