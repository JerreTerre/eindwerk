from time import sleep, gmtime, strftime
import io 
import pymysql
# Open database connection (IP, mysql naam, mysql paswoord, databasenaam)
conn = pymysql.connect(host='127.0.0.1', unix_socket='/var/run/mysqld/mysqld.sock', user='Smets', passwd='Thomas', db='CpuLog')
cur = conn.cursor()

try:
	#Tabel van database leeg maken
	cur.execute("TRUNCATE TABLE time")
	while True:
		#Temperatuur ophalen van CPU
		f = open("/sys/class/thermal/thermal_zone0/temp", "r")
		t = f.readline ()

		#string omvormen naar een integer
		g = int(t)
		temperature = g/1000

		#Printen temperatuur en tijd in Shell
		print(temperature)
		print (strftime("%Y-%m-%d %H:%M:%S"))

		#Tijd en temperatuur importeren in DB
		cur.execute("INSERT INTO time(time,value) VALUES (%s,%s)",(strftime('%Y-%m-%d %H:%M:%S',gmtime()),temperature))
		conn.commit()

		# %s betekend dat er naar de sql regel gezocht gaat worden voor variabelen die meegestuurd moeten worden
		# voorbeeld met 2 kolommen : cursor.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (42, 'bar'))
		sleep(1)

except:
	cur.close()
	conn.close()
