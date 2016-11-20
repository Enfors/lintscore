#!/usr/bin/env python2.7
"Evaluate a Python file."

from __future__ import print_function

import argparse
import os
import sys

from pylint.lint import Run
from pylint.reporters import BaseReporter

import lintscore_db

SCORE_APPRAISAL = [
    [1.00, "OH MY GOD, PYLINT ISN'T BREATHING! DOES SOMEBODY KNOW PYTHON CPR?!"],
    [2.00, "Whoa, whoa! Are you trying to KILL PyLint? That's TERRIBLE!"],
    [3.00, "You made PyLint SAD. I hope you're happy."],
    [4.00, "PyLint looked at your file. PyLint was not impressed."],
    [5.00, "PyLint just sighed when it saw this file."],
    [6.00, "PyLint says your file is pretty meh."],
    [7.00, "PyLint has seen a lot worse, but it's seen better too."],
    [8.00, "This looks pretty decent, but could easily be improved."],
    [9.00, "This looks pretty good, well done."],
    [9.99, "This looks really good, you just gave PyLint a happy."],
    [50, "That's absolutely PERFECT!"],
]

POINT_CHANGE_APPRAISAL = [
    [-50, "You killed PyLint! You BASTARD!"],
    [-40, "AAAAAH! You just gave poor old PyLint a heart attack!"],
    [-30, "Oh my God, what did you do to that poor file?!"],
    [-20, "You're really messing it up!"],
    [-10, "You're making it worse. Stop it."],
    [0, "You made it a little worse, but not too bad."],
    [1, "It looks about the same as it used to."],
    [10, "I see you've improved it slightly. Nice."],
    [20, "Nice work, the file has been improved!"],
    [30, "Very nice work indeed, it looks a lot better now!"],
    [40, "Wow! You've really cleaned it up! Well done!"],
    [50, "Amazing job! It looks SO much better now."]
]

OVERALL_APPRAISAL = [
    [-100, "This code REALLY needs some PyLint. Like, seriously."],
    [-50, "This code could use a serious cleanup. Use PyLint."],
    [-20, "Consider using PyLint to improve code quality."],
    [0, "I've seen worse, but PyLint would help."],
    [20, "Overall, you're improving the code. Nice job."],
]

class App(object):
    "Application which keeps score of how well-written Python files are."

    def __init__(self, name):
        self.name = name
        self.database = None

    def run(self):
        "Start the application."
        points_awarded = 0

        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--database", type=str, default="lintscore.db",
                            help="specify which database to use")
        parser.add_argument("file_names", metavar="filename", type=str, nargs="+",
                            help="a file to process")
        args = parser.parse_args()

        print("Files: %s" % args.file_names)
        print("Database: %s" % args.database)

        self.database = lintscore_db.Database(args.database)

        for file_name in args.file_names:
            points_awarded += self.handle_file(file_name)

        print("Total points awarded in this run: %d" % points_awarded)
        if points_awarded < 0:
            print("Consider using pylint to improve your code quality.")
        print()

        self.show_score_tables()

    def handle_file(self, file_name):
        "Analyze a file. Return the points awarded."
        prev_score = self.database.get_file_score(file_name)
        prev_num_lines = self.database.get_file_num_lines(file_name)
        prev_points = self.calc_points(prev_score, prev_num_lines)
        sys.stdout.write("Analyzing " + file_name + "... ")
        try:
            score = self.run_pylint(file_name)
            print("done. PyLint score: %2.2f" % score)
        except KeyError:
            print("failed.")
            print("Couldn't analyze %s." % file_name)
            sys.exit(2)
        num_lines = self.count_file_lines(file_name)
        points = self.calc_points(score, num_lines)
        points_change = points - prev_points

        if score == 10.0 and points_change < 0:
            points_change = 0

        #print("Points: %d (previous: %d)" % (points, prev_points))

        # print("prev_score      : %2.2f" % prev_score)
        # print("prev_num_lines  : %d" % prev_num_lines)
        # print("prev_points     : %d" % prev_points)
        # print("------------------------------")
        # print("score           : %2.2f" % score)
        # print("num_lines       : %d" % num_lines)
        # print("points          : %d" % points)
        # print("------------------------------")
        # print("score change    : %2.2f" % (score - prev_score))
        # print("num_lines change: %d" % (num_lines - prev_num_lines))
        # print("points change   : %d" % points_change)

        print(self.get_score_appraisal(file_name, score))

        if prev_num_lines is not 0: # If this is not a new file
            print("  - " + self.get_point_change_appraisal(file_name,
                                                           points_change))

        self.database.add_record("#000000", file_name, "Christer",
                                 score, num_lines, points_change)
        return points_change

    def show_score_tables(self):
        "Print Hall of Fame and Hall of Shame."
        rows = self.database.get_highscore_table()
        highscore_table = self.make_score_table("Hall of Fame (yay!)", rows)

        rows = self.database.get_lowscore_table()
        lowscore_table = self.make_score_table("Hall of Shame (boo, hiss)", rows)

        table_lines = max([len(highscore_table), len(lowscore_table)])

        for line_num in range(0, table_lines):
            if line_num < len(highscore_table):
                sys.stdout.write(highscore_table[line_num] + " ")
            else:
                sys.stdout.write(" " * (len(lowscore_table[line_num]) + 1))
            if line_num < len(lowscore_table):
                sys.stdout.write(lowscore_table[line_num])
            print()

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
        reward = cls.get_points_rewarded(point_change)

        for threshold, comment in POINT_CHANGE_APPRAISAL:
            if point_change < threshold:
                return comment + " " + reward

        return "I cannot BELIEVE how much you've improved it! " + reward

    @classmethod
    def get_score_appraisal(cls, file_name, score):
        "Return a verbal description of the state of a file based on PyLint score."

        file_name = os.path.basename(file_name)

        for threshold, comment in SCORE_APPRAISAL:
            if score < threshold:
                return "  - %s" % comment

    @classmethod
    def get_points_rewarded(cls, points):
        "Return a string like 'Points: +3'."

        if points is 0:
            return "No points for you. NEXT."
        elif points > 0:
            return "Points: +%d." % points
        else:
            return "Points: %d." % points

    @classmethod
    def calc_points(cls, score, num_lines):
        "Return points based on score and number of lines."
        return int((score - 5.0) * num_lines / 40)

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
    App("lintscore").run()

