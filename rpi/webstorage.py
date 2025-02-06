from azure.storage.fileshare import ShareFileClient
from datetime import datetime
import time
import sys
import os

filename = datetime.now().strftime("%m-%d-%Y")+".csv"

connection_string = "DefaultEndpointsProtocol=https;AccountName=airsensorstorage;AccountKey=LFsKI/91D3oxuSrcUDXqwV4XGhSZYhM/d0zR83KZkvYVFh2nxlAUHQVHstUQ3o33TTki2+wuWqdu+AStyO/ViA==;EndpointSuffix=core.windows.net"
service = ShareFileClient.from_connection_string(conn_str=connection_string,share_name = "gassensortest", file_path = filename )
#if file does not exist yet, create it.
if os.path.isfile("gasanalyzerdata/"+filename) == False:
      f = open("gasanalyzerdata/"+filename,'x')
      f.write("Timestamp,MQ-5,MQ-3,MQ-136,MQ-137,MQ-4,MQ-2,MQ-135,MQ-6,MQ-9,MQ-138,MQ-8,MQ-7\n")
      f.flush()
      f.close
      
time.sleep(1)
with open("gasanalyzerdata/"+filename, "rb") as source_file:
    service.upload_file(source_file)
source_file.close