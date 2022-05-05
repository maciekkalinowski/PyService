import sqlite3

def createPyDB():
	#conn = sqlite3.connect('C:\\Flask\\PyService\\flask\\app\\PyDB.sqlite')
	conn = sqlite3.connect('PyDB.sqlite')
	c = conn.cursor()



	# Utwórz tabelę tags
	c.execute('''
	CREATE TABLE "tags" (
		"ID"	INTEGER PRIMARY KEY,
		"TAG_NAME"	TEXT NOT NULL UNIQUE)
		''')

	# Utwórz tabelę users
	c.execute('''
	CREATE TABLE "users" (
		"ID"	INTEGER PRIMARY KEY,
		"USER_NAME"	TEXT NOT NULL UNIQUE)
		''')

	# Utwórz tabelę entries
	c.execute('''
	CREATE TABLE "entries" (
		"ENTRY_ID"	INTEGER PRIMARY KEY,
		"DATE"	TIMESTAMP NOT NULL,
		"AUTHOR"	TEXT,
		"VALUE"	REAL NOT NULL,
		"COMMENT" TEXT)
	''')

	# Utwórz tabelę entryTags
	c.execute('''
	CREATE TABLE "entryTags" (
		"ID"	INTEGER PRIMARY KEY,
		"ENTRY_ID"	INTEGER NOT NULL,
		"TAG_NAME"	TEXT NOT NULL,
	FOREIGN KEY(ENTRY_ID) REFERENCES entries(ENTRY_ID),
	FOREIGN KEY(TAG_NAME) REFERENCES tags(TAG_NAME)
	)
	''')
	# Wlacznie obslugi foreign keys
	c.execute('PRAGMA foreign_keys = ON')

	# Zamknięcie połączenia z bazą danych
	conn.close()