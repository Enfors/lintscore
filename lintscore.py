#!/usr/bin/env python2.7

from __future__ import print_function

from pylint.lint import Run
from pylint.reporters import BaseReporter

import lintscore_db

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
        print("points change   : %d" % (points - prev_points))

        self.database.add_record("#000000", file_name, "Christer",
                                 score, num_lines, points - prev_points)

    def run_pylint(self, file_name):
        "Run pylint on the specified file. Return the pylint score."

        results = Run([file_name], reporter=QuietReporter(), exit=False)
        return float(results.linter.stats["global_note"])

    def count_file_lines(self, file_name):
        "Return the number of lines the the specified file."

        with open(file_name, "r") as file_handle:
            return len(file_handle.readlines())


    def calc_points(self, score, num_lines):
        "Return points based on score and number of lines."
        return int((score - 5.0) * num_lines)
        

class QuietReporter(BaseReporter):
    "Empty reporter to disable pylint output."

    def _display(self, foo):
        pass


if __name__ == "__main__":
    App("lintscore").run("lintscore_db.py")

