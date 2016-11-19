#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"Create the database needed for the program."

from __future__ import print_function

import datetime
import sqlite3

class Database(object):
    "The database class for lintscore."

    def __init__(self, file_name):
        "Initialize the database."

        self.file_name = file_name
        self.con = sqlite3.connect(self.file_name)

        with self.con:
            cur = self.con.cursor()

            cur.execute("create table if not exists RECORD("
                        "COMMIT_ID     text,"
                        "FILE_NAME     text,"
                        "USER          text,"
                        "SCORE         float,"
                        "NUM_LINES     int,"
                        "POINTS_CHANGE int,"
                        "TIME          timestamp);")


    def add_record(self, commit_id, file_name, user, score, num_lines,
                   points_change):
        "Add one record to the database."
        with self.con:
            cur = self.con.cursor()

            cur.execute("insert into RECORD("
                        "commit_id, file_name, user, score, num_lines, "
                        "points_change, time) values (?, ?, ?, ?, ?, ?, ?)",
                        (commit_id, file_name, user,
                         score, num_lines, points_change,
                         datetime.datetime.now()))

    def get_file_score(self, file_name):
        "Return the latest PyLint score for a file from the database."
        with self.con:
            cur = self.con.cursor()

            cur.execute("select SCORE from RECORD where file_name = ? "
                        "order by time desc limit 1", (file_name,))

            try:
                return float(cur.fetchone()[0])
            except TypeError:
                return 0

    def get_file_num_lines(self, file_name):
        "Return the number of lines the file had last time."
        with self.con:
            cur = self.con.cursor()

            cur.execute("select NUM_LINES from RECORD where file_name = ? "
                        "order by time desc limit 1", (file_name,))

            try:
                return cur.fetchone()[0]
            except TypeError:
                return 0

    def get_highscore_table(self):
        "Summarize the POINTS (not score) for all users, sorted."
        with self.con:
            cur = self.con.cursor()

            cur.execute("select USER, sum(POINTS_CHANGE) from RECORD "
                        "group by user "
                        "order by sum(POINTS_CHANGE) desc")

            return [row for row in cur.fetchall() if row[1] > 0]

    def get_lowscore_table(self):
        "Summarize the POINTS (not score) for all users, sorted."
        with self.con:
            cur = self.con.cursor()

            cur.execute("select USER, sum(POINTS_CHANGE) from RECORD "
                        "group by user "
                        "order by sum(POINTS_CHANGE) asc")

            return [row for row in cur.fetchall() if row[1] < 0]

if __name__ == "__main__":
    print("I ain't doin' shit.")

