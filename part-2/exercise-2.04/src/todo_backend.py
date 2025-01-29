from fastapi.responses import JSONResponse
import uvicorn, os
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request

# initialize FastAPI app
app = FastAPI()
host = "0.0.0.0"  
port = int(os.environ["PORT"])

# Enable CORS (Allow all origins, methods, and headers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# manage todos in memory before moving on to databases
app.state.todos = []

@app.post("/todos")
async def create_todo(request: Request):
    # parse body & save todo
    body = await request.json()
    app.state.todos.append(body["todo"])
    return {"message": "OK"}

@app.get("/todos")
def get_todos():
    return JSONResponse(jsonable_encoder(app.state.todos))

# if this file is the entrypoint, start the server app
if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port)