import logging, os

_logger = None

def getLogger():
    global _logger
    if not _logger:
        appPath = os.path.dirname(os.path.abspath(__file__))
        _logger = logging.getLogger(__name__)
        _logger.setLevel(logging.INFO)
        for handler in _logger.handlers:
            handler.close
            _logger.removeHandler(handler)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s][%(filename)s.%(funcName)s]: %(message)s')
        logHandler = logging.FileHandler(os.path.join(appPath, 'logTest.log'), mode='a')
        logHandler.setFormatter(formatter)
        logHandler.encoding = 'utf-8'
        logHandler.flush()
        _logger.addHandler(logHandler)

    return _logger

def delLogger():
    global _logger;
    if _logger:
        for handler in _logger.handlers:
            handler.close
            _logger.removeHandler(handler)
