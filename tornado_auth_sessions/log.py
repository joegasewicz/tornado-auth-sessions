import logging
import sys

from config import config

log_level = logging.DEBUG
if not config.DEBUG:
    log_level = logging.INFO

log = logging.getLogger("app")
log.setLevel(log_level)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(
    "[%(asctime)s] %(levelname)s: %(message)s"
))

log.addHandler(handler)
log.propagate = False
