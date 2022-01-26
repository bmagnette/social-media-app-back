import logging
import os

from core.application import create_app

app = create_app()

if __name__ == '__main__':
    if os.environ["env"] != "dev":
        gunicorn_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
    else:
        app.run(host='0.0.0.0', port=5000)
