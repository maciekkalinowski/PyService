from asyncio.windows_events import NULL
from contextlib import nullcontext
#from binascii import rledecode_hqx
#from contextlib import nullcontext
from optparse import Values
from os.path import exists
from urllib import response
from flask import jsonify, request
from flask import render_template, redirect, flash
from flask import Response
from sqlalchemy import null
from .PyDB import createPyDB
from app.forms import entryForm, LoginForm
from config import Config
import requests, json, datetime


from app import app
import os
import sqlite3

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

### TST ##################################################
#TEST
@app.route("/test")
def test():
    testResponse = 'TEST TEST'
    return testResponse

#TEST2
@app.route("/test2")
def test2():
    r = requests.get('http://localhost:5000/'+apiBasePath+'/tags')
    print(r.json())
    #return 'fsdf'
    return render_template('getTags.html', tagsTable=r.json())
### TST ##################################################


### API ##################################################

#TAGS
@app.route(apiBasePath + "/tags", methods=['GET', 'POST'])
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

        #print(tagsTable)
        
        apiResponse = jsonify(tagsTable)
        #return Response(tagsTable, status=200, mimetype='application/json')
        return apiResponse
        #return render_template('getTags.html', tagsTable=tagsTable)
    
    
    # Dodanie nowego taga
    elif request.method == 'POST':
        requestBody  = request.get_json()
        requestTag = requestBody["tagName"]

        conn = sqlite3.connect(dataBaseFile)
        c = conn.cursor()

        c.execute('INSERT INTO tags VALUES (?, ?)', (None , requestTag))

        conn.commit()
        conn.close()
        return Response('OK', status=201, mimetype='application/json')


#ENTRIES
@app.route(apiBasePath + "/entries", methods=['GET', 'POST'])
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
        #print(entriesTable)
        apiResponse = jsonify(entriesTable)
        return apiResponse
        #return render_template('getEntries.html', entriesTable=entriesTable)
    
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
        
        entry = list(c.execute('SELECT * FROM entries WHERE ENTRY_ID = ?', (entryId)))        
        conn.close()
        #print(entry)
        apiResponse = jsonify(entry)
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
        return Response(null, status=201, mimetype='application/json')



### API ##################################################

### WEB ##################################################
#VIEW

@app.route(basePath + "/view")
def view():
    tags = requests.get('http://localhost:5000'+apiBasePath+'/tags')
    tagsJSON = tags.json()
    #print(tagsJSON)

    entries = requests.get('http://localhost:5000'+apiBasePath+'/entries')
    entriesJSON = entries.json()
    #print(entriesJSON)


    return render_template('dbTables.html', tagsTable=tagsJSON, entriesTable=entriesJSON )

#INDEX
@app.route(basePath + "/")
@app.route(basePath + "/index", methods=['GET', 'POST'])
def index():
    form = entryForm()
    if form.validate_on_submit():
        value = request.form['value']
        print('Entered value: ' + str(value))



        requestBody = {}
        
        requestBody['date'] = str(datetime.datetime.now())
        requestBody['author'] = 'noOne'
        requestBody['value'] = value
        requestBody['comment'] = ''
        requestBody["tags"] = []
        
        
        r = requests.post('http://localhost:5000'+apiBasePath+'/entries', json=requestBody)
        print(r.text)
        return redirect(basePath +'/index')
    else:
        if len(form.errors) > 0:
            print(form.errors)

    return render_template('index.html', form=form )




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