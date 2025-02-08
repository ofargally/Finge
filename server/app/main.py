from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth
# from .routers import #file names here

app = FastAPI()
origins = ["0.0.0.0/0"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all relevant routers there like this:
# app.include_router(post.router)
app.include_router(auth.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
