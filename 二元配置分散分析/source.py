import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols

data = {
    'value':[14.5,15.1,14.1,16.2,15.3,17.5,16.5,16.1,15,18.6,16.9,18.6,17.8,19,15.2,21.7,20.5,19.4,18.1,20.2,17.2,23.6,24.9,25.5],
    'type':["要因A","要因A","要因A","要因B","要因B","要因B","要因A","要因A","要因A","要因B","要因B","要因B","要因A","要因A","要因A","要因B","要因B","要因B","要因A","要因A","要因A","要因B","要因B","要因B"],
    'amount':['100g','100g','100g','100g','100g','100g','200g','200g','200g','200g','200g','200g','300g','300g','300g','300g','300g','300g','400g','400g','400g','400g','400g','400g']
}

model = ols('value ~ type + amount + type:amount', data).fit()

aov_table = sm.stats.anova_lm(model)
print(aov_table)