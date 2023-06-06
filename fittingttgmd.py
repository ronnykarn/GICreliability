import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from fitter import Fitter, get_common_distributions, get_distributions

TTGMD = pd.read_csv('TTGMD.csv')

sns.histplot(data=TTGMD, x="TTGMD", kde=True)
plt.xlabel('TTGMD(hours)')
plt.savefig('plots\\TTGMD.png', dpi=300)

TTGMDFit = Fitter(TTGMD['TTGMD'])
TTGMDFit.fit()
TTGMDSummary = TTGMDFit.summary(plot=True)
plt.savefig('plots\\TTGMD_fitted.png', dpi=300)
TTGMDSummary .to_csv('TTGMD_fitted.csv')
x = 1

