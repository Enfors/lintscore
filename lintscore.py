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

        pylint_score = self.run_pylint(file_name)
        num_lines = self.count_file_lines(file_name)
        points = int(pylint_score * num_lines)

        print("PyLint score: %f" % pylint_score)
        print("Lines       : %d" % num_lines)
        print("Final score : %d" % points)

        self.database.add_record("#000000", file_name, "Christer",
                                 pylint_score, num_lines, points)

    def run_pylint(self, file_name):
        "Run pylint on the specified file. Return the pylint score."

        results = Run([file_name], reporter=QuietReporter(), exit=False)
        return results.linter.stats["global_note"]

    def count_file_lines(self, file_name):
        "Return the number of lines the the specified file."

        with open(file_name, "r") as file_handle:
            return len(file_handle.readlines())


class QuietReporter(BaseReporter):
    "Empty reporter to disable pylint output."

    def _display(self, foo):
        pass


if __name__ == "__main__":
    App("lintscore").run("lintscore_db.py")

