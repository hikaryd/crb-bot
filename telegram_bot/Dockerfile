FROM python:3.12

WORKDIR /app

RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false

COPY ./pyproject.toml ./

RUN poetry install

COPY ./ .

RUN python aioredis-patch.py

CMD ["python", "-m", "bot"]
