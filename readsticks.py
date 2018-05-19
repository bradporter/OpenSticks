'''
Copyright 2018 Brad Porter 

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
 
from gi.repository import Gtk, Gdk, WebKit
import requests
import sqlite3
import pdb
import sys
import os
from zipfile import ZipFile
from bs4 import BeautifulSoup
import re
from unidecode import unidecode
import htmlToText

'''
#select database
list=os.system('ls data/_scripture*')
itemnum=0
for item in list:
    itemnum=itemnum+1
    print("%3d - %s" % (itemnum, item))

#wait for input
'''
#load all indexes

r = re.compile(r'^(\s*)', re.MULTILINE)
def prettify_2space(s, encoding=None, formatter="minimal"):
    return r.sub(r'\1\1\1\1\1\1\1\1', s.prettify(encoding, formatter))
    # http://stackoverflow.com/questions/15509397/custom-indent-width-for-beautifulsoup-prettify

def myprettify_2space(s, encoding=None, formatter="minimal"):
    def indentstr(n):
        str=''
        while n>0:
            str=str+'       '
            n-=1
        return str
            
    def loop(ss):
        print 'entered loop'
        index=0
        indent=0
        while(index>=0):
            p=ss[index:].find('<p')
            pc=ss[index:].find('</p>')
            d=ss[index:].find('<div')
            dc=ss[index:].find('</div>')
            a=[p,pc,d,dc]
            print a, max(a), max(a)==-1
            #pdb.set_trace()
            indexofminval=a.index(min(a))
            i=-1
            minval=len(ss)
            for val in a:
                i=i+1
                if val!=-1:
                    if val<minval:
                        minval=val
                        indexofminval=i
            dn=0
            pn=0
            if max(a)==-1: #end
                index=-1
            elif indexofminval==0:             # <p
                pn+=1
                index=index+p
                ss=ss[:index]+'\n'+indentstr(indent)+ss[index:]
                index=index+4+len(indentstr(indent))
                indent+=1
            elif indexofminval==1:            #  </p>
                pn-=1
                indent-=1
                index=index+pc
                ss=ss[:index]+'\n'+indentstr(indent)+ss[index:index+4]+'\n'+indentstr(indent)+ss[index+4:]
                index=index+8+len(indentstr(indent))
                #index=index+2
            elif indexofminval==2:            # <div
                dn+=1
                index=index+d
                ss=ss[:index]+'\n'+indentstr(indent)+ss[index:]
                index=index+6+len(indentstr(indent))
                indent+=1
            elif indexofminval==3:            # </div>
                dn-=1
                indent-=1
                index=index+dc
                ss=ss[:index]+'\n'+indentstr(indent)+ss[index:index+6]+'\n'+indentstr(indent)+ss[index+6:]
                index=index+10+len(indentstr(indent))
                #index=index+2

        print 'sssssss'
        return ss
        
    '''
    indent=0
    index=0
    divcount=0
    test=s.find('<div>') or s.find('<p>')
    while test:
        i2=s[index:].find('<div')
        if i2>0:  divcount+=1
        else: test=0
        index=index+i2
        print '<div>\'s = ',divcount
    index=0
    divcount=0
    test=1
    while test:
        i2=s[index:].find('</div>')
        if i2>0:  divcount+=1
        else: test=0
        index=index+i2
        print '</div>\'s = ', divcount
    index=0
    pcount=0
    test=1
    while test:
        i2=s[index:].find('<p')
        if i2>0:  pcount+=1
        else: test=0
        index=index+i2
        print '<p>\'s =', pcount
    index=0
    pcount=0
    test=1
    while test:
        i2=s[index:].find('</p>')
        if i2>0:  pcount+=1
        else: test=0
        index=index+i2
        print '</p>\'s =', pcount

    test=1
    index=0
    pdb.set_trace()
    '''
    print 'before loop'
    html=loop(s)
    return str(html)
    
#print htmlToText(html)
def getscripturebooks(mainbook,book):
       # find books with sqlite> select * from nav_collection; 
       if mainbook=='p':
          mainbook='pgp'
          switch= {
            "t": "title-page",
            'i': "introduction",
            'm': "moses",
            'a': 'abr',
            'jh': 'js-h',
            'jm': 'js-m',
            'af': 'a-of-f',
          }
          return mainbook, switch.get(book,'title-page')
       elif mainbook=='b':
          mainbook='bofm'
          switch= {
              't':'title-page',
              'i':'introduction',
              'n':'1-ne',
              'nn':'2-ne',
              'j':'jacob',
              'e':'enos',
              'jm':'jarom',
              'o':'omni',
              'w':'w-of-m',
              'm':'mosiah',
              'a':'alma',
              'h':'hel',
              'nnn':'3-ne',
              'nnnn':'4-ne',
              'mn':'morm',
              'er':'ether',
              'mi':'moro',
          }
          return mainbook, switch.get(book,'title-page')
       elif mainbook=='n':
          mainbook='nt'
          switch={
              'ma':'matt',
              'mar':'mark',
              'lu':'luke',
              'jo':'john',
              'ac':'acts',
              'ro':'rom',
              '1c':'1-cor',
              '2c':'2-cor',
              'ga':'gal',
              'ep':'eph',
              'ps':'philip',
              'phili':'philip',
              'co':'col',
              '1th':'1-thes',
              '2th':'2-thes',
              '1ti':'1-tim',
              '2ti':'2-tim',
              'ti':'titus',
              'pm':'philem',
              'phile':'philem',
              'he':'heb',
              'ja':'james',
              '1p':'1-pet',
              '2p':'2-pet',
              '1j':'1-jn',
              '2j':'2-jn',
              '3j':'3-jn',
              'ju':'jude',
              're':'rev',
          }
          return mainbook, switch.get(book,'matt')
       elif mainbook=='o':
          mainbook='ot'
          switch={
                  'ge':'gen',
                  'ex':'ex',
                  'le':'lev',
                  'nu':'num',
                  'de':'deut',
                  'jo':'josh',
                  'ju':'judg',
                  'ru':'ruth',
                  's':'1-sam',
                  'ss':'2-sam',
                  'k':'1-kgs',
                  'kk':'2-kgs',
                  'c':'1-chr',
                  'cc':'2-chr',
                  'ezr':'ezra',
                  'ne':'neh',
                  'es':'esth',
                  'jo':'job',
                  'ps':'ps',
                  'pr':'prov',
                  'ec':'eccl',
                  'so':'song',
                  'is':'isa',
                  'je':'jer',
                  'la':'lam',
                  'eze':'ezek',
                  'da':'dan',
                  'ho':'hosea',
                  'joe':'joel',
                  'am':'amos',
                  'ob':'obad',
                  'jon':'jonah',
                  'mi':'micah',
                  'na':'nahum',
                  'hab':'hab',
                  'ze':'zeph',
                  'hag':'hag',
                  'za':'zech',
                  'ma':'mal',
          }
          return mainbook, switch.get(book,'gen')
       elif mainbook=='d':
          mainbook='dc-testament'
          switch={
                  'd':'dc',
                  'o':'od',
                  }
          return mainbook, switch.get(book,'dc')

def volumeswitch(volume):
    switch={
            's':'scriptures',
            'hb':'handbook',
           }
    return switch.get(volume,'bofm')


def parseInputString(cmd):
    #parse input
    if cmd[0]=='/':
       cmds=cmd.split('/')
    if (cmds[1]=='ll'):
       # Connecting to the database file
       sqlite_file='Catalog.sqlite'
       try:
          conn = sqlite3.connect(sqlite_file)
       except:
          print "failed to connect"
          sys.exit()

       ##   !!!!  notdonehere

       c = conn.cursor()
       # 1) Contents of all columns for row that match a certain value in 1 column
       #c.execute('SELECT * FROM {tn} WHERE {cn}="Hi World"'.\
               #format(tn=table_name, cn=column_2))
       #c.execute('SELECT _id, external_id, title, latest_version FROM item WHERE language_id=1 ORDER BY _id LIMIT 5;')
       
    else:
        volume=volumeswitch(cmds[1])
        if(volume=='scriptures'):
            mainbook=volumeswitch(cmds[2])
            mainbook,book=getscripturebooks(cmds[2],cmds[3])
        if(volume=='handbook'):
            volume='handbook'
            #_handbook_handbook-2-administering-the-church_000
            mainbook='handbook-2-administering-the-church'
            book='title-page'
            chap=''

    try:
        chap=cmds[4]
    except:
        if book=='introduction' or book=='title-page':
           chap=''
        else:
           chap='1'
    try:
        sourcecode=cmds[5]
    except:
        sourcecode=False
    return volume, mainbook, book, chap, sourcecode

def getChapter_2col(volume,mainbook,db_id_ref,cmd):
    #todo   use same func for 2col and scroll ...   cmdParse(cmd)
    #cmd='/s/p/m/3'
    sourcecode=False
    if db_id_ref<0:
       #parse input
       volume, mainbook, book, chap, sourcecode = parseInputString(cmd)
       print volume, mainbook, book, chap

       # Connecting to the database file
    
    #sqlite_file = 'data/_scriptures_pgp_000/new.sqlite'    # name of the sqlite database file
    sqlite_file = 'data/_'+volume+'_'+mainbook+'_000/new.sqlite'    # name of the sqlite database file
    #sqlite_file = '../oldsrc/data/_'+volume+'_'+mainbook+'_000/new.sqlite'    # name of the sqlite database file
    print sqlite_file
    try:
       conn = sqlite3.connect(sqlite_file)
    except:
       print "failed to connect"
       sys.exit()

    c = conn.cursor()
    # 1) Contents of all columns for row that match a certain value in 1 column
    #c.execute('SELECT * FROM {tn} WHERE {cn}="Hi World"'.\
            #format(tn=table_name, cn=column_2))
    #c.execute('SELECT _id, external_id, title, latest_version FROM item WHERE language_id=1 ORDER BY _id LIMIT 5;')
    #c.execute('select content from subitem_content where subitem_id=1;')
    #chapter = c.fetchall()
    ##do nothing to title

    db_id=(db_id_ref)
    posthtml=''
    endpage=-1 #posthtml.find('</div></div></div></div>')
    while (endpage < 0):
        #find chapter end
        if db_id==-1:  #then we don't know the id yet
           if chap=='':
              db_chapstr='/'+volume+'/'+mainbook+'/'+book             # name of the sqlite database file
           else:
              db_chapstr='/'+volume+'/'+mainbook+'/'+book+'/'+chap    # name of the sqlite database file
           print db_chapstr
           c.execute('select _id from subitem where uri=\"%s\";' % (db_chapstr) )
           db_id=c.fetchone()  #a tuple of form (id,)
           db_id=db_id[0]
           db_id_ref=db_id
        c.execute('select * from subitem_content where subitem_id=%d;' % (db_id) )
        chapter = c.fetchone()
        for i, column in enumerate(c.description):
            name=column[0]
            if name in ['content_html','content']:
                chapterhtml=chapter[i]
        # Get and parse the chapter's HTML into a document
        '''
        doc=BeautifulSoup(chapterhtml,"html.parser")
        docp=(doc.prettify())

        print(doc.get_text())
        '''
        #need to find page end and only include up to that point
        try:
           posthtml=posthtml+chapterhtml
        except:
           print db_chapstr
           posthtml=posthtml+unidecode(unicode(chapterhtml,encoding="utf-8"))

        #endpage=posthtml.find('</div></div></div></div>')
        if endpage==-1:
           endpage=posthtml[0:].find('<!-- dblpgend -->')
        else:
           endpage=posthtml[endpage:].find('<!-- dblpgend -->')
        if endpage > 0:
            #move to end of div's
            #endpage=endpage+24
            endpage=endpage+17

        endhtml=posthtml[:endpage] #if endpage=-1 this will yield the whole st

        #chapn=int(chap)
        #chapn=chapn+1
        #chap='%d' % (chapn)
        db_id=db_id+1
        db_id_next=db_id

    #chap='%d' % (int(cmds[4])-1)
    #chap=chap-1
    db_id=(db_id_ref-1)
    db_id_prev=-1
    #if you find doublepg here, then the chapter must happen to start at top of doublepg
    startpage=endhtml.find('<div class=\"doublepg\"')
    if startpage==0:  pagehtml=endhtml
    while (startpage < 0):
        #find page start
        '''
        startpage=endhtml.find('<div class=\"doublepg\"')
        if db_id==-1:  #then we don't know the id yet
           db_chapstr='/'+volume+'/'+mainbook+'/'+book+'/'+chap    # name of the sqlite database file
           print db_chapstr
           c.execute('select _id from subitem where uri=\"%s\";' % (db_chapstr) )
           db_id=c.fetchone()
        '''
        #just grab it again instead of writing if's for first time through
        c.execute('select * from subitem_content where subitem_id=%d;' % (db_id) )
        chapter = c.fetchone()
        for i, column in enumerate(c.description):
            name=column[0]
            if name in ['content_html','content']:
                chapterhtml=chapter[i]
        # Get and parse the chapter's HTML into a document
        '''
        doc=BeautifulSoup(chapterhtml,"html.parser")
        docp=(doc.prettify())

        print(doc.get_text())
        '''
        prehtml=chapterhtml+endhtml
        #search backwards
        startpage=prehtml.rfind('<div class=\"doublepg\"')
        if startpage >=0:
            pagehtml=prehtml[startpage:]
            
        #chap='%d' % (int(chap)-1)
        db_id=db_id-1
        db_id_prev=db_id

    if db_id_prev==-1:  #we found a double page beginning withing db_id, so second "while" never reached.
        if db_id==1:  db_id_prev=1
        else: db_id_prev=1

    #pagehtml='<head> <link href=\"file:///media/brad/002C-270E/rsync/gospeldata/sticks.css\" rel=\"stylesheet\" type=\"text/css\" /  ></head> '+pagehtml
    pagehtml='<head> <link href=\"file:///home/brad/devel/gospeldata/src/sticks.css\" rel=\"stylesheet\" type=\"text/css\" /  ></head> '+pagehtml
    if sourcecode=='s':
       doc=BeautifulSoup(pagehtml,"html.parser")
       #docp=(doc.prettify())
       #docp=prettify_2space(doc)
       docp=myprettify_2space(str(doc))
       pagehtml='<plaintext>' + str(docp)


    # Closing the connection to the database file
    conn.close()

    '''
    #view.load_html_string(docp, '')
    f1=open('tmp.html','w')
    f1.write(docp.encode('utf-8'))
    f1.close()
    '''

    #f=open('tmpw.html','w')
    #f.write(chapterhtml)
    #f.close()
    #use the following for doublecol otherwise remove utf-8
    print "###############################################################"
    if sourcecode=='s':
       print str(pagehtml)
       return volume, mainbook, db_id_prev, db_id_next, str(pagehtml)
    else:
       print str(pagehtml.encode('utf-8'))
       return volume, mainbook, db_id_prev, db_id_next, str(pagehtml.encode('utf-8'))
    #return str(chapterhtml)

def getChapter_scroll(volume,mainbook,db_id_ref,cmd):
    #todo   use same func for 2col and scroll ...   cmdParse(cmd)
    #cmd='/s/p/m/3'
    sourcecode=False
    if db_id_ref<0:
       #parse input
       volume, mainbook, book, chap, sourcecode = parseInputString(cmd)
       print volume, mainbook, book, chap

    #sqlite_file = 'data/_scriptures_pgp_000/new.sqlite'    # name of the sqlite database file
    sqlite_file = 'data/_'+volume+'_'+mainbook+'_000/package.sqlite'    # name of the sqlite database file
    print sqlite_file
    try:
       conn = sqlite3.connect(sqlite_file)
    except:
       print "failed to connect"
       sys.exit()

    c = conn.cursor()
    pagehtml=''
    db_id=db_id_ref
    if(1):  #this is just here to match the while loop indentation in 2col
        if db_id==-1:  #then we don't know the id yet
           if chap=='':
              db_chapstr='/'+volume+'/'+mainbook+'/'+book             # name of the sqlite database file
           else:
              db_chapstr='/'+volume+'/'+mainbook+'/'+book+'/'+chap    # name of the sqlite database file
           print db_chapstr
           c.execute('select _id from subitem where uri=\"%s\";' % (db_chapstr) )
           db_id=c.fetchone()  #a tuple of form (id,)
           db_id=db_id[0]
           db_id_ref=db_id
        c.execute('select * from subitem_content where subitem_id=%d;' % (db_id) )
        chapter = c.fetchone()
        for i, column in enumerate(c.description):
            name=column[0]
            if name in ['content_html','content']:
                chapterhtml=chapter[i]

    pagehtml=pagehtml+str(chapterhtml)
    # 1) Contents of all columns for row that match a certain value in 1 column
    #c.execute('SELECT * FROM {tn} WHERE {cn}="Hi World"'.\
            #format(tn=table_name, cn=column_2))
    #c.execute('SELECT _id, external_id, title, latest_version FROM item WHERE language_id=1 ORDER BY _id LIMIT 5;')
    #c.execute('select content from subitem_content where subitem_id=1;')
    #chapter = c.fetchall()
    ##do nothing to title

    # Get and parse the chapter's HTML into a document
    '''
    doc=BeautifulSoup(chapterhtml,"html.parser")
    docp=(doc.prettify())

    print(doc.get_text())
    '''
    pagehtml='<head> <link href=\"file:///home/brad/devel/gospeldata/src/sticks.css\" rel=\"stylesheet\" type=\"text/css\" /  ></head> '+pagehtml
    if sourcecode=='s':
       doc=BeautifulSoup(chapterhtml,"html.parser")
       #docp=(doc.prettify())
       docp=prettify_2space(doc)
       pagehtml='<plaintext>'+docp
       #docp=prettify_2space(str(doc))
       #pagehtml='<plaintext>' + str(docp)



    # Closing the connection to the database file
    conn.close()


    '''
    #view.load_html_string(docp, '')
    f1=open('tmp.html','w')
    f1.write(docp.encode('utf-8'))
    f1.close()
    '''

    # Add gutter, h and v lines.  Best to do this here(?), rather than in the database, so it is flexible.
    #chapterhtml=chapterhtml.replace('<div class=\"rtpg\">','<div class=\"gutter\">&nbsp;&nbsp;</div><div class=\"rtpg\">',1)
    #chapterhtml=chapterhtml.replace('<div class=\"rtpg\">','<div"><img src="long_gutter.png" id="gutter"></div><div class=\"rtpg\">',1)

    #f=open('tmpw.html','w')
    #f.write(chapterhtml)
    #f.close()
    #use the following for doublecol otherwise remove utf-8
    #return str(chapterhtml.encode('utf-8'))
    print "###############################################################"
    db_id_prev=db_id-1
    db_id_next=db_id+1
    if sourcecode=='s':
       print (pagehtml)
       return volume, mainbook, db_id_prev, db_id_next, (pagehtml)
    else:
       #print str(pagehtml.encode('utf-8'))
       #return volume, mainbook, db_id_prev, db_id_next, str(pagehtml.encode('utf-8'))
       return volume, mainbook, db_id_prev, db_id_next, str(pagehtml)

#teststring='/s/b/n/2'
#ch=getChapter_2col('scriptures','bofm',5,teststring)
#print ch

'''
http://stackoverflow.com/questions/15509397/custom-indent-width-for-beautifulsoup-prettify
change prettify indent:

I actually dealt with this myself, in the hackiest way possible: by post-processing the result.

r = re.compile(r'^(\s*)', re.MULTILINE)
def prettify_2space(s, encoding=None, formatter="minimal"):
    return r.sub(r'\1\1', s.prettify(encoding, formatter))
Actually, I monkeypatched prettify_2space in place of prettify in the class. That's not essential to the solution, but let's do it anyway, and make the indent width a parameter instead of hardcoding it to 2:

orig_prettify = bs4.BeautifulSoup.prettify
r = re.compile(r'^(\s*)', re.MULTILINE)
def prettify(self, encoding=None, formatter="minimal", indent_width=4):
    return r.sub(r'\1' * indent_width, orig_prettify(self, encoding, formatter))
bs4.BeautifulSoup.prettify = prettify
So:

'''
#x = '''<section><article><h1></h1><p></p></article></section>'''
'''
soup = bs4.BeautifulSoup(x)
print(soup.prettify(indent_width=3))
'''
