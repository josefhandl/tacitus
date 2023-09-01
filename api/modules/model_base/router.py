from fastapi.routing import APIRouter

class BaseRouter:
    PREFIX = "/"

    def __init__(self):
        self.router = APIRouter(prefix=self.PREFIX)
        self.__add_routes__()

    def __call__(self) -> APIRouter:
        return self.router

    def __add_routes__(self):
        for parameter_name in dir(self):
            if parameter_name.startswith("__"):
                continue
            if parameter_name.startswith("get_"):
                parameter = getattr(self, parameter_name)
                if not callable(parameter):
                    continue
                route = parameter_name.replace("get_", "")
                if route == "root":
                    route = ""
                self.router.get(
                    f"/{route}",
                    response_model=parameter.__annotations__["return"]
                )(parameter)
