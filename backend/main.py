from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import analyze, guide

app = FastAPI(title="Drawing Coach AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ──
app.include_router(analyze.router)
app.include_router(guide.router)

@app.get("/")
def root():
    return {"message": "Drawing Coach AI is running!"}
