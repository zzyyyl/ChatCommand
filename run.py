import asyncio
import threading
import openai
import tiktoken
from openai import AsyncOpenAI
import logging
import os

cur_dir = os.path.dirname(__file__)
logging.basicConfig(filename='chat.log', format='[%(asctime)s][%(levelname)s][%(name)s] %(message)s', encoding='utf-8', level=logging.DEBUG)

messages_template = [
    {
        "role": "system",
        "content": "不要在对话中强调自己的身份, 回答尽量准确。"
    },
]
messages_chat_template = [
    {
        "role": "system",
        "content": "不要在对话中强调自己的身份, 回答尽量准确, 不要超过50个字, 越短越好。"
    },
]

class PrintWaitingDots:
    def __init__(self):
        self.is_waiting = True
    async def run(self):
        while True:
            loop_len = 6
            # for i in range(loop_len):
            #     print("waiting", ("." * (i + 1)) + (" " * (loop_len - i - 1)), end="\r")
            for i in range(loop_len):
                print("waiting", (" " * min(i, loop_len - i)) + '.' + (" " * (loop_len - min(i, loop_len - i))), end="\r")
                await asyncio.sleep(0.1)
                if not self.is_waiting:
                    print(" " * (8 + loop_len), end="\r")
                    return

def num_tokens_from_message(message, model="gpt-3.5-turbo-0613", encoding=None):
    if encoding is None:
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(message))

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model or "gpt-4" in model:
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError()
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

from config import config

async def main():
    if config.proxies:
        openai.proxies = config.proxies
    if config.api_key is None:
        print("Please set your OpenAI API key in config.py.")
        return
    client = AsyncOpenAI(
        api_key=config.api_key,
    )
    messages = []
    model = "gpt-3.5-turbo-1106"
    while True:
        try:
            input_txt = input(f"User({len(messages)}): ").strip()
        except:
            print("Exit.")
            break
        if input_txt == "/multiline":
            input_txt = ""
            while True:
                input_line = input("....: ")
                if input_line != "/end":
                    input_txt += input_line + '\n'
                else:
                    break
            input_txt = input_txt.strip()
        if input_txt == "/bye" or input_txt == "/exit":
            print("Exit.")
            break
        if input_txt == "/clear":
            print("Reset done.")
            messages = []
            continue
        if input_txt == "/cls":
            os.system("cls")
            continue
        if input_txt == "/simple":
            print("Reset done and switch to simple mode.")
            messages = messages_template.copy()
            continue
        if input_txt == "/chat":
            print("Reset done and switch to chat mode.")
            messages = messages_chat_template.copy()
            continue
        if input_txt == "/gpt4" or input_txt == "/gpt-4-1106-preview":
            print("Set model to gpt-4-1106-preview.")
            model = "gpt-4-1106-preview"
            continue
        if input_txt == "/gpt3" or input_txt == "/gpt-3.5-turbo-1106":
            print("Set model to gpt-3.5-turbo-1106.")
            model = "gpt-3.5-turbo-1106"
            continue
        if input_txt == "/model":
            print("model:", model)
            continue

        if input_txt == "/rerun":
            if messages[-1]["role"] == "assistant" and \
               messages[-2]["role"] == "user":
                messages = messages[:-1]
            else:
                print("Cannot rerun!")
                continue
        elif input_txt.startswith('/'):
            print("Unknown option.")
            continue
        elif input_txt == "":
            continue
        else:
            messages.append({
                "role": "user",
                "content": input_txt
            })

        print_waiting_obj = PrintWaitingDots()
        print_waiting_thread = threading.Thread(target=asyncio.run, args=(print_waiting_obj.run(),))
        print_waiting_thread.start()

        stream_res = await client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            max_tokens=1024,
            # temperature=1.2
        )

        print_waiting_obj.is_waiting = False
        print_waiting_thread.join()

        received_first = False
        current_message = ""
        current_model = None
        async for part in stream_res:
            if not received_first:
                received_first = True
                print(f"{part.model}({len(messages)}): ", end="")
                current_model = part.model
            print(part.choices[0].delta.content or "", end="")
            current_message += part.choices[0].delta.content or ""
            logging.debug(f"Stream response part: {part}")

        print()

        # enc = tiktoken.encoding_for_model(current_model)
        prompt_len = num_tokens_from_messages(messages, model=current_model)
        completion_len = num_tokens_from_message(current_message, model=current_model)
        print(f"Calculated usage: prompt {prompt_len}, completion {completion_len}.")
        messages.append({ "role": "assistant", "content": current_message })
        logging.info(f"Current messages: {messages}")


if __name__ == '__main__':
    asyncio.run(main())
