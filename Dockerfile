FROM python:3.13-slim

WORKDIR /app
COPY app ./app
COPY pyproject.toml README.md ./

EXPOSE 6380
CMD ["python", "-m", "app.server"]
