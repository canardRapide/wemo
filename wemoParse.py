import csv

def parseDailySummary(filename):

	header = []
	rawData = []
	isStartOfUsageSummaryTable = False
	rowNumber = 0
	with open(filename, 'rb') as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			if not isStartOfUsageSummaryTable:
				if not row:
					continue
				if row[0] == "Daily Usage Summary":
					isStartOfUsageSummaryTable = True
			else:
				if not row:
					break
				if not header:
					header = row
				else:
					rawData.append([])
					colNumber = 0
					for col in row:
						rawData[rowNumber].append(col)
						colNumber += 1
					rowNumber += 1

	return (header, rawData)

def parseEnergyData(filename):

	header = []
	rawData = []
	isStartOfEnergyTable = False
	rowNumber = 0
	with open(filename, 'rb') as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			if not isStartOfEnergyTable:
				if not row:
					continue
				if row[0] == "Energy Data":
					isStartOfEnergyTable = True
			else:
				if not row:
					break
				if not header:
					header = row
				else:
					rawData.append([])
					colNumber = 0
					for col in row:
						rawData[rowNumber].append(col)
						colNumber += 1
					rowNumber += 1

	return (header, rawData)
