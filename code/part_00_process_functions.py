# mike babb
# 2021 02 20
# functions used to find anagrams

# standard libraries
import datetime
import os
import pickle
import sqlite3

# external
import numpy as np
import pandas as pd

# helper function to save pickled objects
def save_pickle(file_path, file_name, obj):
    """ PICKLE (COMPRESS) A PYTHON OBJECT AND SERIALIZE TO DISK.
    """ 
    # https://docs.python.org/3/library/pickle.html#pickle.dump
    fpn = os.path.join(file_path, file_name)
    with open(fpn, 'wb') as f:
        pickle.dump(obj, f)    
        
    return None


def load_pickle(in_file_path, in_file_name):
    """ LOAD A PICKLED (COMPRESSED) OBJECT
    """     
    # https://docs.python.org/3/library/pickle.html#pickle.load
    fpn = os.path.join(in_file_path, in_file_name)
    with open(fpn, 'rb') as f:
        unpickled_object = pickle.load(f)

    return unpickled_object


def build_db_conn(db_path, db_name):    
    """ BUILD AND RETURN A SQLITE DATABASE CONNECTION
    """
    # https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection
    db_path_name = os.path.join(db_path, db_name)
    db_conn = sqlite3.connect(db_path_name)

    return db_conn


def query_db(sql, db_path, db_name, params = None ):
    """ QUERY A SQLITE DATABASE, RETURN A PANDAS DATAFRAME
    """
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_sql.html        
    db_conn = build_db_conn(db_path = db_path, db_name = db_name)
    
    s_time = datetime.datetime.now()
    
    df = pd.read_sql(sql = sql, con=db_conn, params = params)            
    db_conn.close()
    
    e_time = datetime.datetime.now()
    p_time = e_time - s_time
    p_time = p_time.total_seconds()
    print('...query execution took:', round(p_time, 7), 'seconds...')
    
    return df


def execute_sql_statement(sql, db_path, db_name):
    """ EXECUTE ARBITRATY SQL STATEMENTS AGAINST A DATABASE
    """
    # https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor
         
    # build connection and cursor objects
    db_conn = build_db_conn(db_path = db_path, db_name = db_name)
    db_cursor = db_conn.cursor()
        
    # execute the sql statement
    s_time = datetime.datetime.now()    
    db_cursor.execute(sql)
    db_conn.commit()
    
    e_time = datetime.datetime.now()
    p_time = e_time - s_time
    p_time = p_time.total_seconds()
    p_time = round(p_time, 7)
    print('...SQL execution took:', p_time, 'seconds.')
    
    # close connection objects
    db_cursor.close()
    db_conn.close()
    
    return None


if __name__ == '__main__':
    # simple test, query the first 10 words
    sql = 'select * from words limit 10;'
    db_path = '/project/finding_anagrams/db'
    db_name = 'words.db'
    df = query_db(sql = sql, db_path = db_path, db_name = db_name)
    print(df.head())