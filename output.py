import html

from quiz import Answer, Cloze


def csv_header(questions):
    for i, clozes in enumerate(questions):
        if len(clozes) <= 1:
            yield f"Aufgabe {i+1}"
            continue
        for j, cloze in enumerate(clozes):
            yield f"Aufgabe {i+1} Teil {j+1}"


def csv_row(questions):
    for clozes in questions:
        if len(clozes) == 0:
            yield "<>"
            continue
        for cloze in clozes:
            if len(cloze.answers) == 0:
                yield "<>"
                continue
            correct_answers = (answer.text for answer in cloze.answers if answer.score == 100)
            yield "|".join(correct_answers)


def contains_cloze_type(cloze_types, questions):
    for clozes in questions:
        if len(clozes) == 0:
            yield False
            continue
        for cloze in clozes:
            if len(cloze.answers) == 0:
                yield False
                continue
            yield cloze.cloze_type in cloze_types


def test_csv_functions():
    questions = [
        [
            Cloze(
                id=1,
                cloze_type="multichoice",
                answers=[
                    Answer(text="correct1", score=100),
                    Answer(text="correct2", score=100),
                    Answer(text="incorrect", score=80),
                ],
            ),
            Cloze(id=1, cloze_type="diimageortext", answers=[]),
            Cloze(
                id=1,
                cloze_type="shortanswer",
                answers=[
                    Answer(text="correct", score=100),
                    Answer(text="incorrect1", score=50),
                    Answer(text="incorrect2", score=80),
                ],
            ),
        ],
        [],
    ]

    assert tuple(csv_header(questions)) == (
        "Aufgabe 1 Teil 1",
        "Aufgabe 1 Teil 2",
        "Aufgabe 1 Teil 3",
        "Aufgabe 2",
    )
    assert tuple(csv_row(questions)) == ("correct1|correct2", "<>", "correct", "<>")
    assert tuple(contains_cloze_type(("shortanswer",), questions)) == (False, False, True, False)


def postprocess_cell(cell):
    processed = html.unescape(cell.replace("\r", "").replace("\n", "")).strip()
    return processed if len(processed) > 0 else "leer"


def test_postprocess_cell():
    assert postprocess_cell("bla\rblupp\r\n\r") == "blablupp"
    assert postprocess_cell(" bla   ") == "bla"
    assert postprocess_cell("") == "leer"
    assert postprocess_cell(" ") == "leer"


def test_sorted():
    sorted1 = sorted([["NachnameA", "VornameA"], ["NachnameA", "VornameB"]])
    sorted2 = sorted([["NachnameA", "VornameB"], ["NachnameA", "VornameA"]])
    correct = [["NachnameA", "VornameA"], ["NachnameA", "VornameB"]]

    assert sorted1 == correct
    assert sorted2 == correct
