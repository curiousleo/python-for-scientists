#!/usr/bin/env python3

import csv
from operator import itemgetter

import quiz, output, result


if __name__ == "__main__":
    from sys import argv

    _, quiz_filename, result_filename, output_filename = argv

    with open(output_filename, "w", newline="", encoding="utf-8") as output_file:
        csv_writer = csv.writer(output_file)
        keep_indices = []
        with open(quiz_filename, newline="", encoding="utf-8") as quiz_file:
            clozes_list = []  # list of list of clozes
            for _, question_text in sorted(quiz.extract_questions(quiz_file), key=itemgetter(0)):
                clozes_list.append(
                    [quiz.parse_cloze(q) for q in quiz.extract_clozes(question_text)]
                )
            keep_indices = tuple(output.shortanswer_marker(clozes_list))
            header = [
                cell for (keep, cell) in zip(keep_indices, output.csv_header(clozes_list)) if keep
            ]
            row = [cell for (keep, cell) in zip(keep_indices, output.csv_row(clozes_list)) if keep]
            csv_writer.writerow(["Name", "Vorname"] + header)
            csv_writer.writerow(["Richtige", "Antwort"] + row)

        with open(result_filename, newline="", encoding="utf-8") as result_file:
            next(result_file)
            csv_writer.writerows(
                [row[0], row[1]]
                + [
                    output.postprocess_cell(cell)
                    for (keep, cell) in zip(keep_indices, row[2:])
                    if keep
                ]
                for row in sorted(result.parse_result_rows(result_file))
            )
