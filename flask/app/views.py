from asyncio.windows_events import NULL
#from binascii import rledecode_hqx
#from contextlib import nullcontext
from optparse import Values
from os.path import exists
from flask import request
from flask import render_template
from .PyDB import createPyDB

from app import app
import os
import sqlite3


dataBaseFile = 'C:\\Flask\\PyService\\flask\\app\\PyDB.sqlite'
#dataBaseFile = 'app\\PyDB.sqlite'
if not exists(dataBaseFile):
#if not os.path.isfile('PyDB.sqlite'):
    print ("Can't find database PyDB, creating one")
    createPyDB()
    print('Done')
else:
    print('Found a database: ' + dataBaseFile)


#INDEX
@app.route("/")
@app.route("/index")
def index():
    user = {'username': 'Maciek'}
    return render_template('index.html', title='Home', user=user)
    #return f"Hello from Flask"
#TEST
@app.route("/test")
def test():
    return f"TEST TEST"

#TAGS
@app.route("/tags", methods=['GET', 'POST'])
def tags():
    # Pobieranie listy tagow
    if request.method == 'GET':
        conn = sqlite3.connect(dataBaseFile)
        c = conn.cursor()
        
        tagsTable = []
        for row in c.execute('SELECT * FROM tags'):
            #print(row)
            tagsTable.append(row)
        
        conn.close()

        print(tagsTable)

        return render_template('getTags.html', tagsTable=tagsTable)
    
    
    # Dodanie nowego taga
    elif request.method == 'POST':
        requestBody  = request.get_json()
        requestTag = requestBody["tagName"]

        conn = sqlite3.connect(dataBaseFile)
        c = conn.cursor()

        c.execute('INSERT INTO tags VALUES (?, ?)', (None , requestTag))

        conn.commit()
        conn.close()
        return f'Dodano wpis do tabeli tags'


#ENTRIES
@app.route("/entries", methods=['GET', 'POST'])
def entries():
    # Pobieranie listy wpisow
    if request.method == 'GET':
        conn = sqlite3.connect(dataBaseFile)
        c = conn.cursor()
        
        entriesTable = []
        for row in c.execute('SELECT * FROM entries'):
            #print(row)
            entriesTable.append(row)
        
        conn.close()
        print(entriesTable)
 
        return render_template('getEntries.html', entriesTable=entriesTable)
    # Dodanie nowego wpisu
    elif request.method == 'POST':
        requestBody  = request.get_json()
        requestDate = requestBody['date']
        requestAuthor = requestBody['author']
        requestValue = str(requestBody['value'])
        requestComment = requestBody['comment']
        requestTags = requestBody["tags"]

        conn = sqlite3.connect(dataBaseFile)
        c = conn.cursor()
        # Dodanie wpisu do tabeli entries
        c.execute('INSERT INTO entries VALUES (?, ?, ?, ?, ?)', (None , requestDate, requestAuthor, requestValue, requestComment))
        # pobranie identyfikatora ostatniego wpisu
        lastEntryId = list(c.execute('SELECT ENTRY_ID FROM entries ORDER BY ENTRY_ID DESC LIMIT 1'))[0][0]

        # Dodanie wpisu do tabeli entryTags dla kazdego tagu we wpisie
        for tag in requestTags:
            c.execute('INSERT INTO entryTags VALUES (?, ?, ?)', (None, lastEntryId, tag ))
        
        
        conn.commit()
        conn.close()
        
        return f'Dodano wpis do bazy'



@app.route("/entries/<entryId>", methods=['GET', 'POST'])
def entry(entryId):
    # Pobranie informacji o konkretnym wpisie
    if request.method == 'GET':
        conn = sqlite3.connect(dataBaseFile)
        c = conn.cursor()
        
        entry = list(c.execute('SELECT * FROM entries WHERE ENTRY_ID = ?', (entryId)))
        print(entry)
        
        conn.close()
        return f'Wywolano metode GET'
    # Edycja istniejacego wpisu
    elif request.method == 'POST':
        conn = sqlite3.connect(dataBaseFile)
        c = conn.cursor()
        requestBody = request.get_json()
        newAuthor = requestBody["author"]
        newValue = requestBody["value"]
        newComment = requestBody["comment"]
        newTags = requestBody["tags"]
        
        c.execute('UPDATE entries SET author=?, value=?, comment=? WHERE ENTRY_ID=?', (newAuthor, newValue, newComment, entryId))
        entry = list(c.execute('SELECT * FROM entries WHERE ENTRY_ID = ?', (entryId)))
        
        conn.commit()
        conn.close()
        return f'Wywolano metode POST /entries/{entryId}'