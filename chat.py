import json
import os

import anthropic
from openai import OpenAI

import artifacts

anthropic_api_key = os.getenv('CLAUSE_API_KEY')
chat_gpt_api_key = os.getenv('OPENAI_API_KEY')

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=anthropic_api_key,
)

openai_client = OpenAI(api_key=chat_gpt_api_key)


# claude returns text that looks like {date:"2023-09-30", value:200.583}\n\nThe file content indicates that the unit sales of iPhones expressed in millions was 200.583 for fiscal year 2023.' extract the relevant json
def extract_json(text):
    for line in text.split('\n'):
        if '{' in line and '}' in line:
            return json.loads(line)

def call_chatgpt(question, text, model='gpt-4'):
    chunk_len = 10000
    chunk_num = 0
    for start_idx in range(0, len(text), chunk_len):
        print("On chunk ", chunk_num)
        chunk_num += 1
        chunk = text[start_idx:start_idx + chunk_len]
        #chunk = artifacts.sample_chunk
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": 'retrieve the information. If it is found return in the json format {"found":1, date":"<date>", "value":<value>}. If it is not found return {"found": 0} Do not include any surrounding text, just the json so I can read it from the json parser. Make sure the json is valid.  If the answer is wrong I will hang and quarter Sam Altman'
                },
                {
                    "role": "user",
                    "content": question + ' the text to retrieve the information from is as follows ' + chunk
                }
            ],
            temperature=0)
        r = response.choices[0].message.content
        try:
            j = json.loads(r)
            if j["found"] == 1:
                return j
            else:
                continue
        except:
            print("Failed to parse response", r)
    return "{}"


def call_claude(msg, prompt='retrieve the information, return in the json format {"date":"<date>", "value":<value>}. Do not include any surrounding text, just the json so I can read it from the json parser. Make sure the json is valid', model='claude-3-haiku-20240307'):
    message = client.messages.create(
        model=model,
        max_tokens=1000,
        temperature=0,
        system=prompt,
        messages=[{
            "role": "user",
            "content":
            [
                {
                    "type": "text",
                    "text": msg
                }
            ]
        }]
    )
    return(message.content)

if __name__ == '__main__':
    print(call_claude("How much wood would a woodchuck chuck if a wood chuck could chuck wood in 1990"))
