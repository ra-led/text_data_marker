import pandas as pd
import numpy as np
from conf import CFG

tag_ckeckbox = (
    '<div style="background-color:{color}">'
    '<input class="w3-check w3-margin-left" '
    'type="checkbox" name="{tag}" value=1>'
    '<label>{tag}</label>'
    '</div>'
)


class MarkPage:
    def __init__(self):

        elements = [
            tag_ckeckbox.format(tag=tag, color=CFG['colors'][i])
            for i, tag in enumerate(CFG['tags'])
        ]
        if len(elements) % 6 > 0:
            elements += [''] * (6 - len(elements) % 6)
        elements = np.array(elements).reshape(int(len(elements) / 6), 6)

        self.df_tags = pd.DataFrame(elements)

    def tag_table(self):
        return self.any_table(self.df_tags)

    def any_table(self, df):
        return df.to_html(
            header=False,
            index=False,
            classes="w3-table-all w3-centered",
            escape=False
        )
