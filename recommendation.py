from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import mysql.connector as con

mydb = None

def connection():
	global mydb

	mydb = con.connect(user='root', password='doremifasol', host='localhost', database='recsys_db')

def retrieveMatch(user):
	global mydb

	if mydb is None:
		connection()

	mycursor = mydb.cursor()
	sql = "SELECT champion FROM recsys_db.match WHERE user = %s"
	usr = (user, )
	mycursor.execute(sql, usr)
	matches = mycursor.fetchall()

	return matches

def mostUsedChampion(matches):
	champions = {}

	for m in matches:
		if m not in champions:
			champions[m] = 1
		else:
			champions[m] += 1

	champions = sorted(champions, key=champions.get, reverse=True)

	return champions

def retrieveMastery(user):
	global mydb

	if mydb is None:
		connection()

	mycursor = mydb.cursor()
	sql = "SELECT * champion FROM mastery WHERE user = %s"
	usr = (user, )
	mycursor.execute(sql, usr)
	champions = mycursor.fetchall()

	return champions

def retrieveChampions(champion_id=None):
	global mydb

	if mydb is None:
		connection()

	mycursor = mydb.cursor()

	champions = None
	if champion_id is not None:
		sql = "SELECT attack, defense, magic, hp, hpperlevel, movespeed, armor, armorperlevel, spellblock, spellblockperlevel, attackrange, attackdamage, attackdamageperlevel, atackspeed, attackspeedperlevel FROM champion WHERE id = %s"
		mycursor.execute(sql, champion_id)
		champions = mycursor.fetchone()
	else:
		sql = "SELECT id FROM champion"
		mycursor.execute(sql)
		champions = mycursor.fetchall()

	return champions

def retrieveSummoner(username):
	global mydb

	if mydb is None:
		connection()

	mycursor = mydb.cursor()
	sql = "SELECT summonerId FROM user WHERE summonerName = %s"
	name = (username,)
	mycursor.execute(sql, name)
	summoner = mycursor.fetchone()

	return summoner

def retrieveChampionTags(champion_id):
	global mydb

	if mydb is None:
		connection()

	mycursor = mydb.cursor()
	sql = "SELECT tank, mage, support, fighter, assassin, marksman FROM champion WHERE id = %s"
	mycursor.execute(sql, champion_id)
	champion = mycursor.fetchone()

	return champion

def similarity(a, b):
	champion_a = retrieveChampions(a)
	champion_b = retrieveChampions(b)

	sim = 0
	for attibute in range(len(champion_a)):
		sim += abs(champion_a[attibute]-champion_b[attibute])
	sim = sim / len(champion_a)

	return sim

def tagsScore(a, b):
	champion_a = retrieveChampionTags(a)
	champion_b = retrieveChampionTags(b)

	score = 0
	for tag in range(len(champion_a)):
		if champion_a[tag] == champion_b[tag]:
			score += 1.0/len(champion_a)

	return score

def retrieveSkills(champion_id):
	global mydb

	if mydb is None:
		connection()

	mycursor = mydb.cursor()
	sql = "SELECT skill_q, skill_w, skill_e, skill_r FROM skills WHERE champion = %s"
	mycursor.execute(sql, champion_id)
	champion = mycursor.fetchone()

	return champion

def preprocess(skill_1, skill_2):
	l1 = []
	l2 = []

	sk_1 = word_tokenize(skill_1)
	sk_2 = word_tokenize(skill_2)

	sk_1_set = {w for w in sk_1 if not w in sw}
	sk_2_set = {w for w in sk_2 if not w in sw}

	rvector = sk_1_set.union(sk_2_set)
	for w in rvector:
		if w in sk_1_set:
			l1.append(1)
		else:
			l1.append(0)

		if w in sk_2_set:
			l2.append(1)
		else:
			l2.append(0)

	return rvector, l1, l2

def cosineSimilarity(rvector, l1, l2):
	cos = 0

	for i in range(len(rvector)):
		cos += l1[i] * l2[i]
	cosine = cos / float((sum(l1) * sum(l2)) ** 0.5)

	return cosine

def similaridadeParAPar(skill_a, skill_b, sim_anterior):
	rvector, l1, l2 = preprocess(skill_a, skill_b)
	sim = cosineSimilarity(rvector, l1, l2)

	if sim > sim_anterior:
		return sim
	else:
		return sim_anterior

def abilitiesSimilarity(a, b):
	champion_a = retrieveSkills(a)
	champion_b = retrieveSkills(b)

	skills_sim = []
	for skill_a in champion_a:
		sim = 0
		for skill_b in champion_b:
			sim = similaridadeParAPar(skill_a, skill_b, sim)

		skills_sim.append(sim)

	sim = 0
	for skill_sim in skills_sim:
		sim += skill_sim

	return sim / len(skills_sim)

def retrieveChampionName(champion_id):
	global mydb

	if mydb is None:
		connection()

	mycursor = mydb.cursor()
	sql = "SELECT name FROM champion WHERE id = %s"
	mycursor.execute(sql, champion_id)
	champion_name = mycursor.fetchone()

	return champion_name
	
if __name__ == '__main__':
	username = raw_input("Informe o nome do jogador:")
	summoner = retrieveSummoner(username)
	matches = retrieveMatch(summoner[0]) # lista de tuplas (id_champion, )
	champions = mostUsedChampion(matches) # lista de tuplas (id_champion, )
	all_champions = retrieveChampions() # lista de tuplas (id_champion, )
	sw = stopwords.words('english')

	count = 0
	recomendacoes = []
	for a in champions:
		r = []
		if count < 3:
			count += 1
			for b in all_champions:
				sim = similarity(a, b)
				score = tagsScore(a, b)
				abilities_sim = abilitiesSimilarity(a, b)
				total = abilities_sim + score - (sim/100.0)

				r.append({
					'id': b[0], 
					'similarity': sim, 
					'score': score,
					'abilities': abilities_sim, 
					'total': total
				})

			r = sorted(r, key = lambda i: i['total'])
			recomendacoes.append(r)

	#print(recomendacoes)

	count = 0
	for a in champions:
		imprimir = ''
		if count < 3:
			count += 1
			imprimir += retrieveChampionName(a)[0] + ': '
			r = recomendacoes[count-1]
			contador = 0
			for c in r:
				if contador < 5:
					contador += 1
					imprimir += retrieveChampionName((c['id'],))[0] + ','
				else:
					imprimir += '\n'
					print(imprimir)
					break
		else:
			break


