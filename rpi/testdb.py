import pyodbc
from datetime import datetime
server = 'airsensors.database.windows.net'
database = 'airsensorsdb'
username = ''
password = ''
driver = 'FreeTDS'
datestr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(datestr)
try:
  cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password + ';TDS_Version=8.0')
  cursor = cnxn.cursor()
  cursor.execute("INSERT INTO data (date_time, MQ2, MQ3, MQ4, MQ5, MQ6, MQ7, MQ8, MQ9, MQ135, MQ136, MQ137, MQ138) "+ "VALUES" + " ('" +datestr + "',2,2,2,2,2,2,2,2,2,2,2,2)")
  cnxn.commit()
except pyodbc.Error:
  print("err")
