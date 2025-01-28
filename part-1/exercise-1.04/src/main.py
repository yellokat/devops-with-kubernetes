import uvicorn, os
from fastapi import FastAPI

# initialize FastAPI app
app = FastAPI()

# enable local network
host = "0.0.0.0"  

# inherit from environment variable
port = int(os.environ["PORT"])

# dummy endpoint 
@app.get("/health-check")
def read_root():
    return {"message": "OK"}

# if this file is the entrypoint, start the server app
if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port)