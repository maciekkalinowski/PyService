

from contextlib import nullcontext
#from binascii import rledecode_hqx
#from contextlib import nullcontext
from optparse import Values
from os.path import exists
import re

from urllib import response
from flask import jsonify, request, url_for
from flask import render_template, redirect, flash
from flask import Response



from .PyDB import createPyDB
from app.forms import entryForm, LoginForm, statsForm
from config import Config
import requests, json, datetime


from app import app
import os
import sqlite3


apiBasePath = '/api/PyService/v1'
basePath = '/PyService/v1'

#dataBaseFile = 'C:\\Flask\\PyService\\flask\\app\\PyDB.sqlite'
dataBaseFile = 'db/PyDB.sqlite'
#dataBaseFile = 'app\\PyDB.sqlite'
if not exists(dataBaseFile):
#if not os.path.isfile('PyDB.sqlite'):
    print ("Can't find database PyDB, creating one")
    createPyDB()
    print('Done')
else:
    print('Found a database: ' + dataBaseFile)


### CACHE ##################################################
#
class PyServiceCache():

    usersCache = []
    tagsCache = []

    def getUsersCache(self):
        return self.usersCache

    def getTagsCache(self):
        return self.tagsCache
    
    def refreshUsersCache(self):
        self.usersCache = []
        conn = sqlite3.connect(dataBaseFile)
        c = conn.cursor()
        usersTable = list(c.execute('SELECT * FROM users'))
        conn.close()
        
        for user in usersTable:
            self.usersCache.append(user[-1])
        print('Odswiezony cache usersCache')
        return self.usersCache

    def refreshTagsCache(self):
        self.tagsCache = []
        conn = sqlite3.connect(dataBaseFile)
        c = conn.cursor()
        tagsTable = list(c.execute('SELECT * FROM tags'))
        conn.close()
        
        for tag in tagsTable:
            self.tagsCache.append(tag[-1])
        print('Odswiezony cache tagsCache')
        return self.tagsCache

    def refreshCache(self):
        self.refreshUsersCache()
        self.refreshTagsCache()



cache = PyServiceCache()
cache.refreshCache()

#
### CACHE ##################################################


### FUNCTIONS  ##################################################
#

def tableToList(table):
    count = len(table)
    i = 0
    list = ''

    for i in range(count):
        if i < len(table) -1 : 
            list = list + table[i] + ','
        else:
            list = list + table[i]
    return list        

def tableToQuery(table):
    count = len(table)
    i = 0
    query = ''

    for i in range(count):
        if i < len(table) -1 : 
            query = query + '\'' + table[i] +'\'' + ','
        else:
            query = query + '\'' + table[i] + '\''
    return query  

#
### FUNCTIONS ##################################################

### TST ##################################################
#
@app.route(basePath + "/test")
def test():
    return render_template('test.html')
    #return "fsdfsdfsdfsd"

#
### TST ##################################################


### API ##################################################
#

#TAGS
@app.route(apiBasePath + "/tags", methods=['GET', 'POST'])
def tags():
    # Pobieranie listy tagow
    if request.method == 'GET':
        print('Pobieram liste tagow z bazy')
        conn = sqlite3.connect(dataBaseFile)
        c = conn.cursor()
        

        tagsTable = list(c.execute('SELECT * FROM tags'))
        conn.close()
        
        tags = []
        for row in tagsTable:
            tags.append(row[-1])
        print(tags)


        #print(tagsTable)
        
        apiResponse = jsonify(tags)

        return apiResponse
    
    
    # Dodanie nowego taga
    elif request.method == 'POST':
        requestBody  = request.get_json()
        requestTag = requestBody["tagName"]

        conn = sqlite3.connect(dataBaseFile)
        c = conn.cursor()

        c.execute('INSERT INTO tags VALUES (?, ?)', (None , requestTag))

        conn.commit()
        conn.close()
        print('Dodano nowy tag do bazy: ' + requestTag)
        return Response('OK', status=201, mimetype='application/json')
    


#ENTRIES
@app.route(apiBasePath + "/entries", methods=['GET', 'POST'])
def entries():
    # Pobieranie listy wpisow
    if request.method == 'GET':
        print('Pobieram liste wpisow z bazy')
        args = request.args.to_dict()
        authorsFlag = False
        tagsFlag = False
        valueMinFlag = False
        valueMaxFlag = False
        dateStartFlag = False
        dateEndFlag = False
        if 'authors' in args:
            authors = args["authors"].split(',')
            authorsFlag = True
        if 'tags' in args:
            tags = args["tags"].split(',')
            tagsFlag = True
        if 'valueMin' in args:
            valueMin = args["valueMin"]
            valueMinFlag = True
        if 'valueMax' in args:
            valueMax = args["valueMax"]
            valueMaxFlag = True
        if 'dateStart' in args:
            dateStart = args["dateStart"]
            dateStartFlag = True
        if 'dateEnd' in args:
            dateEnd = args["dateEnd"]
            dateEndFlag = True


        

        
        sqlWHERE = ' WHERE E.DATE BETWEEN ' + '\'' +  dateStart + ' 00:00:00' + '\'' + ' AND ' +'\'' + dateEnd + ' 23:59:59' +'\'' \
                     + ' AND E.VALUE BETWEEN ' + valueMin + ' AND ' + valueMax

        if authorsFlag:
            sqlWHERE = sqlWHERE + ' AND E.AUTHOR IN (' + tableToQuery(authors) + ')'
        if tagsFlag:
            sqlWHERE = sqlWHERE + ' AND ET.TAG_NAME IN (' + tableToQuery(tags) + ')'
        


        sql = 'SELECT E.ENTRY_ID, E.DATE, E.AUTHOR, E.VALUE, E.COMMENT FROM entries E JOIN entryTags ET ON E.ENTRY_ID = ET.ENTRY_ID' + sqlWHERE + ' GROUP BY E.ENTRY_ID'

        print(sql)
        
        conn = sqlite3.connect(dataBaseFile)
        c = conn.cursor()
        
        entriesTable =  list(c.execute(sql))
        #print(entriesTable)
        
        entryTagsTable =[]
        for row in entriesTable:
            sql = 'SELECT TAG_NAME FROM entryTags WHERE ENTRY_ID =' + str(row[0])
            print(sql)
            entryTagsTable.append(list(c.execute(sql)))         


        entryTagsTable2 = []

        for row in entryTagsTable:
            elems = []
            for elem in row:               
                elems.append(elem[0])
            entryTagsTable2.append(elems)

        print('Pobrano list wpisow z bazy')
        conn.close()

        entries = []
        i = 0
        for row in entriesTable:
            entry = {}
            entry["id"] = row[0]
            entry["date"] = row[1]
            entry["author"] = row[2]
            entry["value"] = row[3]
            entry["comment"] = row[4]
            entry["tags"] = entryTagsTable2[i] 
            entries.append(entry)
            i = i + 1

        
        apiResponse = jsonify(entries)

        return apiResponse
    
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
        if len(requestTags) > 0:
            for tag in requestTags:
                c.execute('INSERT INTO entryTags VALUES (?, ?, ?)', (None, lastEntryId, tag ))
        
        
        conn.commit()
        conn.close()
        print('Dodano nowy wpis')
        return Response('OK', status=201, mimetype='application/json')



@app.route(apiBasePath + "/entries/<entryId>", methods=['GET', 'POST'])
def entry(entryId):
    # Pobranie informacji o konkretnym wpisie
    if request.method == 'GET':
        conn = sqlite3.connect(dataBaseFile)
        c = conn.cursor()
        entry = list(c.execute('SELECT ENTRY_ID, DATE, AUTHOR, VALUE, COMMENT FROM entries WHERE ENTRY_ID = ?', [entryId]))   
        entryTags = list(c.execute('SELECT * FROM entryTags WHERE ENTRY_ID = ?', [entryId]))     
        conn.close()
        
        entryJ = {}
        entryJ["id"] = entry[0][0]
        entryJ["date"] = entry[0][1]
        entryJ["author"] = entry[0][2]
        entryJ["value"] = entry[0][3]
        entryJ["comment"] = entry[0][4]
        
        tags = []
        for tag in entryTags:
            tags.append(tag[-1])
        
        entryJ["tags"] = tags

        apiResponse = jsonify(entryJ)
        return apiResponse
        
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
        return Response(' ', status=201, mimetype='application/json')


#
### API ##################################################

### WEB ##################################################
#

#INDEX
@app.route(basePath + "/")
@app.route(basePath + "/index", methods=['GET', 'POST'])
def index():
    form = entryForm()


    tagsDict = []
    for tag in cache.getTagsCache():
        tagsDict.append((tag,tag))

    
    authorsDict = []
    for user in cache.getUsersCache():
        authorsDict.append((user, user))
    
    #form.author.choices = authorsDict
    
    form.tags.choices = tagsDict
    
    if form.validate_on_submit():
        value = request.form['value']
        #author = request.form['author']
        tags = []
        for key in request.form.keys():
            if 'tags' in key:
                #print('JEST tag: ' + key)
                tags.append(request.form[key])
        print(tags)
        if len(tags) == 0:
            tags.append('none')
        print(tags)
        requestBody = {}
        
        newTag = request.form["newTag"]
        if len(newTag) > 0:
            requestBody["tagName"] = newTag
            #print(requestBody)
            print('Dodaje nowy tag: ' + newTag)
            nt = requests.post('http://localhost:5000'+ apiBasePath +'/tags', json=requestBody)
            #print(nt.text)
            tags.append(newTag)
            cache.refreshTagsCache()   

        requestBody = {}
        
        requestBody['date'] = str(datetime.datetime.now())
        # zahardkodowany user noOne
        requestBody['author'] = authorsDict[0][0]
        requestBody['value'] = value
        requestBody['comment'] = request.form['comment']
        requestBody["tags"] = tags
        
        print('Dodaje nowy wpis: ')
        print(requestBody)
        r = requests.post('http://localhost:5000'+ apiBasePath +'/entries', json=requestBody)
        #print(r.text)
        return redirect(basePath +'/index')
    else:
        if len(form.errors) > 0:
            print(form.errors)

    return render_template('index.html', form=form )


#VIEW
@app.route(basePath + "/stats", methods=['GET', 'POST'])
def stats():

    params = statsForm()

    authorsDict = []
    for user in cache.getUsersCache():
        authorsDict.append((user, user))
    params.authors.choices = authorsDict

    tagsDict = []
    for tag in cache.getTagsCache():
        tagsDict.append((tag,tag))
    params.tags.choices = tagsDict


    if params.validate_on_submit():
        print('Wyszukiwanie: ')
        #print(request.form.to_dict())
        authors = []
        tags = []
        for key in request.form.keys():
            if 'authors' in key:
                authors.append(request.form.to_dict()[key])
            elif 'tags' in key:
                tags.append(request.form.to_dict()[key])
            


        valueMin = request.form.to_dict()['valueMin']
        valueMax = request.form.to_dict()['valueMax']
        dateStart = request.form.to_dict()['dateStart']
        dateEnd = request.form.to_dict()['dateEnd']


        print('Parametry wyszukiwnaia: AUTHORS: ' + str(authors) + ' TAGS: ' + str(tags) + ' VALUE_MIN: ' + str(valueMin) + ' VALUE_MAX: ' + str(valueMax) + ' DATE_START: ' + str(dateStart) + ' DATE_END ' + str(dateEnd))

        requestArgs = '?'
        if len(authors)>0:
            requestArgs = requestArgs + 'authors=' + tableToList(authors)

        if len(tags)>0:
            requestArgs = requestArgs + '&tags=' + tableToList(tags)

        requestArgs = requestArgs + '&valueMin=' + valueMin + '&valueMax=' + valueMax + '&dateStart=' + dateStart + '&dateEnd=' + dateEnd 

        entries = requests.get('http://localhost:5000'+ apiBasePath + '/entries' + requestArgs )


        #print('Zwrotka z API: ' + str(entries.json()))
        entriesJSON = entries.json()
        print('Wyniki wyszukiwania: ')
        print(entriesJSON)
        #return redirect(basePath +'/stats')
        return render_template('dbTables.html', entriesTable=entriesJSON )
    else:
        if len(params.errors) > 0:
            print(params.errors)

    return render_template('stats.html', params=params)



#LOGIN

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    #print('request')
    if form.validate_on_submit():
        #print('validated')
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/login')
    else:
        print('notValidated')
        print(form.errors)
    return render_template('login.html', title='Sign In', form=form)
#
### WEB ##################################################