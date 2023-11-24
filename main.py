from login import login
from run import main
import asyncio

if __name__ == '__main__':
    username = login()
    if not username:
        exit()
    else:
        asyncio.run(main(username))
