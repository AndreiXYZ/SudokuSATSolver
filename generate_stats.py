import pickle
import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr
import numpy as np

def removeOutliers(runtimes):
	xvals, yvals = zip(*runtimes)
	dataMean = np.mean(yvals)
	dataStd = np.std(yvals)
	filtered = [(x,y) for x,y in runtimes if (dataMean - 2*dataStd < y < dataMean + 2*dataStd)]
	print(f'Removed {len(xvals)-len(filtered)} outliers')
	return filtered


def getStats(filename):
	with open(filename, 'rb') as f:
		measurements = pickle.load(f)

	#Remove outliers for plotting only
	xvals, yvals = zip(*removeOutliers(measurements))
	plt.xticks(range(21,32))
	plt.yticks(range(0,int(max(xvals))))
	plt.grid()
	plt.title(heuristic + ' ' + metric)
	plt.xlabel('Num. givens')
	plt.ylabel(metric)
	plt.plot(xvals, yvals, 'bo')
	plt.show()

	#Run Pearson on data without outliers
	corr, pval = pearsonr(xvals, yvals)
	print(f'No outliers: corr= {corr}, pval= {pval}')
	#Run Pearson test on original data
	xvals, yvals = zip(*measurements)
	corr, pval = pearsonr(xvals, yvals)
	print(f'With outliers: corr= {corr}, pval= {pval}')
	print('-'*50)

metrics = ['backtrack', 'runtimes']
heuristics = ['randoms', 'jeroslow', 'diag', 'dlis']

for metric in metrics:
	for heuristic in heuristics:
		getStats(metric + '_' + heuristic + '.pkl')