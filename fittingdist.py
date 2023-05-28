import numpy as np
import pandas as pd
import seaborn as sns
from fitter import Fitter, get_common_distributions, get_distributions


sample = pd.read_csv('Stormlength.csv')

sns.set_style('white')
sns.set_context("paper", font_scale=2)
k = sns.displot(data=sample, x="MGMDT", kind="hist", aspect=1.5)

f = Fitter(sample)
f.fit()
summary = f.summary()
best_fit = f.get_best(method='sumsquare_error')

k=1