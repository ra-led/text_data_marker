import re
from itertools import product
import numpy as np
import pandas as pd
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import make_scorer, matthews_corrcoef
import sentencepiece as spm
from tqdm import tqdm
from conf import CFG


class Learner:
    def __init__(self, lang, db):
        self.lang = lang
        self.db = db

        self.pipeline = Pipeline([
            ('vect', CountVectorizer()),
            ('tfidf', TfidfTransformer()),
            ('clf', SGDClassifier(n_jobs=1, penalty='elasticnet')),
        ])

        parameters = {
            'vect__max_features': [10000, 32000],
            'vect__max_df': [1.0],
            'vect__ngram_range': [(1, 1), (1, 2)],
            'tfidf__norm': ['l2'],
            'clf__alpha': [0.001, 0.1, 1],
            'clf__l1_ratio': [.001, 0.1, 1],
            'clf__loss': ['log'],
        }

        skf = StratifiedKFold(n_splits=5, random_state=123, shuffle=True)

        self.grid_search = GridSearchCV(
            self.pipeline,
            parameters,
            refit=True,
            scoring=make_scorer(matthews_corrcoef),
            cv=skf,
            n_jobs=-1,
            verbose=1
            )

        self.spp = spm.SentencePieceProcessor()
        self.spp.Load('utils/models/{}_spm_unigram_32000.model'.format(self.lang))

        self.cleaner = {
            'en': self.clean_en
        }

    def clean_en(self, text):
        text = text.lower()
        text = re.sub("[^A-Za-z]", " ", text)
        return ' '.join(text.split())

    def train_baseline(self):
        df = pd.read_excel('{}_gold_labels.xlsx'.format(self.lang))
        claen_reviews = df.text.apply(self.cleaner[self.lang])
        sp_reviews = claen_reviews.apply(
            lambda x: ' '.join(self.spp.encode_as_pieces(x))
        )
        results = []
        for i, label in tqdm(enumerate(CFG['tags'])):
            self.grid_search.fit(
                sp_reviews.values,
                df[label].values
            )
            joblib.dump(
                self.grid_search.best_estimator_,
                'utils/models/en_tag{}_model.joblib'.format(i)
            )
            result = {
                'tag': label,
                'cnt': 0,
                'score': self.grid_search.best_score_
            }
            results.append(result)
        self.db.write_rows(results, '{}_results'.format(self.lang))

    def get_progress(self):
        return self.db.query('SELECT * FROM {}_results'.format(self.lang))

    def unlabeled_tag_proba(self):
        df = self.db.query('SELECT * FROM {}_reviews'.format(self.lang))
        reviews = df['title'] + df['content']
        claen_reviews = reviews.apply(self.cleaner[self.lang])
        sp_reviews = claen_reviews.apply(
            lambda x: ' '.join(self.spp.encode_as_pieces(x))
        )
        y_proba = np.zeros((df.shape[0], len(CFG['tags'])))
        for i, label in tqdm(enumerate(CFG['tags'])):
            model = joblib.load(
                'utils/models/en_tag{}_model.joblib'.format(i)
            )
            proba = model.predict_proba(sp_reviews.values)
            y_proba[:, i] = proba[:, 1]
        df_preds = pd.DataFrame(y_proba, columns=CFG['tags'])
        df_preds['id'] = df['id'].values
        df_preds.to_csv(
            '{}_probs.csv'.format(self.lang),
            index=False,
            sep='\t'
        )

    def load_probs(self):
        self.probs = pd.read_csv(
            '{}_probs.csv'.format(self.lang),
            sep='\t'
        ).set_index('id')

    def store_probs(self):
        self.probs.reset_index().to_csv(
            '{}_probs.csv'.format(self.lang),
            index=False,
            sep='\t'
        )

    def sample_border(self, tag, min_p=0.4, max_p=0.6):
        sample = (
            self
            .probs[
                (self.probs[tag] > min_p) & (self.probs[tag] < max_p)
            ]
            .reset_index(drop=False)
            .sample()
            .iloc[0]
        ).to_dict()
        self.probs.drop([sample['id']], axis=0, inplace=True)
        return sample

    def sample_radical(self, tag, thresh=0.9, pos=True):
        sample = (
            self
            .probs[
                (self.probs[tag] >= thresh) == pos
            ]
            .reset_index(drop=False)
            .sample()
            .iloc[0]
        ).to_dict()
        self.probs.drop([sample['id']], axis=0, inplace=True)
        return sample

    def sample_top(self, tag):
        sample = (
            self
            .probs[
                (self.probs[tag] == self.probs[tag].max())
            ]
            .reset_index(drop=False)
            .sample()
            .iloc[0]
        ).to_dict()
        self.probs.drop([sample['id']], axis=0, inplace=True)
        return sample
