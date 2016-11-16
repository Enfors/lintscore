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
                        "PYLINT_SCORE  float,"
                        "NUM_LINES     int,"
                        "POINTS        int,"
                        "POINTS_CHANGE int,"
                        "TIME          timestamp);")

    def add_record(self, commit_id, file_name, user, pylint_score, num_lines,
                   points):
        "Add one record to the database."
        with self.con:
            cur = self.con.cursor()

            print("-- POINTS: %d" % points)

            prev_points = self.get_prev_points(file_name)
            if prev_points:
                points_change = points - prev_points
                print("-- PREV_POINTS: %d" % prev_points)
            else:
                points_change = 0

            print("-- POINTS_CHANGE: %d" % points_change)

            print("INSERT")
            cur.execute("insert into RECORD "
                        "(commit_id, file_name, user, pylint_score, num_lines, "
                        "points, points_change, time) values "
                        "(?, ?, ?, ?, ?, ?, ?, ?)",
                        (commit_id, file_name, user, pylint_score,
                         num_lines, points, points_change,
                         datetime.datetime.now()))

    def get_prev_points(self, file_name):
        with self.con:
            cur = self.con.cursor()

            cur.execute("select POINTS from RECORD where file_name = ? "
                        "order by time desc limit 1", (file_name,))

            return cur.fetchone()[0]

    def get_user_points_change(self, user):
        with self.con:
            cur = self.con.cursor()

            cur.execute("select sum(points_change) from RECORD where "
                        "user = ?", (user,))

            return cur.fetchone()[0]

    def get_all_users(self):
        pass

if __name__ == "__main__":
    print("I ain't doin' shit.")

