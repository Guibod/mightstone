class ServiceError(Exception):
    def __init__(self, message, url=None, status=None):
        self.message = message
        self.url = url
        self.status = status

    def __str__(self):
        return "{message} (HTTP:{status} {url})".format(**self.__dict__)
