import pickle
import matplotlib.pyplot as plt


with open('runtimes_random.pkl', 'rb') as f:
	runtimes = pickle.load(f)

xvals, yvals = zip(*runtimes)
plt.plot(xvals, yvals, 'ro')
plt.show()