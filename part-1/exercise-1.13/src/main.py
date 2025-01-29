from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn, os, requests, datetime
from fastapi import FastAPI, Request

# initialize FastAPI app
app = FastAPI()

host = "0.0.0.0"  
port = int(os.environ["PORT"])

def init_app():
    # create directory if not exist
    app.state.volume_dir = os.path.join('/', 'usr', 'src', 'app', 'files')
    if "assets" not in os.listdir(app.state.volume_dir):
        os.mkdir(os.path.join(app.state.volume_dir, 'assets'))

    app.state.assets_dir = os.path.join(app.state.volume_dir, 'assets')
    app.state.image_path = os.path.join(app.state.assets_dir, 'image.jpg')
    app.state.last_updated_path = os.path.join(app.state.assets_dir, 'last_updated.txt')

    # mount static files
    # /usr/src/app/files/assets -> /assets
    app.mount("/assets", StaticFiles(directory=app.state.assets_dir), name="assets")

init_app()
templates = Jinja2Templates(directory="src/templates")

# dummy endpoint 
@app.get("/health-check")
def read_root():
    return {"message": "OK"}

def download_image_and_leave_logs():
    # make request
    response = requests.get('https://picsum.photos/1000')

    # save image
    with open(app.state.image_path, 'wb') as file:
        file.write(response.content)
    
    # save refresh time
    with open(app.state.last_updated_path, 'w') as file:
        file.write(datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))

# html page endpoint
@app.get("/home", response_class=HTMLResponse)
def read_root(request: Request):
    # download random image if not exist
    if "image.jpg" not in os.listdir(app.state.assets_dir):
        download_image_and_leave_logs()
    
    # check refresh time, if > 60 minutes, fetch again
    now = datetime.datetime.now()
    with open(app.state.last_updated_path, 'r') as file:
        last_updated = datetime.datetime.strptime(file.read(), '%Y-%m-%d_%H:%M:%S')
    # if (now - last_updated).seconds > 60*60:
    if (now - last_updated).seconds > 10:
        print('INFO:\tImage has expired. Downloading new images...')
        download_image_and_leave_logs()

    return templates.TemplateResponse("home.html", {"request":request, "image_path": "/assets/image.jpg"})

# if this file is the entrypoint, start the server app
if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port)