import pandas as pd
from utils.tools import Translater
from tqdm import tqdm

tr = Translater('en')

df = pd.read_excel('ru_gold_labels.xlsx').fillna('')

translated = []
for text in tqdm(df.text):
    translated.append(tr.translate(text))

df['text'] = sum(translated, [])

df.to_excel('en_gold_labels.xlsx')
