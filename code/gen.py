import pandas as pd
from secret import MODEL_request_by_API
from logger import get_logger
import json
import os
import random

# TODO: 舆情文本可能包含多个类别
engine = 'gpt-4o-2024-05-13'

logger = get_logger(__name__, log_file=f'log/gen.log')

gen_param = {"max_tokens": 2000, "temperature": 2, "top_p": 0.8, "stream": False}

data_dir = 'datasets/refined'
file_path = 'datasets/label_system.xlsx'
prompt_path = 'prompt/prompt.txt'
prompt_format_path = 'prompt/prompt_format.txt'
res_path = f'datasets/gen/gen_illegal_{engine}.jsonl'
stats_path = 'stats/stats.txt'

def read_files_from_directory(directory):
    """读取目录下所有文件的内容并分类"""
    files_content = {
        'adv': [],
        'app': [],
        'intro': [],
        'op': [],
        'per_op': []
    }
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                if filename.startswith('adv'):
                    files_content['adv'].append(content)
                elif filename.startswith('app'):
                    files_content['app'].append(content)
                elif filename.startswith('intro'):
                    files_content['intro'].append(content)
                elif filename.startswith('op'):
                    files_content['op'].append(content)
                elif filename.startswith('per_op'):
                    files_content['per_op'].append(content)
    
    return files_content

def random_sample_from_list(data_list, n):
    """从列表中随机抽取n个元素"""
    return random.sample(data_list, min(n, len(data_list)))

def load_prompt_template(prompt_path):
    with open(prompt_path, 'r', encoding='utf-8') as file:
        prompt_template = file.read()
    return prompt_template

# get n_shot data
n_shot = 1
files_content = read_files_from_directory(data_dir)
adv = '\n'.join(random_sample_from_list(files_content['adv'], n_shot))
app_intro = '\n'.join(random_sample_from_list(files_content['app'], n_shot))
intro = '\n'.join(random_sample_from_list(files_content['intro'], n_shot))
neg_op = '\n'.join(random_sample_from_list(files_content['op'], n_shot))
usr_rec = '\n'.join(random_sample_from_list(files_content['per_op'], n_shot))


df = pd.read_excel(file_path)
with open(stats_path, 'w', encoding='utf-8') as file:
    stats = df['类型'].value_counts()
    risk_format_empty_count = df['风险详请描述格式'].isnull().sum()
    file.write(stats.to_string(index=True) + "\n")
    file.write(f"风险详请描述格式为空的数量: {risk_format_empty_count}\n")

df = df.fillna('')
keys = ['编号', '类型', '风险点', '风险详请描述格式']
with open(res_path, 'w', encoding='utf-8') as file:
    for index, row in df.iterrows():
        index = row['编号'].strip()
        risk_type = row['类型'].strip()
        risk = row['风险点'].strip()
        risk_format = row['风险详请描述格式'].strip()

        if risk_format:
            prompt = load_prompt_template(prompt_path)
            prompt = prompt.format(risk_type=risk_type, risk=risk, risk_format=risk_format, adv=adv, app_intro=app_intro, intro=intro, neg_op=neg_op, usr_rec=usr_rec)
            response = MODEL_request_by_API(engine, prompt, gen_param)
            logger.info("====================================")
            logger.info(response)
            response = response.split('## Output:')[1].strip()
            risk_text = response.split('[舆情文本]:')[1].split('[风险详请描述]:')[0].strip()
            risk_analysis = response.split('[风险详请描述]:')[1].strip()
            
            res = {'id': index, 'risk_type': risk_type, 'risk': risk, 'risk_format': risk_format, 'risk_text': risk_text, 'risk_analysis': risk_analysis}
        else:
            prompt = load_prompt_template(prompt_format_path)
            prompt = prompt.format(risk_type=risk_type, risk=risk, adv=adv, app_intro=app_intro, intro=intro, neg_op=neg_op, usr_rec=usr_rec)
            response = MODEL_request_by_API(engine, prompt, gen_param)

            risk_text = response.split('[舆情文本]:')[1].split('[风险详请描述格式]:')[0].strip()
            risk_format = response.split('[风险详请描述格式]:')[1].split('[风险详请描述]:')[0].strip()
            risk_analysis = response.split('[风险详请描述]:')[1].strip()

            res = {'id': index, 'risk_type': risk_type, 'risk': risk, 'risk_format': risk_format, 'risk_text': risk_text, 'risk_analysis': risk_analysis}
        
        file.write(json.dumps(res, ensure_ascii=False) + "\n")
        logger.info(f"response: {response}\nrisk_text: {risk_text}\nrisk_analysis: {risk_analysis}\nrisk_format: {risk_format}\n")

    


    

