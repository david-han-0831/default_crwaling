import logging

class Log() :

  def __init__(self, name) :
    self.logger = logging.getLogger("{0}.{1}".format(self.__class__.__qualname__, name))
    self.logger.setLevel(logging.DEBUG)
    self.handler = logging.StreamHandler()
    self.formatter = logging.Formatter(
      fmt = "\033[93m%(asctime)s \033[94m%(name)s \033[96m%(filename)s \033[33m%(funcName)s \033[32m%(lineno)s \033[95m %(levelname)s \033[36m %(message)s \033[0m",
      datefmt = '%Y-%m-%d %I:%M:%S'
    )
    self.handler.setFormatter(self.formatter)
    self.logger.addHandler(self.handler)
    
