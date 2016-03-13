import numpy as np
import matplotlib.pyplot as plt

def plotWeekRegions(dayOfTheWeek, ax, isAbove=False):
	ylim = ax.get_ylim()
	if isAbove:
		textYLocation = (ylim[1] - ylim[0]) * 1.03 + ylim[0]
	else:
		textYLocation = (ylim[1] - ylim[0]) * 0.97 + ylim[0]

	N = len(dayOfTheWeek)
	x = range(N)
	mondays =[]
	for it in range(len(dayOfTheWeek)):
		if dayOfTheWeek[it] == 'M':
			mondays.append(it)

	weekNumber = 0
	if mondays[0] != x[0]:
		weekNumber += 1

	xdelta = x[1]-x[0]
	ybox = [ylim[1],ylim[1]]
	for it in range(len(mondays)):
		xi = x[mondays[it]]
		xbox = [xi-xdelta/2.0,xi+6+xdelta/2.0]
		if (it % 2 == 0):
			ax.fill_between(xbox, ybox, 0, color='lightgray')

		str = 'Week %d' % (it+1+weekNumber)
		ax.text(np.mean(xbox), textYLocation, str, 
			verticalalignment = 'center', horizontalalignment = 'center')

	if weekNumber:
		xbox = [x[0], x[mondays[0]-1]]
		str = 'Week 1'
		ax.text(np.mean(xbox), textYLocation, str, 
			verticalalignment = 'center', horizontalalignment = 'center')

	xBuffer = (x[1] - x[0]) / 2.0
	plt.xticks(x)
	ax.set_xticks(x)
	ax.set_xticklabels(dayOfTheWeek)
	plt.xlim([x[0]-xBuffer,x[-1]+xBuffer])
	plt.tick_params(axis='x', which='both', bottom='off', top='off')
	plt.xlabel('Day')	

	return