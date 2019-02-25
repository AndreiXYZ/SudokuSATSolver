import pickle
import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr
from scipy.stats import spearmanr, kendalltau, mannwhitneyu
import numpy as np
import seaborn as sns

def removeOutliers(runtimes):
	xvals, yvals = zip(*runtimes)
	dataMean = np.mean(yvals)
	dataStd = np.std(yvals)
	filtered = [(x,y) for x,y in runtimes if (dataMean - 2*dataStd < y < dataMean + 2*dataStd)]
	print(f'Removed {len(xvals)-len(filtered)} outliers')
	return filtered

def createHeatmap(measurements):
	xvals, yvals = zip(*measurements)
	xvals = np.array(xvals)
	yvals = np.array(yvals)

	ydim = yvals.max()+1
	xdim = xvals.max()-20
	
	twodvals = np.concatenate((xvals[:,np.newaxis],yvals[:,np.newaxis]), axis=1)
	unique, counts = np.unique(twodvals.astype(np.int8), return_counts=True, axis=0)
	countsArray = np.concatenate((unique,counts[:,np.newaxis]), axis=1)

	a = np.zeros((int(yvals.max()+1),int(xvals.max()-20)))
	for x,y,z in countsArray:
		a[int(y)][int(x-21)] = z

	ax = sns.heatmap(a, annot=True, xticklabels=np.arange(21,32), yticklabels=np.arange(0,ydim-1).astype(np.int8),
					 linewidth=0.5)
	plt.xlabel('num. givens')
	plt.ylabel('num. backtracks')
	ax.invert_yaxis()
	plt.title(heuristic + ' ' + metric + ' heatmap')
	plt.show()

def getStats(heuristic, metric):
	filename = metric + '_' + heuristic + '.pkl'
	print('Stats for ', filename)
	with open(filename, 'rb') as f:
		measurements = pickle.load(f)

	#Remove outliers for plotting only
	measurementsCurated = removeOutliers(measurements)
	
	#Create heatmap
	createHeatmap(measurementsCurated)
	
	xvals, yvals = zip(*measurementsCurated)
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
	# corr, pval = spearmanr(xvals, yvals)
	# corr, pval = kendalltau(xvals, yvals)
	print(f'No outliers: corr= {corr}, pval= {pval}')
	#Run Pearson test on original data
	xvals, yvals = zip(*measurements)
	corr, pval = pearsonr(xvals, yvals)
	print(f'With outliers: corr= {corr}, pval= {pval}')
	print('-'*50)

metrics = ['backtrack', 'runtimes']
heuristics = ['random', 'jeroslow', 'diag', 'dlis']

for metric in metrics:
	for heuristic in heuristics:
		getStats(heuristic, metric)
# getStats('jeroslow', 'backtrack')
# getStats('jeroslow', 'runtimes')