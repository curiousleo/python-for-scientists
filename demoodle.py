#!/usr/bin/env python3

from collections import namedtuple
from lxml import etree
from io import StringIO
import re
import html
from parsimonious import NodeVisitor, Grammar

CLOZE_XPATH = '/quiz/question[@type="cloze"]'
NAME_XPATH = "name/text/text()"
HTML_XPATH = 'questiontext[@format="html"]/text/text()'
CLOZE_RE = re.compile(r"({\d+:[^}]+})")


Question = namedtuple("Question", ("name", "clozes"))
Cloze = namedtuple("Cloze", ("id", "cloze_type", "answers"))
Answer = namedtuple("Answer", ("text", "score"))


def extract_questions(quiz):
    questions = etree.parse(quiz).xpath(CLOZE_XPATH)
    return ((q.xpath(NAME_XPATH)[0], q.xpath(HTML_XPATH)[0]) for q in questions)


def extract_clozes(question):
    return (match.group() for match in CLOZE_RE.finditer(question))


def parse_cloze(cloze):
    return ClozeVisitor().parse(cloze)


class ClozeVisitor(NodeVisitor):
    def __init__(self):
        self.grammar = Grammar(
            """
            cloze           = "{" number ":" type ":" answer further_answers "}"
            further_answers = further_answer*
            further_answer  = "~" answer
            answer          = correct / partial / answer_text
            correct         = "=" answer_text
            partial         = "%" number "%" answer_text
            answer_text     = ~"[^~}]+"
            type            = ~"[A-Z]+"
            number          = ~"[0-9]+"
            """
        )

    def generic_visit(self, node, children):
        pass

    def visit_cloze(self, node, children):
        answers = tuple([children[5]] + list(children[6]))
        return Cloze(id=children[1], cloze_type=children[3], answers=answers)

    def visit_further_answers(self, node, children):
        return children

    def visit_further_answer(self, node, children):
        return children[1]

    def visit_answer(self, node, children):
        if isinstance(children[0], Answer):
            return children[0]
        return Answer(text=children[0], score=0)

    def visit_correct(self, node, children):
        return Answer(text=children[1], score=100)

    def visit_partial(self, node, children):
        return Answer(text=children[3], score=children[1])

    def visit_answer_text(self, node, children):
        return html.unescape(node.text)

    def visit_type(self, node, children):
        return node.text.lower()

    def visit_number(self, node, children):
        return int(node.text)


def test_extract_questions():
    quiz = """
        <quiz>
        <!-- question: 0  -->
          <question type="category">
            <category>
                <text>$course$/Standard für 529-1012-00J 2017W</text>
            </category>
          </question>
        <!-- question: 64632  -->
          <question type="cloze">
            <name>
              <text>Aufgabe 01a Nomenklatur</text>
            </name>
            <questiontext format="html">
              <text><![CDATA[<p>hi</p>]]></text>
            </questiontext>
            <generalfeedback format="html">
              <text><![CDATA[<ol><li>But-2-enal</li><li>Stereodeskriptor = <i>Z</i></li><li>Piperidin</li></ol>Gewichtung
        der Teilfragen bzgl. Bewertung = 1:1:1<br>]]></text>
            </generalfeedback>
            <penalty>0.3333333</penalty>
            <hidden>0</hidden>
          </question>
        </quiz>
        """
    questions = tuple(extract_questions(StringIO(quiz)))
    assert len(questions) == 1
    assert questions[0][0] == "Aufgabe 01a Nomenklatur"
    assert questions[0][1] == "<p>hi</p>"


def test_extract_clozes():
    question = """
        <p><strong>Nomenklatur</strong></p>
        <p><em>Bitte verwenden Sie bei der Eingabe der Namen von Molekül-Teilstrukturen ohne Lokanten <span style="text-decoration: underline;">keine</span> initialen oder terminalen <span style="text-decoration: underline;">Bindestriche</span>.</em></p>
        <p><img src="@@PLUGINFILE@@/1a%20%282%29.png" alt="" role="presentation" class="img-responsive atto_image_button_text-bottom" width="220" height="110"><br></p>
        <p>{1:SHORTANSWER:=But-2-enal~=2-Butenal~=But-2-en-1-al~=2-Buten-1-al~%50%But-2-enon~%50%2-Butenon~%50%But-2-en-1-on~%50%2-Buten-1-on~xxxxxxxxxxxxxxxxxxxx}</p>
        <p><strong>2)</strong> Wie lautet der Stereodeskriptor für obiges Molekül?</p>
        <p>{1:MULTICHOICE:R~S~=Z~E~P~M~Re~Si}</p>
        <p><strong>3)</strong> Wie lautet der Name des im Molekül enthaltenen Heterocyclus (Name des unsubstituierten Heterocyclus)?</p>
        <p>{1:SHORTANSWER:=Piperidin~=Azacyclohexan~=1-Azacyclohexan~xxxxxxxxxxxxxxxxxxxx}</p>
        """
    clozes = tuple(extract_clozes(question))
    assert clozes == (
        "{1:SHORTANSWER:=But-2-enal~=2-Butenal~=But-2-en-1-al~=2-Buten-1-al~%50%But-2-enon~%50%2-Butenon~%50%But-2-en-1-on~%50%2-Buten-1-on~xxxxxxxxxxxxxxxxxxxx}",
        "{1:MULTICHOICE:R~S~=Z~E~P~M~Re~Si}",
        "{1:SHORTANSWER:=Piperidin~=Azacyclohexan~=1-Azacyclohexan~xxxxxxxxxxxxxxxxxxxx}",
    )


def test_parse_cloze():
    cloze = parse_cloze(
        "{1:SHORTANSWER:=But-2-enal~=2-Butenal~=But-2-en-1-al~=2-Buten-1-al~%50%But-2-enon~%50%2-Butenon~%50%But-2-en-1-on~%50%2-Buten-1-on~xxxxxxxxxxxxxxxxxxxx}"
    )

    assert isinstance(cloze, Cloze)
    assert len(cloze.answers) == 9
    assert cloze.answers[0] == Answer(text="But-2-enal", score=100)
    assert cloze.answers[4] == Answer(text="But-2-enon", score=50)


if __name__ == "__main__":
    from sys import argv

    with open(argv[1]) as quiz:
        for (name, question) in extract_questions(quiz):
            print(name)
            for cloze in extract_clozes(question):
                print(f"  {cloze}")
                for answer in parse_cloze(html.unescape(cloze)).answers:
                    print(f"    [{answer.score: >3}%] {answer.text}")
