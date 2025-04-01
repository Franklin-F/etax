import requests
from lib.logger import logger


class Curl:
    host = None
    port = None
    protocol = 'http'
    auth = None

    def __init__(self, host=None, port=None, protocol=None, auth=None):
        self.host = host or self.host
        self.port = port or self.port
        self.protocol = protocol or self.protocol
        self.auth = auth or self.auth

    def get_url(self, action):
        if self.port:
            return f'{self.protocol}://{self.host}:{self.port}{action}'
        return f'{self.protocol}://{self.host}{action}'

    def get(self, action='/', params=None):
        url = self.get_url(action)
        logger.debug(f'Get {url}')
        return requests.get(url=url, auth=self.auth, params=params)

    def post(self, action='/', params=None, data=None, json=None, headers=None):
        url = self.get_url(action)
        logger.debug(f'Post {url}')
        final_headers = headers or {}
        return requests.post(url=url, auth=self.auth, params=params, data=data, json=json, headers=final_headers)

    def delete(self, action='/', params=None):
        url = self.get_url(action)
        logger.debug(f'Delete {url}')
        return requests.delete(url=url, auth=self.auth, params=params)

    def put(self, action='/', params=None):
        url = self.get_url(action)
        logger.debug(f'Put {url}')
        return requests.put(url=url, auth=self.auth, params=params)

    def patch(self, action='/', params=None):
        url = self.get_url(action)
        logger.debug(f'Patch {url}')
        return requests.patch(url=url, auth=self.auth, params=params)

    def head(self, action='/', params=None):
        url = self.get_url(action)
        logger.debug(f'Head {url}')
        return requests.head(url=url, auth=self.auth, params=params)

    def options(self, action='/', params=None):
        url = self.get_url(action)
        logger.debug(f'Options {url}')
        return requests.options(url=url, auth=self.auth, params=params)


class Inner(Curl):
    pass


if __name__ == '__main__':
    pass
