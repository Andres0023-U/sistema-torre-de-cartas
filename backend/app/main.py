from fastapi import FastAPI

app = FastAPI(title="Torre de Cartas API")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Torre de Cartas API funcionando"}