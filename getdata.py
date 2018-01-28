#This downloads all the packages with the string "scriptures" in the gospel library id name that are listed in Catalog.sqlite, and places them in a folder data.
'''
Prior to running this script:
    1) Get Catalog version number:  
       http://broadcast3.lds.org/crowdsource/mobile/gospelstudy/production/2.0.3/index.json
    2) Get catalog zip file
       http://broadcast3.lds.org/crowdsource/mobile/gospelstudy/production/2.0.3/catalogs/<CATALOG_VERSION>.zip
    3) Unzip the file.  The file "Catalog.sqlite" should result
    4) More detailed instructions at:  http://blog.crosswaterbridge.com/how-the-gospel-library-content-system-works/
'''

'''
Significant portions of this program were obtained from gospellibrary (https://github.com/CrossWaterBridge/python-gospel-library), requiring the following:

Copyright (c) 2015 Hilton Campbell

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
''' 

import requests
import sqlite3
import pdb
import sys
import os
from zipfile import ZipFile


sqlite_file = 'Catalog.sqlite'    # name of the sqlite database file
table_name = 'my_table_2'   # name of the table to be queried
id_column = 'my_1st_column'
some_id = 123456
column_2 = 'my_2nd_column'
column_3 = 'my_3rd_column'

# Connecting to the database file
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()

# 1) Contents of all columns for row that match a certain value in 1 column
#c.execute('SELECT * FROM {tn} WHERE {cn}="Hi World"'.\
        #format(tn=table_name, cn=column_2))
#c.execute('SELECT _id, external_id, title, latest_version FROM item WHERE language_id=1 ORDER BY _id LIMIT 5;')
c.execute('SELECT _id, external_id, title, latest_version FROM item WHERE language_id=1 ORDER BY _id;')
all_rows = c.fetchall()
#pdb.set_trace()
base_url='http://broadcast3.lds.org/crowdsource/mobile/gospelstudy/production/2.0.3/item-packages'
session = requests.Session()
try:
    from io import BytesIO
    Bytes = BytesIO
except ImportError:
    from StringIO import StringIO
    Bytes = StringIO

for database in all_rows:
   #print(database[3])
   #cmd="http://broadcast3.lds.org/crowdsource/mobile/gospelstudy/production/2.0.3/item-packages/<EXTERNAL_ID>/<ITEM_VERSION>.zip".format(database[1],database[3])
   cmd="http://broadcast3.lds.org/crowdsource/mobile/gospelstudy/production/2.0.3/item-packages/{0}/{1}.zip".format(database[1],database[3])
   #cmd="echo test"
   #os.system("{0}".format(cmd)) 
   catalog_zip_url = '{baseurl}/{dbname}/{dbversion}.zip'.format(baseurl=base_url, dbname=database[1],dbversion=database[3])
   catalog_path='data/{dbname}'.format(dbname=database[1])
   if (database[1].find("scriptures") != -1 ): #scriptures found (delete next line to get everything)
       print catalog_path
       r = session.get(catalog_zip_url)
       if r.status_code == 200:
           try: #os.makedirs(os.path.dirname(catalog_path))
               os.makedirs(catalog_path)
           except OSError:
               print 'failed to make ', os.path.dirname(catalog_path)
               pass
           with ZipFile(Bytes(r.content), 'r') as catalog_zip_file:
                #catalog_zip_file.extractall(os.path.dirname(catalog_path))
                catalog_zip_file.extractall(catalog_path)

# Closing the connection to the database file
conn.close()

