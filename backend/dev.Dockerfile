FROM python:3.11

WORKDIR /code

# Install Rust
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . /code

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3001", "--reload"]
