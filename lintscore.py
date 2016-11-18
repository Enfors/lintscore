#!/usr/bin/env python2.7

from __future__ import print_function

import os
import sys

from pylint.lint import Run
from pylint.reporters import BaseReporter

import lintscore_db

initial_points_appraisal = [
    [-50, "OH MY GOD, %s ISN'T BREATHING! DOES SOMEBODY KNOW PYTHON CPR?!"],
    [-40, "Whoa, whoa! Are you trying to KILL PyLint? %s looks TERRIBLE!"],
    [-30, "%s: -30"],
    [-20, "%s: -20"],
    [-10, "%s: -10"],
    [0, "%s: 0"],
    [10, "PyLint has seen a lot worse than %s, but it's seen better too."],
    [20, "%s: 20"],
    [30, "%s: 30"],
    [40, "%s: 40"],
    [50, "%s: 50"],
]

point_change_appraisal = [
    [-50, "You bastard, you killed %s!"],
    [-40, "AAAAAH! %s just gave poor old PyLint a heart attack!"],
    [-30, "Oh my God, what did you do to %s?!"],
    [-20, "You're really messing up %s!"],
    [-10, "You're making %s worse. Stop it."],
    [  0, "You made %s a little worse, but not too bad."],
    [  1, "%s looks about the same as it used to."],
    [ 10, "I see you've improved %s slightly. Nice."],
    [ 20, "Nice work, %s is been improved!"],
    [ 30, "Very nice work indeed, %s is looking a lot better!"],
    [ 40, "Wow! You've really cleaned up %s! Well done!"],
    [ 50, "Amazing job on %s! It looks SO much better now."]
]

class App(object):
    "Application which keeps score of how well-written Python files are."

    def __init__(self, name):
        self.name = name
        self.database = lintscore_db.Database("lintscore.db")

    def run(self, file_name):
        "Start the application."

        prev_score = self.database.get_file_score(file_name)
        prev_num_lines = self.database.get_file_num_lines(file_name)
        prev_points = self.calc_points(prev_score, prev_num_lines)

        score = self.run_pylint(file_name)
        num_lines = self.count_file_lines(file_name)
        points = self.calc_points(score, num_lines)
        points_change = points - prev_points

        print("prev_score      : %2.2f" % prev_score)
        print("prev_num_lines  : %d" % prev_num_lines)
        print("prev_points     : %d" % prev_points)
        print("------------------------------")
        print("score           : %2.2f" % score)
        print("num_lines       : %d" % num_lines)
        print("points          : %d" % points)
        print("------------------------------")
        print("score change    : %2.2f" % (score - prev_score))
        print("num_lines change: %d" % (num_lines - prev_num_lines))
        print("points change   : %d" % points_change)

        if (prev_num_lines == 0):
            print(self.get_initial_points_appraisal(file_name, points))
        else:
            print(self.get_point_change_appraisal(file_name, points_change))

        self.database.add_record("#000000", file_name, "Christer",
                                 score, num_lines, points_change)

        rows = self.database.get_highscore_table()
        highscore_table = self.make_score_table("Highscore (yay!)", rows)

        rows = self.database.get_lowscore_table()
        lowscore_table = self.make_score_table("Lowscore (boo, hiss)", rows)

        table_lines = max([len(highscore_table), len(lowscore_table)])

        for line_num in range(0, table_lines):
            if line_num <= len(highscore_table):
                sys.stdout.write(highscore_table[line_num] + " ")
            else:
                sys.stdout.write(" " * len(lowscore_table[line_num] + 1))

            if line_num <= len(lowscore_table):
                print(lowscore_table[line_num])

    @classmethod
    def run_pylint(cls, file_name):
        "Run pylint on the specified file. Return the pylint score."

        results = Run([file_name], reporter=QuietReporter(), exit=False)
        return float(results.linter.stats["global_note"])

    @classmethod
    def count_file_lines(cls, file_name):
        "Return the number of lines the the specified file."

        with open(file_name, "r") as file_handle:
            return len(file_handle.readlines())

    @classmethod
    def get_point_change_appraisal(cls, file_name, point_change):
        "Return a verbal description of the changes made to a file."

        file_name = os.path.basename(file_name)

        for threshold, comment in point_change_appraisal:
            if point_change < threshold:
                return comment % file_name

        return "I cannot BELIEVE how much you've improved %s!" % file_name

    @classmethod
    def get_initial_points_appraisal(cls, file_name, points):
        "Return a verbal description of the state of a file."

        file_name = os.path.basename(file_name)

        for threshold, comment in initial_points_appraisal:
            if points < threshold:
                return comment % file_name

        return "%s looks absolutely PERFECT!" % file_name

    @classmethod
    def calc_points(cls, score, num_lines):
        "Return points based on score and number of lines."
        return int((score - 5.0) * num_lines / 10)

    @classmethod
    def make_score_table(cls, title, rows):
        "Return a list of string representing a score table."
        table = []
        divider = "+----------------------------+-------+"
        
        if len(rows) < 1:
            return []

        table.append(title + " " * (len(divider) - len(title)))
        # table.append("%s%s" % ("=" * len(title),
        #                        " " * (len(divider) - len(title))))
        table.append(divider)
        
        for row in rows:
            table.append("|%-28s|%7d|" % (row[0], row[1]))

        table.append(divider)

        return table

class QuietReporter(BaseReporter):
    "Empty reporter to disable pylint output."

    def _display(self, foo):
        pass


if __name__ == "__main__":
    App("lintscore").run("eb_thread.py")
