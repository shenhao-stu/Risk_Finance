from openai import OpenAI
from anthropic import Anthropic
from logger import get_logger
import random, time

token = ["1790715889671905303"]

base_url = 'https://aigc.sankuai.com/v1/openai/native'
api_key = random.choice(token)

claude_base_url = "https://aigc.sankuai.com/v1/claude/aws"
claude_api_key = random.choice(token)

max_retry = 5
logger = get_logger(__name__, log_file=f'log/{__name__}.log')

def GPT_request_by_API(engine, msg, gen_param):
    # "Baichuan-Text-Embedding" "text-embedding-3-large"
    assert engine in ["deepseek-chat", "gpt-4-turbo-eva", "gpt-4o-2024-05-13", "glm-4-0520"], "engine not supported"
    client = OpenAI(base_url=base_url, api_key=api_key)

    retry = max_retry
    while retry > 0:
        try:
            response = client.chat.completions.create(
                model = engine,
                messages = [
                    {
                        "role": "user",
                        "content": msg
                    }
                ],
                **gen_param
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"engine: {engine}, error: {e}")
            retry -= 1
            time.sleep(15)
            logger.info(f"Retrying {max_retry - retry} times...")
    
    raise Exception("[Error]: Exceed Max Retry Times")

def Claude_request_by_API(engine, msg, gen_param):
    assert engine in ["anthropic.claude-instant-v1", "anthropic.claude-v2", "anthropic.claude-3-opus", "anthropic.claude-3.5-sonnet"], "engine not supported"
    client = Anthropic(base_url=claude_base_url, auth_token=claude_api_key)

    retry = max_retry
    while retry > 0:
        try:
            response = client.messages.create(
                model=engine,
                messages=[{"role": "user", "content": msg}],
                **gen_param
            )
            return response.content[0].text
        except Exception as e:
                logger.error(f"engine: {engine}, error: {e}")
                retry -= 1
                time.sleep(15)
                logger.info(f"Retrying {max_retry - retry} times...")
    
    raise Exception("[Error]: Exceed Max Retry Times")

def MODEL_request_by_API(engine, msg, gen_param):
    if engine in ["deepseek-chat", "gpt-4-turbo-eva", "gpt-4o-2024-05-13", "glm-4-0520"]:
        return GPT_request_by_API(engine, msg, gen_param).strip()
    elif engine in ["anthropic.claude-instant-v1", "anthropic.claude-v2", "anthropic.claude-3-opus", "anthropic.claude-3.5-sonnet"]:
        return Claude_request_by_API(engine, msg, gen_param).strip()
    else:
        raise NotImplementedError("engine not supported")
    
def main():
    engine = "gpt-4o-2024-05-13" # "anthropic.claude-v2", "gpt-4o-2024-05-13"
    msg = "hello, who are u?"
    gen_param = {"max_tokens": 2000, "temperature": 1, "top_p": 0.8, "stream": False}

    response = MODEL_request_by_API(engine, msg, gen_param)
    print(response)

if __name__ == "__main__":
    main()

