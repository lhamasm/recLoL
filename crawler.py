import requests
import mysql.connector as con
from bs4 import BeautifulSoup

mydb = None
bs = None

def connection():
	global mydb

	mydb = con.connect(user='root', password='doremifasol', host='localhost', database='recsys_db')

def retriveChampions():
	global mydb

	if mydb is None:
		connection()

	mycursor = mydb.cursor()
	mycursor.execute("SELECT champion.id, champion.name FROM champion")
	champions = mycursor.fetchall()

	return champions

def saveSkills(skills):
	global mydb

	if mydb is None:
		connection()

	mycursor = mydb.cursor() 

	sql = "INSERT INTO skills VALUES (%s, %s, %s, %s, %s, %s)"

	val = []
	for c in skills:
		val.append((c['id'], c['ataque_basico'], c['q'], c['w'], c['e'], c['ultimate']))

	mycursor.executemany(sql, val)
	mydb.commit()

	print(mycursor.rowcount, "foram inseridos")

def getSkill(skill_name):
	global bs
	
	skill = bs.find('div', class_=skill_name)
	skill = skill.find('div')
	skill = skill.find('div')
	skill = skill.find_all('table')
	skill = skill[1].find_all('tr')

	descricao_skill = ''
	for tr in skill:
		tds = tr.find_all('td')
		for td in tds:
			skill_leveling = td.find('div', class_='skill_leveling')
			if skill_leveling == None:
				descricao_skill += td.text

	return descricao_skill

if __name__ == '__main__':
	global bs 
	
	champs = []

	champions = retriveChampions()
	for champion in champions:
		print(champion[1])

		nome = ''
		if champion[1] == 'Nunu e Willump':
			nome = 'Nunu'
		elif ' ' in champion[1]:
			tokens = champion[1].split(' ')
			nome = tokens[0] + '_' + tokens[1]
		elif "'" in champion[1]:
			tokens = champion[1].split("'")
			nome = tokens[0] + '%27' + tokens[1]
		elif champion[1] == 'Bardo':
			nome = 'Bard'
		else:
			nome = champion[1]

		url = 'https://leagueoflegends.fandom.com/wiki/' + nome + '/Abilities'
		html = requests.get(url)

		bs = BeautifulSoup(html.text, 'lxml')
		descricao_ataque_basico = getSkill('skill_innate')
		descricao_Q = getSkill('skill_q')
		descricao_W = getSkill('skill_w')
		descricao_E = getSkill('skill_e')
		descricao_R = getSkill('skill_r')

		skills = {}

		skills['id'] = champion[0]
		skills['ataque_basico'] = descricao_ataque_basico
		skills['q'] = descricao_Q
		skills['w'] = descricao_W
		skills['e'] = descricao_E
		skills['ultimate'] = descricao_R

		champs.append(skills)

	saveSkills(champs)
