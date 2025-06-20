#!/usr/bin/env python
# coding: utf-8
# Find Anagrams - Part 00
# File and DB i/o utilities
# Mike Babb
# babb.mike@outlook.com

# standard libraries
from time import perf_counter_ns
import os
import pickle
import sqlite3

# external libraries
import pandas as pd

# custom libraries
import _run_constants as rc

# setup the data output path
def create_path(data_output_file_path:str) -> None:
    
    if os.path.exists(data_output_file_path):
        print(os.path.normpath(data_output_file_path), 'exists')
    else:
        os.makedirs(data_output_file_path)

    return None


def calc_time(time_start:perf_counter_ns,                      
              round_digits:int = 2) -> float:
    
    time_end = perf_counter_ns()
    time_proc = (time_end - time_start) / 1e9    
    if round_digits != -1:
        time_proc = round(time_proc, round_digits)
    return time_proc


def compute_total_time(total_time_start:perf_counter_ns):
    print('##########')
    print('TOTAL TIME ELAPSED:')
    # record the total time
    total_time_seconds = calc_time(
        time_start=total_time_start, round_digits=-1)
    total_time_minutes = total_time_seconds / 60
    # round for display
    total_time_seconds = round(total_time_seconds, 2)
    total_time_minutes = round(total_time_minutes, 2)

    print(total_time_seconds, "seconds |",  total_time_minutes, "minutes")

# let's convert to total hours, total minutes, and total seconds
def get_hms(seconds:float, round_seconds_digits:int = 0, as_string:bool = True):
    # convert seconds to total hours, minutes, and seconds
    # for example: 3661 seconds is 1 hour, 1 minute, 1 second
    # whole hours
    hours = int(seconds // 3600)
    # whole minutes
    minutes = int((seconds - (hours * 3600)) // 60)
    remaining_seconds = seconds - ((hours * 3600) + (minutes * 60))
    
    remaining_seconds = round(remaining_seconds, round_seconds_digits)
    if round_seconds_digits == 0:
        remaining_seconds = int(remaining_seconds)
    
    if as_string:
        hours = str(hours)
        minutes = str(minutes)
        remaining_seconds = str(remaining_seconds)

    return hours, minutes, remaining_seconds
    
def compute_elapsed_time(seconds:float):
    hours, minutes, seconds = get_hms(seconds=seconds, round_seconds_digits=8, as_string=False)
    print(f"Hours: {hours} | minutes: {minutes} | seconds: {seconds}")
    

# helper function to save pickled objects
def save_pickle(file_path, file_name, obj):
    """PICKLE (COMPRESS) A PYTHON OBJECT AND SERIALIZE TO DISK."""
    # https://docs.python.org/3/library/pickle.html#pickle.dump
    fpn = os.path.join(file_path, file_name)
    with open(fpn, "wb") as f:
        pickle.dump(obj, f)

    return None


def load_pickle(in_file_path, in_file_name):
    """LOAD A PICKLED (COMPRESSED) OBJECT"""
    # https://docs.python.org/3/library/pickle.html#pickle.load
    fpn = os.path.join(in_file_path, in_file_name)
    with open(fpn, "rb") as f:
        unpickled_object = pickle.load(f)

    return unpickled_object


def build_db_conn(db_path, db_name):
    """BUILD AND RETURN A SQLITE DATABASE CONNECTION"""
    # https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection
    db_path_name = os.path.join(db_path, db_name)
    db_conn = sqlite3.connect(db_path_name)

    return db_conn


def query_db(sql, db_path, db_name, params=None):
    """QUERY A SQLITE DATABASE, RETURN A PANDAS DATAFRAME"""
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_sql.html
    db_conn = build_db_conn(db_path=db_path, db_name=db_name)

    s_time = perf_counter_ns()

    df = pd.read_sql(sql=sql, con=db_conn, params=params)
    db_conn.close()

    p_time = calc_time(s_time)   
       
    print("...query execution took:", p_time, "seconds...")

    return df


def execute_sql_statement(sql, db_path, db_name):
    """EXECUTE ARBITRAY SQL STATEMENTS AGAINST A DATABASE"""
    # https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor

    # build connection and cursor objects
    db_conn = build_db_conn(db_path=db_path, db_name=db_name)
    db_cursor = db_conn.cursor()

    # execute the sql statement
    s_time = perf_counter_ns()
    db_cursor.execute(sql)
    db_conn.commit()

    p_time = calc_time(s_time)       
    print("...SQL execution took:", p_time, "seconds.")

    # close connection objects
    db_cursor.close()
    db_conn.close()

    return None

# write this out

def write_data_to_sqlite(df:pd.DataFrame, table_name:str, db_path:str, db_name:str,
                         if_exists_option='replace',
                         index_option=False, verbose=True):
    """
    A wrapper function to help with writing a pandas df to SQLite
    :param df:
    :param table_name:
    :param db_path:
    :param db_name:
    :param db_conn:
    :param if_exists_option:
    :param index_option:
    :return:
    """
    db_conn = build_db_conn(db_path = db_path, db_name = db_name)

    if verbose:
        print('...now writing:', table_name)

    # write the table of interest
    df.to_sql(name=table_name, con=db_conn, if_exists=if_exists_option,
              index=index_option)
    
    db_conn.close()

    return None




if __name__ == "__main__":
    # simple test, query the first 10 words
    sql = "select * from words limit 10;"
    db_path = rc.DB_PATH
    db_name = rc.DB_NAME
    df = query_db(sql=sql, db_path=db_path, db_name=db_name)
    print(df.head())
