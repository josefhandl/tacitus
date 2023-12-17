from fastapi import FastAPI
from importlib import import_module
from pathlib import Path


def get_modules():
    modules_path = Path(__file__).parent / "modules"
    for module in modules_path.iterdir():
        if module.is_dir() and module.name[0] != '_':
            yield module

def include_modules_by_paths(module_paths: list, app):
    for module_path in module_paths:
        module_name = f"api.modules.{module_path.name}.router"
        module = import_module(module_name)
        app.include_router(module.router())


if __name__ == "api.main":
    app = FastAPI()
    @app.get("/")
    async def root() -> dict:
        return {
            "app": "tacitus-api",
            "version": "0.1.1"
        }

    include_modules_by_paths(get_modules(), app)
