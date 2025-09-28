from fastapi import FastAPI

app = FastAPI(title="Github Issues Homework")

@app.get("/")
def root():
    return {"status": "ok", "docs": "/docs"}
