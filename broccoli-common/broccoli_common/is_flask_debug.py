import os


def is_flask_debug(flask_app) -> bool:
    # detect flask debug mode
    # https://stackoverflow.com/questions/14874782/apscheduler-in-flask-executes-twice
    res = not (not flask_app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true')
    print(f"is_flask_debug={res}")
    return res
