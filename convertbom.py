'''
Copyright 2018 Brad Porter

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import requests
import sqlite3
import pdb
import sys
import os
import shlex
from zipfile import ZipFile
from bs4 import BeautifulSoup

keyfile=open('bomconv.txt','r')
id=0;
db_id_order=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
#read from this file
sqlite_file = 'data/_scriptures_bofm_000/package.sqlite'    # name of the sqlite database file
#write to this file (assumes new.sqlite exists as copied from package.sqlite, though recopying is not necessary)
newsqlite_file = 'data/_scriptures_bofm_000/new.sqlite'    # name of the sqlite database file

leftpg_left='</div><div class=\"leftpg-left\">'
leftpg_rt='</div><div class=\"leftpg-rt\">'
rtpg_left='</div><div class=\"rtpg-left\">'
rtpg_rt='</div><div class=\"rtpg-rt\">'

# Connecting to the new database file
try:
   newconn = sqlite3.connect(newsqlite_file)
except:
   print "failed to connect to newsqlite_file"
   sys.exit()

cnew = newconn.cursor()

# Connecting to the old database file
try:
   conn = sqlite3.connect(sqlite_file)
except:
   print "failed to connect to sqlite_file"
   sys.exit()

c = conn.cursor()
# 1) Contents of all columns for row that match a certain value in 1 column
#c.execute('SELECT * FROM {tn} WHERE {cn}="Hi World"'.\
        #format(tn=table_name, cn=column_2))
#c.execute('SELECT _id, external_id, title, latest_version FROM item WHERE language_id=1 ORDER BY _id LIMIT 5;')
#c.execute('select content from subitem_content where subitem_id=1;')
#chapter = c.fetchall()
##do nothing to title

c.execute('select * from subitem_content where subitem_id=5;')
chapter = c.fetchone()
for i, column in enumerate(c.description):
    name=column[0]
    if name in ['content_html','content']:
        chapterhtml=chapter[i]
# Get and parse the chapter's HTML into a document
#print(chapterhtml)
#remove all divs: 
doc=BeautifulSoup(chapterhtml,"html.parser")
#docp=(doc.prettify())
docp=str(chapterhtml)
for line in keyfile:
    # http://stackoverflow.com/questions/743806/split-string-into-a-list-in-python
    keys=shlex.split(line)
    print keys
    if (keys[0]=='titlepage' or keys[0]=='ch' or keys[0]=='intro'):
       id=id+1
       try:
           db_id=db_id_order[id]
       except:  #assume order continues with +1
           db_id=db_id+1
       print 'id=',id, '     db_id=',db_id
       print (keys[0]=='titlepage' , keys[0]=='ch' , keys[0]=='intro')
       if keys[0]=='ch':
           chapternum=keys[1]
        #if chapternum=='6':
        #    pdb.set_trace()
       c.execute('select content from subitem_content where subitem_id=%d;' % (db_id))
       chapter = c.fetchone()
       for i, column in enumerate(c.description):
            name=column[0]
            if name in ['content_html','content']:
                chapterhtml=chapter[i]
       docp=str(chapterhtml)
       #pdb.set_trace()
       index=0
    elif (keys[0][0]=='#'):
       print 'comment: ', keys
    elif (keys[0]=='illustrations'):
       id=id+1  #we're not going to do anything with these yet in the bofm
    elif (keys[0]=='rplc' or keys[0]=='lplc' or keys[0]=='ccc'):
        # end rpl and end bodyBlock and end column
        try:
           i1=docp[index:].find(keys[1])
           docp=docp[:index]+docp[index:].replace(keys[1],keys[1]+'</div></div></div>',1)
        except:
           i1=0
           docp=docp[:index]+'</div></div></div>'+docp[index:]
        if i1==-1:  print 'err in rplc or lplc or ccc'; sys.exit()
        i2=docp[index+i1:].find('</div></div></div>')
        index=index+i1+i2+18
    elif (keys[0]=='lprc' or keys[0]=='cccc'):
        # end bodyBlock, column, lpr, and page
        try:
           i1=docp[index:].find(keys[1])
           docp=docp[:index]+docp[index:].replace(keys[1],keys[1]+'</div></div></div></div>',1)
        except:
           i1=0
           docp=docp[:index]+'</div></div></div></div>'+docp[index:]
        if i1==-1:  print 'err in lprc or cccc'; sys.exit()
        i2=docp[index+i1:].find('</div></div></div></div>')
        index=index+i1+i2+24
    elif (keys[0]=='rprc' or keys[0]=='ccccc'):
        # end bodyBlock, column, rpr, page, and doublepg
        try:
           i1=docp[index:].find(keys[1])
           docp=docp[:index]+docp[index:].replace(keys[1],keys[1]+'</div></div></div></div></div><!-- dblpgend -->',1)
        except:
           i1=0
           docp=docp[:index]+'</div></div></div></div></div><!-- dblpgend -->'+docp[index:]
        if i1==-1:  print 'err in rprc or ccccc'; sys.exit()
        i2=docp[index+i1:].find('</div></div></div></div></div><!-- dblpgend -->')
        index=index+i1+i2+47
    elif (keys[0]=='dblpgend'):
        # end bodyBlock, column, rpr, page, and doublepg
        try:
           i1=docp[index:].find(keys[1])
           docp=docp[:index]+docp[index:].replace(keys[1],keys[1]+'<!-- dblpgend -->',1)
        except:
           i1=0
           docp=docp[:index]+'<!-- dblpgend -->'+docp[index:]
        if i1==-1:  print 'err in dblpgend'; print ' keys[1]=',keys[1]; sys.exit()
        i2=docp[index+i1:].find('<!-- dblpgend -->')
        index=index+i1+i2+17
    elif (keys[0]=='hc' or keys[0]=='rprhc' or keys[0]=='rplhc' or keys[0]=='lprhc' or keys[0]=='lplhc'):
        # end header and column (header ends with </p>, not /div, so just close column with /div)
        i1=docp[index:].find(keys[1])
        if i1==-1:  print 'err in hc'; sys.exit()
        docp=docp[:index]+docp[index:].replace(keys[1]+'</p>',keys[1]+'</p>' + '</div></div>',1)
        #double /div
        i2=docp[index+i1:].find('</div></div>')
        index=index+i1+i2+12
        # remember
        # if end of heading is at end of column, add some extra c's for special case
    elif (keys[0]=='c'):
        try:
           if (db_id==9):
               pdb.set_trace()
           i1=docp[index:].find(keys[1])
           docp=docp[:index]+docp[index:].replace(keys[1],keys[1] + '</div>',1)
        except:
           i1=0
           docp= docp[:index] + '</div>' + docp[index:]
        if i1==-1:  print 'err in c'; sys.exit()
        i2=docp[index+i1:].find('</div>')
        index=index+i1+i2+6
        print 'i1=',i1,' i2=',i2,'  index=',index,'  index->',docp[index:index+25]
    elif (keys[0]=='pc'):
        try:
           i1=docp[index:].find(keys[1])
           docp=docp[:index]+docp[index:].replace(keys[1],keys[1] + '</p>',1)
        except:
           i1=0
           docp= docp[:index] + '</p>' + docp[index:]
        if i1==-1:  print 'err in pc'; sys.exit()
        i2=docp[index+i1:].find('</p>')
        index=index+i1+i2+4
        print 'i1=',i1,' i2=',i2,'  index=',index,'  index->',docp[index:index+25]
    elif (keys[0]=='cc'):
        #i1=docp[index:].find(keys[1])
        #docp=docp[:index]+docp[index:].replace(keys[1],keys[1] + '</div></div>',1)
        i1=0
        docp=docp[:index] + '</div></div>' + docp[index:]
        #i2=docp[:index+i1].find('</div></div>')
        i2=0
        index=index+i1+i2+12
        print 'i1=',i1,' i2=',i2,'  index->',docp[index:index+25]
    elif (keys[0]=='e'):  #use 'e' for ending prior to close of double page (most of the time)
        #replace div from <div type=chapter ... and bodyBlock which has already been closed
        #docp=docp[:index]+docp[index:].replace('</div></div>','<!-- /div --><!-- /div -->',1)
        #c.execute('update content from subitem_content where subitem_id=%d;' % (db_id))
        cnew.execute("update subitem_content_fts_content set c1content=\'%s\' where c0subitem_id=%d;" % (docp,db_id))
    elif (keys[0]=='ec'):  #use 'ec' for ending chapter at close of double page (rare)
        # in this case, we leave one trailing div to close the doublepg
        docp=docp[:index]+docp[index:].replace('</div>','<!-- /div -->')
        #c.execute('update content from subitem_content where subitem_id=%d;' % (db_id))
        cnew.execute("update subitem_content_fts_content set c1content=\'%s\' where c0subitem_id=%d;" % (docp,db_id))
    elif (keys[0]=='lp'):
        #need three div levels
        docp=docp[:index]+'<div class=\"doublepg\"><div class=\"leftpg\">' + docp[index:]
        i2=docp[index:].find('leftpg')
        index=index+i2+8
    elif (keys[0]=='rp'):
        #need three div levels
        docp=docp[:index] + '<div class=\"rtpg\">' + docp[index:]
        i2=docp[index:].find('rtpg')
        index=index+i2+6
    elif (keys[0]=='lpl'):
        #need three div levels
        docp=docp[:index] + '<div class=\"leftpg-left\">' + docp[index:]
        i2=docp[index:].find('leftpg-left')
        index=index+i2+13
    elif (keys[0]=='lpr'):
        #close lpl and open lpr
        docp= docp[:index] + '<div class=\"leftpg-rt\">' + docp[index:]
        i2=docp[index:].find('leftpg-rt')
        index=index+i2+11
    elif (keys[0]=='rpl'):
        #close lpr, close leftpg,  and open rpl
        docp= docp[:index] + '<div class=\"rtpg-left\">' + docp[index:]
        i2=docp[index:].find('rtpg-left')
        index=index+i2+11
    elif (keys[0]=='rpr'):
        #close rpl,  and open rpr
        docp= docp[:index] + '<div class=\"rtpg-rt\">' + docp[index:]
        i2=docp[index:].find('rtpg-rt')
        index=index+i2+9
    elif (keys[0]=='po'):
        #
        docp= docp[:index] + '<p>' + docp[index:]
        print ' index=',index,'  index->',docp[index-10:index+45]
    elif (keys[0]=='bb'):
        #
        docp= docp[:index] + '<div class=\"bodyBlock\">' + docp[index:]
        index=index+23
        print ' index=',index,'  index->',docp[index-10:index+45]
    elif (keys[0]=='colb'):
        #
        docp= docp[:index] + '<div class=\"column\"><div class=\"bodyBlock\">' + docp[index:]
        index=index+43
        print ' index=',index,'  index->',docp[index-10:index+45]
    elif (keys[0]=='col'):
        #
        docp= docp[:index] + '<div class=\"column\">' + docp[index:]
        index=index+20
    elif (keys[0]=='dblcol'):
        #
        docp= docp[:index] + '<div class=\"doublecolumn\">' + docp[index:]
        index=index+26
    elif (keys[0]=='lplh'):
        #need three div levels
        docp=docp[:index] + '<div class=\"leftpg-left\"><div class=\"column\">' + docp[index:]
    elif (keys[0]=='lprh'):
        #close lpl and open lpr
        docp= docp[:index] + '<div class=\"leftpg-rt\"><div class=\"column\">' + docp[index:]
    elif (keys[0]=='rplh'):
        #close lpr, close leftpg,  and open rpl
        docp= docp[:index] + '<div class=\"rtpg-left\"><div class=\"column\">' + docp[index:]
    elif (keys[0]=='rprh'):
        #close rpl,  and open rpr
        docp= docp[:index] + '<div class=\"rtpg-rt\"><div class=\"column\">' + docp[index:]
    elif (keys[0]=='bb'):
        docp= docp[:index] + '<div class=\"bodyBlock\">' + docp[index:]
        #closing class=chapter
        docp=docp.replace('<div class=\"bodyBlock\">', \
                          '</div><!-- div class=\"bodyBlock\" -->',1)
        i2=docp[index:].find('bodyBlock')
        index=index+i2+14
    elif (keys[0]=='he'):  #header end
        #closing class=chapter
        #docp=docp.replace('<div class=\"bodyBlock\">', \
                          #'</div><!-- div class=\"bodyBlock\" -->',1)
        docp=docp.replace('<div class=\"bodyBlock\">', \
                          '<!-- div class=\"bodyBlock\"-->',1)
        i2=docp[index:].find('bodyBlock\"-->')
        index=index+i2+13
        print ' i2=',i2,' index=',index,'  index->',docp[index:index+25]
    elif (keys[0]=='fr'):
        if (db_id==9):
            pdb.set_trace()
        docp=docp[index:].replace(keys[1], keys[2], 1)
        i2=docp[index:].find(keys[2])
        #make adjustment to index
        try:
            offset=int(keys[3])
        except:
            offset=0
        index=index+i2+len(keys[2])+offset
    elif (keys[0]=='f'):
        i2=docp[index:].find(keys[1])
        index=index+i2
    elif (keys[0]=='fskip' or keys[0]=='s'):
        i2=docp[index:].find(keys[1])
        index=index+i2+len(keys[1])
        print 'length of keys1 in fskip = ', len(keys[1])
    elif (keys[0]=='fplb'):
        #old
        #docp='<div class=\"doublepg\"><div class=\"fullpgleftblank\"> blank page </div>'+docp
        #index=docp.find('blank page ')+17
        #new
        docp='<div class=\"doublepg\"><div class=\"leftpg\"><div class=\"leftpg-left\"><div class=\"column\"> blank page </div></div><div class=\"leftpg-rt\"><div class=\"column\"> blank page </div></div></div>'+docp
    elif (keys[0]=='fpl'):
        docp=docp[:index] + '<div class=\"doublepg\"><div class=\"leftpg\">' + docp[index:]
        docp=docp+'</div><!-- end fullpg -->'
        i2=docp[index:].find('end fullpg')
        index=index+i2+14
    elif (keys[0]=='fpr'):
        docp=docp[:index] + '<div class=\"rtpg\">' + docp[index:]
        docp=docp+'</div></div><!-- end fullpg -->'
        i2=docp[index:].find('end fullpg')
        index=index+i2+14
    elif (keys[0]=='fullwidthrt' or keys[0]=='fwrt'):  #always at beginning of pg? no
        #this might want to go inside the heading and/or chapter divs
        #docp=docp[:index] + '</div class=\"fullwidth\">' + docp[index:]
        try:
           i1=docp[index:].find(keys[1])
           docp=docp[:index]+docp[index:].replace(keys[1],keys[1]+'<div class=\"fullwidthrt\">',1)
        except:
           i1=0
           docp= docp[:index] + '<div class=\"fullwidthrt\">' + docp[index:]
        if i1==-1:  print 'err in fullwidthrt'; sys.exit()
        i2=docp[index+i1:].find('fullwidthrt')
        index=index+i1+i2+13
    elif (keys[0]=='fullwidthleft' or keys[0]=='fwleft'):  #always at beginning of pg? no
        #this might want to go inside the heading and/or chapter divs
        #docp=docp[:index] + '</div class=\"fullwidth\">' + docp[index:]
        try:
           i1=docp[index:].find(keys[1])
           docp=docp[:index]+docp[index:].replace(keys[1],keys[1]+'<div class=\"fullwidthleft\">',1)
        except:
           i1=0
           docp= docp[:index] + '<div class=\"fullwidthleft\">' + docp[index:]
        if i1==-1:  print 'err in fullwidthleft'; sys.exit()
        i2=docp[index+i1:].find('fullwidthleft')
        index=index+i1+i2+15
    elif (keys[0]=='fullwidthend'):
        try:
           i1=docp[index:].find(keys[1])
           docp=docp[:index]+docp[index:].replace(keys[1],keys[1]+'</div>',1)
        except:
           i1=0
           docp= docp[:index] + '</div>' + docp[index:]
        if i1==-1:  print 'err in fullwidthend'; sys.exit()
        i2=docp[index+i1:].find('</div>')
        index=index+i1+i2+6
    elif (keys[0]=='facs2'):
        db_id2=17
        c.execute('select content from subitem_content where subitem_id=%d;' % (db_id2))
        chapter = c.fetchone()
        for i, column in enumerate(c.description):
             name=column[0]
             if name in ['content_html','content']:
                 chapterhtml=chapter[i]
        docp2=str(chapterhtml)
        index2=1
        docp2='<div class=\"doublepg\"><div class=\"fullpgleft\">' + docp2
        docp2=docp2.replace('</img></a>','</img></a></div></div></div><div class=\"fullpgrt\">',1)
        #index2=docp2.find('pgrt')
        #docp2=docp2[:index]+docp2[index:].replace('</div>','<!-- /div -->,1)
        docp=docp[:index]+docp2+docp[index:]
        index=docp.find('give at the present time.')
        i2=docp[index:].find('div>')
        index=index+i2+4
        i2=docp[index:].find('div>')
        index=index+i2+4
    elif (keys[0]=='facs3'):
        db_id2=18
        c.execute('select content from subitem_content where subitem_id=%d;' % (db_id2))
        chapter = c.fetchone()
        for i, column in enumerate(c.description):
             name=column[0]
             if name in ['content_html','content']:
                 chapterhtml=chapter[i]
        docp2=str(chapterhtml)
        index2=1
        docp2='<div class=\"fullpgrt\">' + docp2
        docp2=docp2+'</div></div><!-- endfacs3 -->'
        #docp2=docp2[:index]+docp2[index:].replace('</div>','<!-- /div -->,1)
        docp=docp[:index]+docp2+docp[index:]
        index=docp.find('endfacs3')+12
    #best to do this just before closing, but can leave for debug.
    #if you use the next lines, it will write to the file even if there is an error later, otherwise not.
    try:
      cnew.execute("update subitem_content_fts_content set c1content=\'%s\' where c0subitem_id=%d;" % (docp,db_id))
      newconn.commit() #commit changes
    except:
      print 'end if'
      # nothing


'''
#close off chapter identifier div at the end of the chapter summary and remove the bodyBlock div
docp=docp.replace('<div class=\"bodyBlock\">','</div><!-- div class=\"bodyBlock\" -->',1)
index=docp.find('bodyBlock')
i2=docp[index:].find('spiritually\n')
index=index+i2
i2=docp[index:].find(', before')
index=index+i2
docp=docp[:index]+docp[index:].replace(',',',{:s}'.format(rtpg_rt),1)
i2=docp[index:].find('for signs, and')
index=index+i2
docp=docp[:index]+docp[index:].replace('for signs, and','for signs, and{:s}'.format(leftpg_left),1)
i2=docp[index:].find('ground I, the')
index=index+i2
docp=docp[:index]+docp[index:].replace('ground I, the','ground I, the{:s}'.format(leftpg_rt),1)
i2=docp[index:].find('</div>')  #skip this one, since you just added it
index=index+i2
i2=docp[index:].find('</div>')
index=index+i2
docp=docp[:index]+docp[index:].replace('</div>','<!-- /div -->')  #replace two trailing div's
#now commit new docp to database.  Give it a new name.
#print docp
#makes error
#c.execute('update subitem_content set content={:s} where subitem_id=5;'.format(docp.encode('utf-8')))
#conn.commit()
'''


#print(doc.get_text())




# Closing the connection to the database file
newconn.commit() #commit changes
newconn.close()
conn.close()
