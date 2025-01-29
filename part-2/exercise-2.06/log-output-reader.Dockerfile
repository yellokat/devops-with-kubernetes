# start from a lightweight python image
# I use python 3.11.2 locally, so for convenience I also choose python version 3.11
FROM python:3.11.11-alpine3.21

# conventional working directory path is /usr/src/app
WORKDIR /usr/src/app

# install python web server packages
RUN pip install fastapi uvicorn requests

# copy source code
COPY src src

# python prints are buffered by default
# kubernetes doesn't understand this so I disble the buffered print
ENV PYTHONUNBUFFERED=1

# run main.py
CMD ["python", "src/log-output-reader.py"]