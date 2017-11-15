#!/usr/bin/python3
import sqlite3

conn = sqlite3.connect('example.db')
c = conn.cursor()

c.execute('''drop table if exists students''')
c.execute('''CREATE TABLE students(name text, uni text)''')
c.execute('''insert into students values('Luke','UNSW')''')
c.execute('''insert into students values('Chris','UIUC')''')
conn.commit
c.execute('''SELECT * FROM students''')
for row in c:
    print('{0} : {1}'.format(row[0], row[1]))
conn.close
