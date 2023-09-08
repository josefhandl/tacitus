import subprocess
from loguru import logger
from typing import List


def run_cmd(cmd: str, allowed_ret_codes: List[int] = [0]):
    # convert str to List[str]
    cmd_list = list()
    cmd_tmp = cmd.split(" ")
    for word in cmd_tmp:
        if word:
            cmd_list.append(word)

    # invoke command
    try:
        result = subprocess.run(cmd_list, capture_output=True)

        # check return code
        valid = False
        for arc in allowed_ret_codes:
            if arc == result.returncode:
                valid = True

        if not valid:
            logger.error(f'Process "{cmd}" failed with error: {result.stderr.decode()}')
            return None

        return result

    except subprocess.CalledProcessError as ex:
        logger.error(ex)
        return None
    except Exception as ex:
        logger.error(ex)
        return None
