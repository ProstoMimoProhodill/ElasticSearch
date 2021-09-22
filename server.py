import sqlite3
from sqlite3 import Error
from random import randint
from flask import Flask, jsonify, request
from elasticsearch import Elasticsearch
from operator import itemgetter

es = Elasticsearch('http://127.0.0.1:9200/')
app = Flask(__name__)

# Example: http://127.0.0.1:5000/search_text?keyword="my text"
@app.route('/search_text', methods=['GET'])
def search_text():
    con = sql_connection()
    body = {
        'from' : 0, 'size' : 20,
        'query': {
            'match': {
                'text': request.args.get('keyword')
            }
        }
    }
    # save indexes id
    res = es.search(index='index', body=body)
    id_indexes = res['hits']['hits']
    # sort by the DateTime
    data = []
    for i in range(len(id_indexes)):
        data.append(sql_get_by_id(con, id_indexes[i]['_id']))
    data = sorted(data, key=lambda k: k[3])
    # print from DB
    data_str = ""
    for i in range(len(data)):
        data_str += "<h2>{}</h2>".format(data[i])
    return data_str

# Example: http://127.0.0.1:5000/delete?id=2
@app.route('/delete', methods=['GET'])
def index():
    id = request.args.get('id')
    con = sql_connection()
    # Delete from DB
    sql_delete(con, id)
    # Delete from index
    es.delete(index='index', id=id)
    return "<h1>Deleted!</h1>"

def sql_connection():
    # connect to database
    try:
        con = sqlite3.connect('database.db')
    except Error:
        print(Error)
    # check table DATA | Exist - OK | Not Exist - Create
    cur = con.cursor()
    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='DATA'").fetchall()
    if tables == []:
        # DATA not exist - Create DATA
        cur.execute("CREATE TABLE DATA(id integer PRIMARY KEY, rubrics text, text text, created_date datetime default current_timestamp)")
        con.commit()
        #  Generate data
        generate_data(con)
    return con

def sql_get_by_id(con, id):
    cur = con.cursor()
    cur.execute('SELECT * FROM DATA WHERE id=?', (id, ))
    return cur.fetchall()[0]

def sql_insert(con, entities):
    cur = con.cursor()
    cur.execute('INSERT INTO DATA(rubrics, text) VALUES(?, ?)', entities)
    con.commit()

def sql_fetch(con):
    cur = con.cursor()
    cur.execute('SELECT * FROM DATA')
    rows = cur.fetchall()
    return rows

def sql_delete(con, id):
    cur = con.cursor()
    cur.execute('DELETE FROM DATA WHERE id=?', (id, ))
    con.commit()

def generate_data(con):
    # generate sql
    for i in range(30):
        var = ('VK-{0},VK-{1}'.format(randint(1, 1000), randint(500, 1000)), 'my text for testing database by number {0}'.format(randint(0, 1000)))
        sql_insert(con, var)
    # copy data from sql to elastic search
    sql_data = sql_fetch(con)
    for i in range(len(sql_data)):
        es.index(index='index', id=sql_data[i][0], body={'text': sql_data[i][2]})
