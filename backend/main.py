from fastapi import FastAPI

app = FastAPI()

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/hello/{name}")
def hello(name: str):
    return {"message" : f"Hello, {name}!"}