def connection():
	global mydb

	mydb = con.connect(user='root', password='doremifasol', host='localhost', database='recsys_db')

def retriveChampions():
	global mydb

	if mydb is None:
		connection()

	mycursor = mydb.cursor()

	# retrieving only the numerical attributes + champion's name
	mycursor.execute("""SELECT champion.name, champion.attack, champion.defense, champion.magic, 
		champion.difficulty, champion.hp, champion.hpperlevel, champion.mp, champion.mpperlevel,
		champion.movespeed, champion.armor, champion.armorperlevel, champion.spellblock, 
		champion.spellblockperlevel, champion.attackrange, champion.hpregen, 
		champion.hpregenperlevel, champion.mpregen, champion.mpregenperlevel, champion.crit, 
		champion.critperlevel, champion.attackdamage, champion.attackdamageperlevel, 
		champion.attackspeedperlevel, champion.atackspeed 
		FROM champion""")

	champions = mycursor.fetchall()

	return champions

def championsSimilarity(champions, features=None):
	mSimilarity = {}

	for c1 in champions:
		line = {}
		for c2 in champions:
			sim = 0
			for a in range(1, len(c2)):
				if features != None:
					if a in features:
						sim += (abs(c1[a]-c2[a]) ** 2.0)
				else:
					sim += (abs(c1[a]-c2[a]) ** 2.0)
			
			sim = sim ** 0.5
			line[c2[0]] = sim

		mSimilarity[c1[0]] = line

	return mSimilarity

def championsAverageSimilarity(champions, features=None):
	mSimilarity = {}

	for c1 in champions:
		line = {}
		for c2 in champions:
			sim = 0
			for a in range(1, len(c2)):
				if features != None:
					if a in features:
						sim += abs(c1[a]-c2[a])
				else:
					sim += abs(c1[a]-c2[a])
			
			sim = sim / (len(c2)-1)
			line[c2[0]] = sim

		mSimilarity[c1[0]] = line

	return mSimilarity

def championsCossineSimilarity(champions, features=None):
	mSimilarity = {}

	for c1 in champions:
		line = {}
		for c2 in champions:
			sim = 0
			for a in range(1, len(c2)):
				if features != None:
					if a in features:
						sim += c1[a]*c2[a]
				else:
					sim += c1[a]*c2[a]

			normaC1 = 0
			normaC2 = 0

			for a in range(1, len(c1)):
				if features != None:
					if a in features:
						normaC1 += c1[a] ** 2
				else:
					normaC1 += c1[a] ** 2

			normaC1 = normaC1 ** 0.5

			for a in range(1, len(c2)):
				if features != None:
					if a in features:
						normaC2 += c2[a] ** 2
				else:
					normaC2 += c2[a] ** 2

			normaC2 = normaC2 ** 0.5
			
			sim = sim / (normaC1*normaC2)
			line[c2[0]] = sim

		mSimilarity[c1[0]] = line

	return mSimilarity

def covariancia(c1, c2, features=None):
	xM = 0
	yM = 0
	cov = 0

	for a in range(1, len(c1)):
		if features != None:
			if a in features:
				xM += c1[a]
				yM += c2[a]
		else:
			xM += c1[a]
			yM += c2[a]

	xM = xM/(len(c1)-1)
	yM = yM/(len(c2)-1)

	for a in range(1, len(c1)):
		if features != None:
			if a in features:
				cov += (c1[a]-xM)*(c2[a]-yM)
		else:
			cov += (c1[a]-xM)*(c2[a]-yM)

	return cov, xM, yM

def desvioPadrao(c, media, features=None):
	dv = 0

	for a in range(1, len(c)):
		if features != None:
			if a in features:
				dv += ((c[a]-media) ** 2)
		else:
			dv += ((c[a]-media) ** 2)

	dv = dv ** 0.5

	return dv

def championSimilarityPearson(champions, features=None):
	mSimilarity = {}

	for c1 in champions:
		line = {}
		for c2 in champions:
			cov, xM, yM = covariancia(c1, c2, features)
			dv1 = desvioPadrao(c1, xM, features)
			dv2 = desvioPadrao(c2, yM, features)

			sim = cov/(dv1*dv2)

			line[c2[0]] = sim

		mSimilarity[c1[0]] = line

	return mSimilarity

def criaPlanilha(nomeArq, similarity):
	arquivo = open(nomeArq, 'w+')

	linhas = []

	linha = '-:'
	for c in similarity:
		linha += c + ':'
	linhas.append(linha[:len(linha)-1] + '\n')

	for c in similarity:
		linha = ''
		linha += c + ':'
		for sim in similarity[c]:
			linha += str(similarity[c][sim]) + ':'

		linhas.append(linha[:len(linha)-1] + '\n')

	arquivo.writelines(linhas)
	arquivo.close()

if __name__ == '__main__':
	# retrive all champs from champion's table
	champs = retriveChampions()

	similarity = championsSimilarity(champs)
	criaPlanilha('similaridade_1.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get)

	arquivo = open('sim_1.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	similarity = championsAverageSimilarity(champs)
	criaPlanilha('similaridade_2.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get)

	arquivo = open('sim_2.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	# ataque, defesa, magica, dificuldade, armadura
	similarity = championsSimilarity(champs, [1, 2, 3, 4, 10])
	criaPlanilha('similaridade_3.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get)

	arquivo = open('sim_3.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	# ataque, defesa, magica, armadura, resistencia magica
	similarity = championsSimilarity(champs, [1, 2, 3, 10, 12])
	criaPlanilha('similaridade_4.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get)

	arquivo = open('sim_4.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	# ataque, magica, hp, armadura, resistencia magica
	similarity = championsSimilarity(champs, [1, 3, 5, 10, 12])
	criaPlanilha('similaridade_5.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get)

	arquivo = open('sim_5.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	# ataque, defesa, magica, dificuldade, armadura
	similarity = championsAverageSimilarity(champs, [1, 2, 3, 4, 10])
	criaPlanilha('similaridade_6.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get)

	arquivo = open('sim_6.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	# ataque, defesa, magica, armadura, resistencia magica
	similarity = championsAverageSimilarity(champs, [1, 2, 3, 10, 12])
	criaPlanilha('similaridade_7.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get)

	arquivo = open('sim_7.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	# ataque, magica, hp, armadura, resistencia magica
	similarity = championsAverageSimilarity(champs, [1, 3, 5, 10, 12])
	criaPlanilha('similaridade_8.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get)

	arquivo = open('sim_8.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	similarity = championsSimilarity(champs, [1, 2, 3, 4, 5, 7, 10, 12, 21, 24])
	criaPlanilha('similaridade_9.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get)

	arquivo = open('sim_9.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	similarity = championsAverageSimilarity(champs, [1, 2, 3, 4, 5, 7, 10, 12, 21, 24])
	criaPlanilha('similaridade_10.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get)

	arquivo = open('sim_10.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	similarity = championsSimilarity(champs, [1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 21, 22, 23, 24])
	criaPlanilha('similaridade_11.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get)

	arquivo = open('sim_11.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	similarity = championsAverageSimilarity(champs, [1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 21, 22, 23, 24])
	criaPlanilha('similaridade_12.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get)

	arquivo = open('sim_12.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	similarity = championsCossineSimilarity(champs, [1, 2, 3, 4, 10])
	criaPlanilha('similaridade_13.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get, reverse=True)

	arquivo = open('sim_13.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	similarity = championsCossineSimilarity(champs, [1, 2, 3, 10, 12])
	criaPlanilha('similaridade_14.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get, reverse=True)

	arquivo = open('sim_14.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	similarity = championsCossineSimilarity(champs, [1, 3, 5, 10, 12])
	criaPlanilha('similaridade_15.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get, reverse=True)

	arquivo = open('sim_15.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	similarity = championsCossineSimilarity(champs, [1, 2, 3, 4, 5, 7, 10, 12, 21, 24])
	criaPlanilha('similaridade_16.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get, reverse=True)

	arquivo = open('sim_16.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	similarity = championsCossineSimilarity(champs)
	criaPlanilha('similaridade_17.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get, reverse=True)

	arquivo = open('sim_17.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	similarity = championSimilarityPearson(champs)
	criaPlanilha('similaridade_18.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get, reverse=True)

	arquivo = open('sim_18.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	similarity = championSimilarityPearson(champs, [1, 2, 3, 4, 10])
	criaPlanilha('similaridade_19.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get, reverse=True)

	arquivo = open('sim_19.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	similarity = championSimilarityPearson(champs, [1, 2, 3, 10, 12])
	criaPlanilha('similaridade_20.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get, reverse=True)

	arquivo = open('sim_20.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	similarity = championSimilarityPearson(champs, [1, 3, 5, 10, 12])
	criaPlanilha('similaridade_21.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get, reverse=True)

	arquivo = open('sim_21.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	similarity = championSimilarityPearson(champs, [1, 2, 3, 4, 5, 7, 10, 12, 21, 24])
	criaPlanilha('similaridade_22.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get, reverse=True)

	arquivo = open('sim_22.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	similarity = championsSimilarity(champs, [13, 15, 16, 2, 4])
	criaPlanilha('similaridade_23.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get)

	arquivo = open('sim_23.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	similarity = championsAverageSimilarity(champs, [13, 15, 16, 2, 4])
	criaPlanilha('similaridade_24.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get)

	arquivo = open('sim_24.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	similarity = championsCossineSimilarity(champs, [13, 15, 16, 2, 4])
	criaPlanilha('similaridade_25.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get, reverse=True)

	arquivo = open('sim_25.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()

	similarity = championSimilarityPearson(champs, [13, 15, 16, 2, 4])
	criaPlanilha('similaridade_26.csv', similarity)

	for c in similarity:
		similarity[c] = sorted(similarity[c], key = similarity[c].get, reverse=True)

	arquivo = open('sim_26.txt', 'w+')
	for c in similarity:
		imprimir = c + ':'
		for i in range(1, 4):
			imprimir += similarity[c][i] + ','
		arquivo.write(imprimir[:len(imprimir)-1] + '\n')
	arquivo.close()