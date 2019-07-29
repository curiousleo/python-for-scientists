from collections import namedtuple
from lxml import etree
from io import StringIO
import re
import html
from parsimonious import NodeVisitor, Grammar
from typing import Iterable, Tuple

CLOZE_XPATH = '/quiz/question[@type!="category" and @type!="description"]'
NAME_XPATH = "name/text/text()"
HTML_XPATH = 'questiontext[@format="html"]/text/text()'
CLOZE_RE = re.compile(r"({\d+:[^}]+})")


Question = namedtuple("Question", ("name", "clozes"))
Cloze = namedtuple("Cloze", ("id", "cloze_type", "answers"))
Answer = namedtuple("Answer", ("text", "score"))


def extract_questions(quiz: str) -> Iterable[Tuple[str, str]]:
    questions = etree.parse(quiz).xpath(CLOZE_XPATH)
    return ((q.xpath(NAME_XPATH)[0], q.xpath(HTML_XPATH)[0]) for q in questions)


def extract_clozes(question: str) -> Iterable[str]:
    return (match.group() for match in CLOZE_RE.finditer(question))


def parse_cloze(cloze: str) -> Cloze:
    return ClozeVisitor().parse(cloze)


class ClozeVisitor(NodeVisitor):
    def __init__(self):
        self.grammar = Grammar(
            """
            cloze           = "{" number ":" type ":" answer further_answers "}"
            further_answers = further_answer*
            further_answer  = "~" answer
            answer          = correct / partial / incorrect
            incorrect       = ~"[^~}]+" # using answer_text here means "incorrect" would be optimised away
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
        answers = list([children[5]] + list(children[6]))
        return Cloze(id=children[1], cloze_type=children[3], answers=answers)

    def visit_further_answers(self, node, children):
        return children

    def visit_further_answer(self, node, children):
        return children[1]

    def visit_answer(self, node, children):
        return children[0]

    def visit_correct(self, node, children):
        return Answer(text=children[1], score=100)

    def visit_partial(self, node, children):
        return Answer(text=children[3], score=children[1])

    def visit_incorrect(self, node, children):
        return Answer(text=html.unescape(html.unescape(node.text)), score=0)

    def visit_answer_text(self, node, children):
        return html.unescape(html.unescape(node.text))

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
        <!-- question: 66143  -->
          <question type="description">
            <name>
              <text>Hinweise und Tools</text>
            </name>
            <questiontext format="html">
              <text><![CDATA[blabla]]></text>
            </questiontext>
          </question>
        <!-- question: 66143  -->
        <question type="ddmarker">
          <name>
            <text>Aufgabe 03g Enantiomer einer Fischerprojektion</text>
          </name>
          <questiontext format="html">
            <text><![CDATA[dontcare]]></text>
          </questiontext>
        </question>
      </quiz>
        """
    questions = list(extract_questions(StringIO(quiz)))
    assert len(questions) == 2
    assert questions[0][0] == "Aufgabe 01a Nomenklatur"
    assert questions[0][1] == "<p>hi</p>"
    assert questions[1][0] == "Aufgabe 03g Enantiomer einer Fischerprojektion"
    assert questions[1][1] == "dontcare"


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
    clozes = list(extract_clozes(question))
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
    assert cloze.answers[8] == Answer(text="xxxxxxxxxxxxxxxxxxxx", score=0)
