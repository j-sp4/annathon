FROM --platform=linux/amd64 python:3.9


RUN apt-get update
RUN apt-get install pandoc texlive-xetex poppler-utils -y && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . /code

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
