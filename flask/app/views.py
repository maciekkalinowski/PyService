from asyncio.windows_events import NULL
from contextlib import nullcontext
#from binascii import rledecode_hqx
#from contextlib import nullcontext
from optparse import Values
from os.path import exists
import re
from urllib import response
from flask import jsonify, request
from flask import render_template, redirect, flash
from flask import Response
from sqlalchemy import null


from .PyDB import createPyDB
from app.forms import entryForm, LoginForm, statsForm
from config import Config
import requests, json, datetime


from app import app
import os
import sqlite3

from app.cache import PyServiceCache

apiBasePath = '/api/PyService/v1'
basePath = '/PyService/v1'

dataBaseFile = 'C:\\Flask\\PyService\\flask\\app\\PyDB.sqlite'
#dataBaseFile = 'app\\PyDB.sqlite'
if not exists(dataBaseFile):
#if not os.path.isfile('PyDB.sqlite'):
    print ("Can't find database PyDB, creating one")
    createPyDB()
    print('Done')
else:
    print('Found a database: ' + dataBaseFile)


### CACHE ##################################################

conn = sqlite3.connect(dataBaseFile)
c = conn.cursor()

usersTable = list(c.execute('SELECT * FROM users'))

tagsTable = list(c.execute('SELECT * FROM tags'))


conn.close()
        
usersCached = []
for user in usersTable:
   usersCached.append(user[-1])

tagsCached = []
for tag in tagsTable:
   tagsCached.append(tag[-1])


cached = PyServiceCache()


'''
usersCached = []
tagsCached = []
def refreshCache(cacheName):
    usersCached = []
    tagsCached = []
    conn = sqlite3.connect(dataBaseFile)
    c = conn.cursor()
    if cacheName == 'users':
        usersTable = list(c.execute('SELECT * FROM users'))
        for user in usersTable:
            usersCached.append(user[-1])
        print('odswiezam cache usersCached')
        print(usersCached)

    elif cacheName == 'tags':
        tagsTable = list(c.execute('SELECT * FROM tags'))
        for tag in tagsTable:
            tagsCached.append(tag[-1])
        print('odswiezam cache tags')
        print(tagsCached)
    
    conn.close()

refreshCache('users')
refreshCache('tags')
'''

### CACHE ##################################################


### TST ##################################################


### TST ##################################################


### API ##################################################

#TAGS
@app.route(apiBasePath + "/tags", methods=['GET', 'POST'])
def tags():
    # Pobieranie listy tagow
    if request.method == 'GET':
        conn = sqlite3.connect(dataBaseFile)
        c = conn.cursor()
        
        #tagsTable = []
        #for row in c.execute('SELECT * FROM tags'):
        #    #print(row)
        #    tagsTable.append(row)
        tagsTable = list(c.execute('SELECT * FROM tags'))
        conn.close()
        
        tags = []
        for row in tagsTable:
            tags.append(row[-1])
        #print(tags)


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

        #refreshCache('tags')
        return Response('OK', status=201, mimetype='application/json')


#ENTRIES
@app.route(apiBasePath + "/entries", methods=['GET', 'POST'])
def entries():
    # Pobieranie listy wpisow
    if request.method == 'GET':
        conn = sqlite3.connect(dataBaseFile)
        c = conn.cursor()
        
        entriesTable =  list(c.execute('SELECT * FROM entries'))
        conn.close()

        entries = []
        for row in entriesTable:
            entry = {}
            entry["id"] = row[0]
            entry["date"] = row[1]
            entry["author"] = row[2]
            entry["value"] = row[3]
            entry["comment"] = row[4]
            entries.append(entry)

        

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
        #return "sfsdf"
        
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
        return Response(null, status=201, mimetype='application/json')



### API ##################################################

### WEB ##################################################


#INDEX
@app.route(basePath + "/")
@app.route(basePath + "/index", methods=['GET', 'POST'])
def index():

    form = entryForm()
    #tagsList = requests.get('http://localhost:5000'+apiBasePath+'/tags').json()
    tagsDict = []

    for tag in tagsCached:
        tagsDict.append((tag,tag))

    authorsDict = []
    for user in usersCached:
        authorsDict.append((user, user))
    
    form.author.choices = authorsDict

    
    #form.tags.choices = [('Biedronka', 'Biedronka'), ('Warzywniak', 'Warzywniak'), ('Castorama', 'Castorama')]
    form.tags.choices = tagsDict
    
    if form.validate_on_submit():
        value = request.form['value']
        author = request.form['author']
        tags = []
        for key in request.form.keys():
            if 'tags' in key:
                #print('JEST tag: ' + key)
                tags.append(request.form[key])
        
        requestBody = {}
        
        newTag = request.form["newTag"]
        if len(newTag) > 0:
            requestBody["tagName"] = newTag
            print(requestBody)
            nt = requests.post('http://localhost:5000'+ apiBasePath +'/tags', json=requestBody)
            print(nt.text)
            tags.append(newTag)   

        requestBody = {}
        
        requestBody['date'] = str(datetime.datetime.now())
        requestBody['author'] = author
        requestBody['value'] = value
        requestBody['comment'] = request.form['comment']
        requestBody["tags"] = tags
        
        
        r = requests.post('http://localhost:5000'+ apiBasePath +'/entries', json=requestBody)
        print(r.text)
        return redirect(basePath +'/index')
    else:
        if len(form.errors) > 0:
            print(form.errors)

    return render_template('index.html', form=form )


#VIEW

@app.route(basePath + "/view")
def view():
    tags = requests.get('http://localhost:5000'+apiBasePath+'/tags')
    tagsJSON = tags.json()
    #print(tagsJSON)

    entries = requests.get('http://localhost:5000'+apiBasePath+'/entries')
    entriesJSON = entries.json()
    print(entriesJSON)


    return render_template('dbTables.html', tagsTable=tagsJSON, entriesTable=entriesJSON )

@app.route(basePath + "/view/entry/<int:entryId>")
def viewEntry(entryId):
    print(entryId)
    entry = requests.get('http://localhost:5000'+apiBasePath+'/entries/' + str(entryId))
    entryJSON = entry.json()
    print(entryJSON)


    return render_template('entry.html', entry=entryJSON )



@app.route(basePath + "/stats")
def stats():

    params = statsForm()

    authorsDict = []
    for user in usersCached:
        authorsDict.append((user, user))
    
    params.authors.choices = authorsDict

    #tagsList = requests.get('http://localhost:5000'+apiBasePath+'/tags').json()
    tagsDict = []
    for tag in tagsCached:
        tagsDict.append((tag,tag))
    
    params.tags.choices = tagsDict

    return render_template('stats.html', params=params)



#LOGIN

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print('request')
    if form.validate_on_submit():
        print('validated')
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/login')
    else:
        print('notValidated')
        print(form.errors)
    return render_template('login.html', title='Sign In', form=form)
### WEB ##################################################