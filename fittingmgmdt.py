import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from fitter import Fitter, get_common_distributions, get_distributions

# Read storm data
stormData = pd.read_csv('stormlengths.csv')

sns.histplot(data=stormData, x="MGMDT", binwidth=3, kde=True)
plt.xlabel('MGMDT(hours)')
plt.savefig('plots\\MGMDT.png', dpi=300)

MGMDTFit = Fitter(stormData['MGMDT'])
MGMDTFit.fit()
MGMDTFit.summary(plot=True)
MGMDTFitSummary = MGMDTFit.summary(plot=True)
plt.savefig('plots\\MGMDT_fitted.png', dpi=300)
MGMDTFitSummary.to_csv('MGMDT_fitted.csv')
k = 1
