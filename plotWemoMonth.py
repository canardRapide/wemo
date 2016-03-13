import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import time
import datetime
import wemoPlot
import wemoParse
from matplotlib.patches import Polygon
from matplotlib.ticker import MultipleLocator

isPlotTimeOn = True
isPlotPower = True
isPlotCost = True
isPlotEnergyData = True
isShowWorkAndOutOfTown = True

# February bill (Boston MA)
# Delivery and generation charges
deliveryChargePerKWH = 0.168
generationChargePerKWH = 0.108
costPerKWH = deliveryChargePerKWH + generationChargePerKWH

##########################################################################
# Parse WeMo data export .csv file
filename = "Export for WeMo Insight.csv"
dailySummaryHeader, dailySummary = wemoParse.parseDailySummary(filename)
energyDataHeader, energyData = wemoParse.parseEnergyData(filename)

##########################################################################
# Unpack raw data
date = []
timeOn = []
powerConsumption = []
dailyCost = []
energyCostPerKWH = dailySummary[0][9]
for it in range(len(dailySummary)):
	date = [dailySummary[it][0]] + date
	timeOn = [dailySummary[it][1]] + timeOn
	powerConsumption = [float(dailySummary[it][2])] + powerConsumption
	dailyCost = [float(dailySummary[it][8])] + dailyCost

dateAndTime = []
powerConsumptionOverHalfHour = []
for it in range(len(energyData)):
	dateAndTime = [energyData[it][0]] + dateAndTime
	powerConsumptionOverHalfHour = [float(energyData[it][1])] + powerConsumptionOverHalfHour

##########################################################################
# Clean up daily summary data
# Date and time formatting
dateDT = []
dayOfTheWeek = []
pattern = '%Y/%m/%d'
for it in date:
	dt = datetime.datetime.strptime(it, pattern)
	dateDT.append(dt)
	day = dt.strftime('%A')
	dayOfTheWeek.append(day[0])

# Get time on in decimal hours
timeOnHours = []
for it in timeOn:
	tokens = it.split(':')
	hours = int(tokens[0])
	minutes = int(tokens[1])
	hours += minutes / 60.0
	timeOnHours.append(hours)

# Calculate cost
cost = []
for it in powerConsumption:
	cost.append(it * costPerKWH)

##########################################################################
# Clean up energy data
# Date and time formatting
epoch = []
dateAndTimeDT = []
pattern = '%Y/%m/%d %H:%M'
for it in dateAndTime:
	epoch.append(int(time.mktime(time.strptime(it, pattern))))
	dt = datetime.datetime.strptime(it, pattern)
	dateAndTimeDT.append(dt)

startDay = dateAndTimeDT[0]
startDay = datetime.date(startDay.year, startDay.month, startDay.day)
endDay = dateAndTimeDT[-1]
endDay = datetime.date(endDay.year, endDay.month, endDay.day)
delta = endDay - startDay
nDays = delta.days
nThirtyMinuteBlocks = 24 * 2
timeUp = np.zeros((nDays, nThirtyMinuteBlocks))

for it in range(len(powerConsumptionOverHalfHour)):
	if powerConsumptionOverHalfHour[it] > 0:
		currentDate = dateAndTimeDT[it]
		delta = datetime.date(currentDate.year, 
			currentDate.month, currentDate.day) - startDay
		currentDay = int(delta.days)
		hours = currentDate.hour + currentDate.minute / 60.0
		index = int(round(hours * 2)) - 1
		timeUp[currentDay][index] = 1.0
	
##########################################################################
# Plot setup
N = len(date)
x = range(N)
xBuffer = (x[1] - x[0]) / 2.0

xL = 0.15
xR = 0.2
yBorder = 0.15
ax_size = [0.0 + xL, 0.0 + yBorder, 
	1.0 - (xL+ xR), 1.0 - 2.0 * yBorder]

barWidth = 1.0

##########################################################################
if isPlotTimeOn:
	# Plot time on per day	
	barColor = 'palegreen'
	textColor = 'teal'
	fig = plt.figure(facecolor='white')
	ax = fig.add_axes(ax_size)

	# y-axis formatting
	plt.yticks(np.arange(0,25,4))
	plt.ylim([0,24])
	plt.ylabel('Time On Per Day (hours)')

	# Title
	titleStr = '%s\n%s - %s (%d days)' % ('WeMo Insight Switch Daily Usage', 
		dateDT[0].strftime("%B %d"),
		dateDT[-1].strftime("%B %d"),
		len(x))
	plt.title(titleStr)

	# Bars
	ax.bar(x, timeOnHours, color = barColor, align = 'center', width = barWidth)

	# Median
	y = np.median(timeOnHours)
	hh = int(y)
	mm = (y-hh)*60
	ax.plot([x[0]-xBuffer,x[-1]+xBuffer], [y,y], color = textColor, linewidth = 2)
	str = '%d hours and\n%d minutes\nMedian\nUsage' % (hh, mm)
	ax.text(x[-1]+xBuffer*3/2,y,str,
		verticalalignment = 'center', horizontalalignment = 'left', 
		color = textColor, fontweight = 'bold')

	# Total
	total = np.sum(timeOnHours)
	ylim = ax.get_ylim()
	yloc = (ylim[1] - ylim[0]) * -0.1 + ylim[0]
	str = 'Total: %d hours' % (total)
	ax.text(x[-1]+xBuffer*3/2, yloc, str,
		verticalalignment = 'center', horizontalalignment = 'left', 
		color = textColor, fontweight = 'bold',
		bbox={'color':textColor,'facecolor':'white', 'alpha':1.0, 'pad':10})

	# Week regions and x-axis formatting
	wemoPlot.plotWeekRegions(dayOfTheWeek, ax)

	plt.savefig("dailyUsage.tif")
	plt.draw()

##########################################################################
if isPlotPower:
	# Plot power consumption per day
	barColor = 'salmon'
	textColor = 'darkred'
	fig = plt.figure(facecolor='white')
	ax = fig.add_axes(ax_size)

	# y-axis formatting
	plt.yticks(np.arange(0.0,1.1,0.1))
	plt.ylim([0,1])
	plt.ylabel('Power Consumption (kWh)')

	# Title
	titleStr = '%s\n%s - %s (%d days)' % ('Wemo Insight Switch Daily Power Consumption', 
		dateDT[0].strftime("%B %d"),
		dateDT[-1].strftime("%B %d"),
		len(x))
	plt.title(titleStr)

	# Bars
	ax.bar(x, powerConsumption, color = barColor, align = 'center', width = barWidth)

	# Median
	y = np.median(powerConsumption)
	ax.plot([x[0]-xBuffer,x[-1]+xBuffer], [y,y], color = textColor, linewidth = 2)
	str = '%.2f kWh\nMedian\nUsage' % (y)
	ax.text(x[-1]+xBuffer*3/2,y,str,
		verticalalignment = 'center', horizontalalignment = 'left', 
		color = textColor, fontweight = 'bold')

	# Total
	total = np.sum(powerConsumption)
	ylim = ax.get_ylim()
	yloc = (ylim[1] - ylim[0]) * -0.1 + ylim[0]
	str = 'Total: %.2f kWh' % (total)
	ax.text(x[-1]+xBuffer*3/2, yloc, str,
		verticalalignment = 'center', horizontalalignment = 'left', 
		color = textColor, fontweight = 'bold',
		bbox={'color':textColor,'facecolor':'white', 'alpha':1.0, 'pad':10})

	# Week regions and x-axis formatting
	wemoPlot.plotWeekRegions(dayOfTheWeek, ax)

	plt.savefig("power.tif")
	plt.draw()

##########################################################################
if isPlotCost:
	# Plot cost per day
	barColor = 'paleturquoise'
	textColor = 'darkcyan'
	fig = plt.figure(facecolor='white')
	ax = fig.add_axes(ax_size)

	# y-axis formatting
	plt.yticks(np.arange(0.0,1.1,0.1))
	plt.ylim([0,1])
	plt.ylabel('Electricity Cost')
	ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('$%.2f'))

	# Title
	titleStr = '%s\n%s - %s (%d days)' % ('WeMo Insight Switch Daily Cost$\mathregular{^*}$', 
		dateDT[0].strftime("%B %d"),
		dateDT[-1].strftime("%B %d"),
		len(x))
	plt.title(titleStr, linespacing = 0.3, y = 1.025)

	# Bars
	ax.bar(x, cost, color = barColor, align = 'center', width = barWidth)

	# Median
	y = np.median(cost)
	ax.plot([x[0]-xBuffer,x[-1]+xBuffer], [y,y], color = textColor, linewidth = 2)
	str = '$%02.2f\nMedian\nUsage' % (y)
	ax.text(x[-1]+xBuffer*3/2, y, str,
		verticalalignment = 'center', horizontalalignment = 'left', 
		color = textColor, fontweight = 'bold')

	# Total
	total = np.sum(cost)
	ylim = ax.get_ylim()
	yloc = (ylim[1] - ylim[0]) * -0.1 + ylim[0]
	str = 'Total: $%02.2f' % (total)
	ax.text(x[-1]+xBuffer*3/2, yloc, str,
		verticalalignment = 'center', horizontalalignment = 'left', 
		color = textColor, fontweight = 'bold',
		bbox={'color':textColor,'facecolor':'white', 'alpha':1.0, 'pad':10})

	# Week regions and x-axis formatting
	wemoPlot.plotWeekRegions(dayOfTheWeek, ax)

	# Footnote
	xlim = ax.get_xlim()
	xloc = (xlim[1] - xlim[0]) * -0.15 + xlim[0]
	ylim = ax.get_ylim()
	yloc = (ylim[1] - ylim[0]) * -0.15 + ylim[0]
	str = 'February electricity charge Boston MA\n' +\
		'%.1f' % (costPerKWH * 100.0) +\
		u'\xa2' + ' per kWh (' +\
		'%.1f' % (deliveryChargePerKWH * 100.0) +\
		u'\xa2' + ' delivery + ' +\
		'%.1f' % (generationChargePerKWH * 100.0) +\
		u'\xa2' + ' generation)'
	ax.text(xloc, yloc, str,
		verticalalignment = 'center', horizontalalignment = 'left',
		fontsize = 10)
	str = ' $\mathregular{^*}$'
	ax.text(xloc - 0.75, yloc, str,
		verticalalignment = 'center', horizontalalignment = 'left')

	plt.savefig("cost.tif")
	plt.draw()

##########################################################################
if isPlotEnergyData:
	# Plot energy data in 30 minute blocks
	fig = plt.figure(facecolor='white')
	ax = fig.add_axes(ax_size)

	# y-axis formatting
	plt.yticks(np.arange(0,49,8))
	minorLocator = MultipleLocator(2)
	ax.yaxis.set_minor_locator(minorLocator)
	ax.set_yticklabels(('12:00 a.m.','4:00 a.m.','8:00 a.m.','12:00 p.m.',
		'4:00 p.m.','8:00 p.m.', '11:59 p.m.'))
	plt.ylim([0,48])
	plt.ylabel('Time')

	# Title
	titleStr = '%s\n%s - %s (%d days)\n' % ('WeMo Insight Switch Time On (30 minute resolution)', 
		dateDT[0].strftime("%B %d"),
		dateDT[-1].strftime("%B %d"),
		len(x))
	plt.title(titleStr)

	# Week regions and x-axis formatting
	wemoPlot.plotWeekRegions(dayOfTheWeek, ax, True)

	# Get Mondays
	mondays =[]
	for it in range(len(dayOfTheWeek)):
		if dayOfTheWeek[it] == 'M':
			mondays.append(it)

	if isShowWorkAndOutOfTown:
		# Get time at work regions
		# First week
		r = 174 / 255.0;
		g = 242 / 255.0;
		b = 245 / 255.0;
		a = 1;
		v = [r,g,b,a]
		if mondays[0] != x[0]:
			xi = x[mondays[0]] - 7
			box = Polygon(((xi-xBuffer,8.5*2),
				(xi-xBuffer,17*2),
				(xi+4+xBuffer,17*2),
				(xi+4+xBuffer,8.5*2)),
	    		fc=v, ec=v, lw=1)
			ax.add_artist(box)

		# Loop over weeks
		for it in range(len(mondays)):
			xi = x[mondays[it]]
			box = Polygon(((xi-xBuffer,8.5*2),
				(xi-xBuffer,17*2),
				(xi+4+xBuffer,17*2),
				(xi+4+xBuffer,8.5*2)),
	    		fc=v, ec=v, lw=1)
			ax.add_artist(box)

		# Work text
		xi = x[mondays[-1]]
		xloc = np.mean([xi-xBuffer, xi+4+xBuffer])
		yloc = np.mean([8.5*2, 17*2])
		str = 'Normal\nWorking\nHours'
		ax.text(xloc, yloc, str,
			verticalalignment = 'center', horizontalalignment = 'center', 
			fontweight = 'bold', color = 'darkcyan', fontsize = 11)

		# Out of town
		r = 213 / 255.0;
		g = 174 / 255.0;
		b = 245 / 255.0;
		a = 1;
		v = [r,g,b,a]
		xi = mondays[-1] - 2
		box = Polygon(((xi-xBuffer,0),
			(xi-xBuffer,48),
			(xi+xBuffer,48),
			(xi+xBuffer,0)),
	    	fc=v, ec=v, lw=1)
		ax.add_artist(box)
		xi = xi - 1
		box = Polygon(((xi-xBuffer,(8+12)*2),
			(xi-xBuffer,48),
			(xi+xBuffer,48),
			(xi+xBuffer,(8+12)*2)),
	    	fc=v, ec=v, lw=1)
		ax.add_artist(box)
		xi = xi + 2
		box = Polygon(((xi-xBuffer,0),
			(xi-xBuffer,(8+12)*2),
			(xi+xBuffer,(8+12)*2),
			(xi+xBuffer,0)),
	    	fc=v, ec=v, lw=1)
		ax.add_artist(box)

		# Out of town text
		xloc = xi-xBuffer
		yloc = np.mean([8.5*2, 17*2])
		str = 'Out\nof\nTown'
		ax.text(xloc, yloc, str,
			verticalalignment = 'center', horizontalalignment = 'center', 
			fontweight = 'bold', color = 'purple', fontsize = 11)

	# Time up
	r = 245 / 255.0;
	g = 177 / 255.0;
	b = 174 / 255.0;
	a = 1;
	v = [r,g,b,a]
	for it in range(len(timeUp)):
		for jt in range(len(timeUp[it])):
			if timeUp[it][jt] > 0:
				box = Polygon(((it-xBuffer,jt),
					(it-xBuffer,jt+1),
					(it+xBuffer,jt+1),
					(it+xBuffer,jt)),
                    fc=v, ec=v, lw=1)
				ax.add_artist(box)

	# Plot week separators
	for it in range(len(mondays)):
		xi = mondays[it] - xBuffer
		ax.plot([xi,xi],[0,48], color = 'black')
				
	# Total
	total = np.sum(timeOnHours)
	xlim = ax.get_xlim()
	xloc = (xlim[1] - xlim[0]) * 1.05 + xlim[0]
	yloc = np.mean([8.5*2, 17*2])
	str = 'Total Time On:\n%d hours' % (total)
	ax.text(xloc, yloc, str,
		verticalalignment = 'center', horizontalalignment = 'left', 
		fontweight = 'bold',
		bbox={'color':'darkred','facecolor':v[0:3], 'alpha':1, 'pad':10})

	plt.savefig("timeOn.tif")
	plt.draw()

plt.show()




