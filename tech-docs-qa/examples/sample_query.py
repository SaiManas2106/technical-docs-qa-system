import requests, os, json
from dotenv import load_dotenv
load_dotenv()
API = os.environ.get('QA_API','http://localhost:8000/query')
def ask(q):
    r = requests.post(API, json={'question': q})
    print(r.json())
if __name__ == '__main__':
    ask('What are the outputs and max current for the PSU-1200?')