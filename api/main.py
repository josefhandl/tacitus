from fastapi import FastAPI
from api.modules.smartctl.router import router as smartctl_router
from api.modules.zpool.router import router as zpool_router


app = FastAPI()


@app.get("/")
async def root() -> dict:
    return {}

app.include_router(smartctl_router())
app.include_router(zpool_router())
