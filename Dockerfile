FROM python:3.13-slim
WORKDIR /app
COPY --chown=10001:10001 core.py main.py example.json ./
USER 10001:10001
CMD ["python","main.py","demo"]
