from ..model_base.router import BaseRouter
from ...utilities.terminal import run_cmd


# TODO: Auth and better response!
class Power(BaseRouter):
    PREFIX = "/power"

    async def post_reboot(self) -> dict:
        """
        Reboots system.
        """
        run_cmd("reboot")
        return {"status": "ok"}

    async def post_shutdown(self) -> dict:
        """
        Shutsdown system.
        """
        run_cmd("shutdown -P now")
        return {"status": "ok"}


router = Power()
