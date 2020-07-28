import sys
import urllib.request, json
import sqlite3
import csv
import datetime

logitiedosto = 'tapahtumat.log'
tietokanta = 'haettavatasemat.db'
asematcsv = 'sää-asemat-ilmatieteenlaitos.csv'

f = open(logitiedosto, "a")
conn = sqlite3.connect(tietokanta)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS paikkakunnat (kunta text, FMISID integer)')
conn.commit()

def loggeri(viesti):
	f.write(f'{datetime.datetime.now()} : {viesti}\n')
	
def haeLampotilaITL(paikka_koodi):
	itl_url = f'https://ilmatieteenlaitos.fi/observation-data?station={paikka_koodi}'
	with urllib.request.urlopen(itl_url) as url:
		data = json.loads(url.read().decode())
		if "t2m" in data:
			return str(data['t2m'][-1][1]) + 'C'
		else:
			loggeri("sääasemalta ei löydy lämpötilatietoja")
			return "Sääasemalta ei löydy lämpötilatietoja"

def lueKannasta():
	onnistuneetHaut = 0
	print('===================================================')
	for row in c.execute('SELECT * FROM paikkakunnat ORDER BY kunta'):
		#print(f'{row[0]}\t\t\t\t{haeLampotilaITL(row[1])}C')
		lampotila = haeLampotilaITL(row[1])
		if(lampotila[-1] == 'C'):
			onnistuneetHaut +=1
		print(' {: <40} {: <20}'.format( row[0], lampotila) )
	loggeri(f'Onnistuneita hakuja {onnistuneetHaut}')


def lisaaKantaan(paikka):
	c.execute('INSERT INTO paikkakunnat VALUES (?, ?)', (paikka[0], int(paikka[1])))
	conn.commit()
	print(f'paikka {paikka[0]} lisätty listaan')

def tyhjennaTaulu():
	#print(f'Taulu tyhjäksi')
	c.execute('DELETE FROM paikkakunnat')
	conn.commit()

def syottoLuuppi():
	tyhjennaTaulu()
	while True:
		vaihtoehdot = 0
		paikat = []

		with open(asematcsv) as csv_file:
			csv_reader = csv.reader(csv_file, dialect=csv.excel,delimiter=';')
			haku = input('Paikan nimi: ')
			kysely = False
			if haku.lower() == "x":
				break
			print('---------------------------------------------------')
			print('{: <3} {: <40} {: <7}'.format('nro','Sääasema','FMISID'))
			print('---------------------------------------------------')
			for row in csv_reader:
				tmp = row[0].lower().split()
				if tmp[0] == haku.lower():
					paikat.append(row)
					row[0] = row[0]
					vaihtoehdot += 1
					print('{: <3} {: <40} {: <7}'.format(vaihtoehdot,row[0],row[1]))
					kysely = True


		if kysely:
			print('---------------------------------------------------')
			value = input('Lisää numero: ')
			if value > str(0) and value <= str(vaihtoehdot):
				lisaaKantaan(paikat[int(value)-1])
			elif(value.lower() == "x"):
				break
			else:
				print('Numerolla ei löytynyt yhtään asemaa')
				loggeri(f'Hakuvirhe: {haku} {value} numeroa ei löytynyt')
		elif(vaihtoehdot == 0):
				print('Haulla ei löytynyt säähavaintoasemia\n')
				loggeri(f'Hakuvirhe: {haku} ei löytynyt havaintoasemia')

# kyselyt
value = input("haluatko muuttaa seurattavia paikkakuntia? (K)yllä / muuten ei: ")
if(value.lower() == "k"):
	print('Kirjoita "X" lopettaksesi paikkakuntien lisäämisen\n')
	syottoLuuppi()

value = input("haluatko hakea lämpötilatiedon ilmatieteenlaitokselta? (K)yllä / muuten ei: ")
if(value.lower() == "k"):
	lueKannasta()

f.close()

print('---------------------------------------------------')
value = input('sulje painamalla mitä tahansa näppäintä')