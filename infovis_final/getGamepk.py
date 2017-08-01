import json,csv
from urllib.request import urlopen

def creatDateDic():
#Creatin game days for each month into a Dic
	month = {'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[]}
	big_month = ['05','07','08','10']
	small_month = ['06','09']
	for k in month.keys():
		if (k in big_month):
			dates = [ date for date in range(1,32) ]
			month[k] = dates
		if (k in small_month):
			dates = [ date for date in range(1,31) ]
			month[k] = dates
		if (k=='04'):
			dates = [ date for date in range(3,31) ]
			month[k] = dates
		if (k=='11'):
			dates = [ date for date in range(1,4) ]
			month[k] = dates
	return month
def getGamepk(dateDic):
#Storing all the game pk id into a list from src1
	gamePK = []
	for k in dateDic.keys():
		for d in range(len(dateDic[k])):
			if (int(dateDic[k][d])<10):
				response = urlopen('http://gd2.mlb.com/components/game/mlb/year_2016/month_'+k+'/day_0'+str(dateDic[k][d])+'/miniscoreboard.json').read().decode('utf-8')
				responseJson = json.loads(response)
				tempLst = (responseJson.get('data').get('games').get('game'))
				try:
					for i in range(len(tempLst)):
						gamePK.append(tempLst[i].get('game_pk'))
				except TypeError as e1:
				#no any games during the day
					print ('the zero game date is: '+k+str(dateDic[k][d]))
				except KeyError as e2:
				#only one game during the day
					print ('there is only 1 game in '+k+str(dateDic[k][d]))
					gamePK.append(tempLst.get('game_pk'))
			else:
				response = urlopen('http://gd2.mlb.com/components/game/mlb/year_2016/month_'+k+'/day_'+str(dateDic[k][d])+'/miniscoreboard.json').read().decode('utf-8')
				responseJson = json.loads(response)
				tempLst = (responseJson.get('data').get('games').get('game'))
				try:
					for i in range(len(tempLst)):
						gamePK.append(tempLst[i].get('game_pk'))
				except TypeError as e3:
					print ('the zero game date is: '+k+str(dateDic[k][d]))
				except KeyError as e4:
					print ('there is only 1 game in '+k+str(dateDic[k][d]))
					gamePK.append(tempLst.get('game_pk'))
		print ('finished month'+k+'gamepk storing')
	return gamePK
def collectTargetGames(gamepkLst):
#From gamepkLst find related games and return a list
	targetLst = []
	#define the target teams below, we can also modify the list to find different target teams
	targetTeams = ['Los Angeles Angels', 'Chicago Cubs', 'Boston Red Sox']
	for game in gamepkLst:
		response = urlopen('http://statsapi.mlb.com/api/v1/game/'+game+'/feed/live?language=en').read().decode('utf-8')
		responseJson = json.loads(response)
		try:
			home = responseJson.get('gameData').get('teams').get('home').get('name').get('full')
			away = responseJson.get('gameData').get('teams').get('away').get('name').get('full')
			if ((home in targetTeams) or (away in targetTeams)):
				targetLst.append(game)
				print ('game id: '+str(game)+' has one of the team in target list!')
		except AttributeError as e5:
			print ('current gamepk may not have the same format with the others: '+str(game))
	return targetLst
def storeGamepk(gamepkLst):
#Storin the input gamepk list into csv file under src directory
	csvFile = open('./src/gamePK.csv','w+',newline='')
	try:
		writer = csv.writer(csvFile)
		writer.writerow({'gamepk'})
		for i in range(len(gamepkLst)):
			writer.writerow({gamepkLst[i]})
	finally:
		csvFile.close()
if __name__ == '__main__':
	gamepk = getGamepk(creatDateDic())
	print ('the total amounts of games are: '+str(len(gamepk)))
	targets = collectTargetGames(gamepk)
	print ('the total amounts of related games are: '+str(len(targets)))
	storeGamepk(targets)
