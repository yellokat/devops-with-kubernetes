# start from a lightweight python image
# I use python 3.11.2 locally, so for convenience I also choose python version 3.11
FROM python:3.11.11-alpine3.21

# conventional working directory path is /usr/src/app
WORKDIR /usr/src/app

# install python web server packages
RUN pip install fastapi uvicorn requests jinja2

# copy source code
COPY src src

# python prints are buffered by default
# kubernetes doesn't understand this so I disble the buffered print
ENV PYTHONUNBUFFERED=1

# environment variable PORT can be used to choose the port the server runs on
# ENV PORT=7777
# EXPOSE ${PORT}

# start server
CMD ["python", "src/todo_backend.py"]