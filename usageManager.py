import random
import time
import json
import os

# 随机生成文件名
def random_filename():
    return filename

# 增加时间戳
def random_filename_with_timestamp():
    filename = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    return f"{filename}_{timestamp}"

def commit_usage(username, model, prompt, completion):
    file_with_timestamp = random_filename_with_timestamp()
    # print(file_with_timestamp)

    usage_dir = 'usage'
    if not os.path.exists(usage_dir):
        os.makedirs(usage_dir)

    with open(os.path.join(usage_dir, file_with_timestamp), "w") as f:
        json.dump({
            "username": username,
            "model": model,
            "prompt": prompt,
            "completion": completion
        }, f)

def summarize_usage():
    # 指定文件夹路径
    usage_dir = 'usage/'
    if not os.path.exists(usage_dir):
        os.makedirs(usage_dir)

    try:
        with open("usage.json", "r") as f:
            usage = json.load(f)
    except FileNotFoundError:
        usage = {}

    while True:
        # 遍历文件夹下的文件
        file_paths = [os.path.join(root, file) for root, dirs, files in os.walk(usage_dir) for file in files]
        for file_path in file_paths:
            with open(file_path, 'r') as f:
                usage_message = json.load(f)

            username = usage_message["username"]
            current_model = usage_message["model"]
            prompt_len = usage_message["prompt"]
            completion_len = usage_message["completion"]

            if username not in usage:
                usage[username] = {}

            if current_model not in usage[username]:
                usage[username][current_model] = {
                    "prompt": prompt_len,
                    "completion": completion_len,
                }
            else:
                usage[username][current_model]["prompt"] += prompt_len
                usage[username][current_model]["completion"] += completion_len
            with open("usage.json", "w") as f:
                json.dump(usage, f, indent=2)
            os.remove(file_path)
            print(file_path)
        time.sleep(5)

if __name__ == '__main__':
    summarize_usage()
