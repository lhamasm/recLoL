#from roleml import roleml
import requests
import mysql.connector as con

mydb = None
partype = {}

def connection():
	global mydb

	mydb = con.connect(user='root', password='doremifasol', host='localhost', database='recsys_db')

def processChamps(allChamps):
	global partype

	count = 1
	champs = []

	for c in allChamps:
		champ = {}
		champ['id'] = allChamps[c]['key']
		champ['name'] = allChamps[c]['name']

		if allChamps[c]['partype'] not in partype:
			partype[allChamps[c]['partype']] = count
			count += 1

		champ['partype'] = partype[allChamps[c]['partype']]
		champ['attack'] = allChamps[c]['info']['attack']
		champ['defense'] = allChamps[c]['info']['defense']
		champ['magic'] = allChamps[c]['info']['magic']
		champ['difficulty'] = allChamps[c]['info']['difficulty']

		champ['tank'] = 0
		champ['mage'] = 0
		champ['support'] = 0
		champ['fighter'] = 0
		champ['assassin'] = 0
		champ['marksman'] = 0

		for t in allChamps[c]['tags']:
			if t == 'Tank':
				champ['tank'] = 1
			elif t == 'Mage':
				champ['mage'] = 1
			elif t == 'Support':
				champ['support'] = 1
			elif t == 'Fighter':
				champ['fighter'] = 1
			elif t == 'Assasin':
				champ['assassin'] = 1
			elif t == 'Marksman':
				champ['marksman'] = 1

		for s in allChamps[c]['stats']:
			champ[s] = allChamps[c]['stats'][s]

		champs.append(champ)

	return champs

def requestSummonerData(region, summonerName, APIKey):
	URL = "https://" + region + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName + "?api_key=" + APIKey	
	response = requests.get(URL)

	return response.json()

def saveSummonerData(summonerName, level, accountId, summonerId):
	global mydb

	if mydb is None:
		connection()

	mycursor = mydb.cursor()

	sql = "INSERT INTO user (summonerName, level, accountId, summonerId) VALUES (%s, %s, %s, %s)"
	values = (summonerName, level, accountId, summonerId)
	mycursor.execute(sql, values)
	mydb.commit()

	print(mycursor.rowcount, "dado inserido")

def requestChampions():
	URL = 'https://ddragon.leagueoflegends.com/api/versions.json'
	response = requests.get(URL)
	responseJson = response.json()
	version = responseJson[0]

	URL = 'http://ddragon.leagueoflegends.com/cdn/' + version + '/data/pt_BR/champion.json'
	response = requests.get(URL)
	champions = response.json()

	champions = champions['data']

	allChamps = {}

	for c in champions:
		allChamps[int(champions[c]['key'])] = champions[c]

	return processChamps(allChamps)

def saveChampions(allChamps):
	global mydb

	if mydb is None:
		connection()

	mycursor = mydb.cursor() 

	sql = "INSERT INTO champion VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

	val = []
	for c in allChamps:
		val.append((c['id'], c['name'], c['partype'], c['attack'], c['defense'], 
			c['magic'], c['difficulty'], c['tank'], c['mage'], c['support'], c['fighter'], 
			c['assassin'], c['marksman'], c['hp'], c['hpperlevel'], c['mp'], 
			c['mpperlevel'], c['movespeed'], c['armor'], c['armorperlevel'], c['spellblock'], 
			c['spellblockperlevel'], c['attackrange'], c['hpregen'], c['hpregenperlevel'], c['mpregen'],
			c['mpregenperlevel'], c['crit'], c['critperlevel'], c['attackdamage'], c['attackdamageperlevel'],
			c['attackspeedperlevel'], c['attackspeed']))

	mycursor.executemany(sql, val)

	mydb.commit()

	print(mycursor.rowcount, "foram inseridos")

def requestChampionMastery(region, summonerName, APIKey):
	summoner = requestSummonerData(region, summonerName, APIKey)
	summonerId = str(summoner['id'])

	URL = "https://" + region + ".api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + summonerId + "?api_key=" + APIKey
	response = requests.get(URL)
	champs = response.json()

	champs = list(filter(lambda cm: cm['championLevel'] >= 5, champs))

	#allChamps, processedChamps = requestChampions()
	#good_with = []

	#for c in champs:
	#	good_with.append(allChamps[c['championId']])

	return champs

def saveChampionMastery(champs):
	global mydb

	if mydb is None:
		connection()

	mycursor = mydb.cursor() 

	sql = "INSERT INTO mastery VALUES (%s, %s, %s, %s)"

	val = []
	for c in champs:
		val.append((c['summonerId'], c['championId'], c['championLevel'], c['championPoints']))
	
	mycursor.executemany(sql, val)
	mydb.commit()

	print(mycursor.rowcount, "foram inseridos")

def requestMatches(region, summonerName, APIKey):
	summoner = requestSummonerData(region, summonerName, APIKey)
	accountId = str(summoner['accountId'])

	URL = "https://" + region + ".api.riotgames.com/lol/match/v4/matchlists/by-account/" + accountId + "?api_key=" + APIKey
	response = requests.get(URL)
	matches = response.json()
	matches = matches['matches']

	return matches

def saveMatches(matches, user):
	global mydb

	if mydb is None:
		connection()

	mycursor = mydb.cursor() 

	sql = "INSERT INTO recsys_db.match VALUES (%s, %s, %s, %s, %s)"

	val = []
	for m in matches:
		val.append((m['gameId'], user, m['champion'], m['lane'], m['role']))

	mycursor.executemany(sql, val)
	mydb.commit()

	print(mycursor.rowcount, "foram inseridos")

#def roleIdentification(region, game_id, APIKey):
#	url = "https://" + region + ".api.riotgames.com/lol/match/v4/matches/" + game_id + "?api_key=" + APIKey
#	response = request.get(url)
#	match = response.json()

#	url = "https://" + region + ".api.riotgames.com/lol/match/v4/timelines/by-match" + game_id + "?api_key=" + APIKey
#	response = request.get(url)
#	timeline = response.json()

#	return roleml.predict(match, timeline)

if __name__ == '__main__':
	APIKey = 'RGAPI-8f6746f4-5b9b-4f02-9e4d-6094039cc591'
	region = 'BR1'
	summoners = ['lhamasmtuctuc', 'Dorapan', 'Four Seasons']

	allChamps = requestChampions()
	saveChampions(allChamps)

	for summoner in summoners:
		s = requestSummonerData(region, summoner, APIKey)
		saveSummonerData(s['name'], s['summonerLevel'], s['accountId'], s['id'])

		masteries = requestChampionMastery(region, summoner, APIKey)
		saveChampionMastery(masteries)

		matches = requestMatches(region, summoner, APIKey)
		saveMatches(matches, s['id'])

		#print(roleIdentification(region, m[0]['gameId'], APIKey))