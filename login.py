import getpass
from config import config

accounts = config.accounts

def login():
    # 获取用户输入的账号和密码
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")

    # 检查账号密码是否匹配
    if username in accounts and accounts[username] == password:
        print("Login successful!")
        return username
    else:
        print("Invalid username or password")
        return None

if __name__ == '__main__':
    login()
    input("调试中...")