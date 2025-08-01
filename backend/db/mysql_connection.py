import pymysql

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        passwd="Ylmzxfatih12355",
        database="stajDB",
        cursorclass=pymysql.cursors.DictCursor #sözlük formatında dönmesini sağlar.
        
    )
