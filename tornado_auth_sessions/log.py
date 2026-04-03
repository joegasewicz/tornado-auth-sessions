import logging
import sys

log_level = logging.DEBUG

log = logging.getLogger("app")
log.setLevel(log_level)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(
    "[%(asctime)s] %(levelname)s: %(message)s"
))

log.addHandler(handler)
log.propagate = False
