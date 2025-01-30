import os
import psycopg2

from dotenv import load_dotenv

conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"))

cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS users;')
cur.execute('CREATE TABLE users (id SERIAL NOT NULL,' 
                                'username VARCHAR(80) NOT NULL,'
                                'my_string VARCHAR(255) NOT NULL,'
                                'credentials BYTEA,'
                                'PRIMARY KEY (id),'
                                'UNIQUE (username));'
        )

conn.commit()

cur.close()
conn.close()