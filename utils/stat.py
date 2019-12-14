import matplotlib.pyplot as plt
import seaborn as sns

from conf import CFG
from utils.tools import Database
from utils.ml import Learner

db = Database()
ml = Learner('en', db)
ml.load_probs()

reviews = db.query('select * from en_marked')
results = ml.get_progress()

for label in CFG['tags']:
    plt.title(
        ' '.join(
            [label,
            str(results.loc[results['tag'] == label, 'score'].iloc[-1])]
        )
    )
    plt.hist(ml.probs[label], bins=100)
    plt.show()
