import csv
import re

ANSWER_PATTERN = re.compile(r"Teil \d+:[ ]?([^;]*)")


def parse_result_rows(rows):
    for cells in csv.reader(rows, delimiter=","):
        first_name = cells[0]
        second_name = cells[1]
        answers = cells[11:]

        exploded = []
        for cell in answers:
            matches = ANSWER_PATTERN.findall(cell)
            if len(matches) == 0:
                exploded.append(cell)
            else:
                exploded.extend(matches)

        yield [first_name] + [second_name] + exploded


def test_parse_result_row():
    row = """
Max,Mustermann,12345,,,max@muster.ch,Beendet,"21. Januar 1999  07:18","21. Januar 2011  17:48","2 Stunden 30 Minuten",44.62,"Teil 1: Butan-1-on; Teil 2: Z; Teil 3: Piperidin","Teil 1: Benzocarboxamid; Teil 2: Nitril; Teil 3: Ethinyl"
    """.strip()
    assert next(parse_result_rows([row])) == [
        "Max",
        "Mustermann",
        "Butan-1-on",
        "Z",
        "Piperidin",
        "Benzocarboxamid",
        "Nitril",
        "Ethinyl",
    ]
