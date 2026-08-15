from fastapi import FastAPI

app = FastAPI(title="AI Essay Detector")


@app.get("/")
def read_root():
    return {"status": "ok", "service": "AI Essay Detector"}
