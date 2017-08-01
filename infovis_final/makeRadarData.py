import json,csv
import copy
from urllib.request import urlopen
#api_1: http://gd2.mlb.com/components/game/mlb/year_2016/month_0x/day_0x/miniscoreboard.json
#api_2: http://statsapi.mlb.com/api/vi/game/"gamepkid"

def readCsv2Lst(directory):
#from ./src/gamePK.csv read each related gamepk into list
	gamepk = []
	with open(directory, newline='') as loadFile:
		reader = csv.reader(loadFile)
		Lst = list(reader)
	#modify the format from [[gampkid]] to [gamepkid] 
	for game in range(1,len(Lst)):
		try:
			gamepk.append(Lst[game][0])
		except IndexError as emptyset:
			print ('the element is empty: '+str(Lst[game]))
	return gamepk
def writeCsv(Lst, nameStr):
	with open(nameStr, 'w', newline='') as outCsv:
		writer = csv.writer(outCsv)
		writer.writerow({'ballName'})
		for element in Lst:
			writer.writerow({element})
def writeJson(jsonDic, nameStr):
#storin the input jsonDic into json file under input directory
	with open(nameStr, 'w') as outFile:
		json.dump(jsonDic, outFile)
def loadFullData(gamepkid):
#usin game_pk id to get the json data from api2
	response = urlopen('http://statsapi.mlb.com/api/v1/game/'+gamepkid+'/feed/live?language=en').read().decode('utf-8')
	return json.loads(response)
def removeDuplicate(Lst):
	tempLst = list(set(Lst))
	return [x for x in tempLst if x is not None or '']
def dateStrToInt(Str):
#converting date string to integer for comparision
	numSet = ('0','1','2','3','4','5','6','7','8','9' )
	string = ''
	for s in range(4,len(Str)):
		if Str[s] in numSet:
			string+=Str[s]
	return int(string)
def buildDicStruc(ballLst, batterDic, radarData):
#creatin the struct of the output format
	for player in batterDic.values():
		for season in radarData.keys():
			radarData[season][player] = {}
	for ballName in ballLst:
		for season in radarData.keys():
			for player in radarData[season].keys():
				radarData[season][player][ballName] = 0
	return radarData
def buildBallLst(gamepkLst):
#from api2 build a ball type list
	fullBallLst = []
	for gamepkid in gamepkLst:
		gameJson = loadFullData(gamepkid)
		allPlays = gameJson.get('liveData').get('plays').get('allPlays')
		for play in range(len(allPlays)):
			playEvents = allPlays[play].get('playEvents')
			for event in range(len(playEvents)):
				ballName = playEvents[event].get('details').get('displayName')
				fullBallLst.append(ballName)
		print ('finished gamepkid:'+str(gamepkid)+' days ballName saving')
	ballLst = removeDuplicate(fullBallLst)
	print (ballLst)
	writeCsv(ballLst, './src/ballLst.csv')
	return ballLst
def buildRadarData(gamepkLst):
#usin the gamepkLst from 'loadFullData' Function to build the format of radar chart
	ballLst = readCsv2Lst('./src/ballLst.csv')
	batterDic = {'545361':'Mike Trout', '405395':'Albert Pujols', '592178':'Kris Bryant', '519203':'Anthony Rizzo', '605141':'Mookie Betts', '120074':'David Ortiz'}
	radarData = {'regularRace':{}, 'playOff':{}}
	resultSet = ('Single', 'Double', 'Triple', 'Home Run')
	#Creatin the structure of the radarData
	radarData = buildDicStruc(ballLst, batterDic, radarData)
	hitDic = copy.deepcopy(radarData)
	print('radarData', radarData)
	#Calculatin the Hit times and counts of faced diff. ballType for each player
	for gameid in gamepkLst:
		gameJson = loadFullData(gameid)
		allPlays = gameJson.get('liveData').get('plays').get('allPlays')
		for play in range(len(allPlays)):
			playEvents = allPlays[play].get('playEvents')
			batter = allPlays[play]['matchup']['batter']
			if batter in batterDic.keys():
				batterName = batterDic[batter]
				result = allPlays[play].get('result').get('event')
				date = dateStrToInt(gameJson.get('gameData').get('datetime').get('originalDate'))
				for event in range(len(playEvents)):
					ballName = playEvents[event].get('details').get('displayName')
					if date<1003:
						try:
							radarData['regularRace'][batterName][ballName]+=1
							#if playEvents[event].get('hitData') != None and result in resultSet:
							if result in resultSet:
								hitDic['regularRace'][batterName][ballName]+=1
						except KeyError as nonetype:
							print ('regular ballname', ballName)
					else:
						try:
							radarData['playOff'][batterName][ballName]+=1
							if result in resultSet:
								hitDic['playOff'][batterName][ballName]+=1
						except KeyError as nonetype2:
							print ('playOff ballname', ballName)
		print ('finished ',gameid,' games countin')
	print ('finished hit times counting\n', radarData)
	print ('hitDic: ', hitDic)
	#Calculatin the Hit rate for each player toward diff. ball types
	for season in radarData.keys():
		for player in radarData[season].keys():
			for balltype in radarData[season][player].keys():
				faceTimes = radarData[season][player][balltype]
				regularHit = hitDic[season][player][balltype]
				playOffHit = hitDic[season][player][balltype]
				try:
					if (season == 'regularRace'):
						hitRate = regularHit/faceTimes
						radarData[season][player][balltype] = hitRate
					if (season == 'playOff'):
						hitRate = playOffHit/faceTimes
						radarData[season][player][balltype] = hitRate
				except ZeroDivisionError as divzero:
					print ('div by zero, faceTimes= ',faceTimes)
	print (radarData)
	return radarData
if __name__ == '__main__':
	gamepkLst = readCsv2Lst('./src/gamePK.csv')
	radarData = buildRadarData(gamepkLst)
	writeJson(radarData, './src/radarData-1.json')
