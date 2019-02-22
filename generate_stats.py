import pickle
import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr


with open('backtrack_random.pkl', 'rb') as f:
	runtimes = pickle.load(f)

xvals, yvals = zip(*runtimes)
plt.plot(xvals, yvals, 'ro')
plt.show()

corr, pval = pearsonr(xvals, yvals)
print(f'corr= {corr}, pval= {pval}')