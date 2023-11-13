__all__ = ['config']

class Config:
    api_key = ""
    # proxies = {}

    def __getattr__(self, name):
        return None

config = Config()
