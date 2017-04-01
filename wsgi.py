from server import app as application
from logging.handlers import RotatingFileHandler
from logging import Formatter
import config

if __name__ == "__main__":
    handler = RotatingFileHandler(config.log_dir + 'ui.log', maxBytes=10000, backupCount=1)
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    handler.setFormatter(Formatter(log_format))
    handler.setLevel(config.logging_level)
    app.logger.addHandler(handler)
    application.run()
