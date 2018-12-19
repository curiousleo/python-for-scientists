from collections import namedtuple
from lxml import etree
from io import StringIO
from lxml.html.soupparser import fromstring as html_fromstring
from parsimonious import NodeVisitor, Grammar

CLOZE_HTML_XPATH = (
    '/quiz/question[@type="cloze"]/questiontext[@format="html"]/text/text()'
)
SHORT_ANSWER_XPATH = '/html/p/text()[contains(.,":SHORTANSWER:")]'

ANSWER_GRAMMAR = Grammar(
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


def extract_questions(quiz):
    cloze_text = etree.parse(quiz).xpath(CLOZE_HTML_XPATH)
    return (html_fromstring(html) for html in cloze_text)


def extract_short_answers(question):
    return question.xpath(SHORT_ANSWER_XPATH)


Cloze = namedtuple("Cloze", ["id", "cloze_type", "answers"])
Answer = namedtuple("Answer", ["text", "score"])


class AnswerVisitor(NodeVisitor):
    def __init__(self):
        self.grammar = ANSWER_GRAMMAR

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
        return node.text

    def visit_type(self, node, children):
        return node.text.lower()

    def visit_number(self, node, children):
        return int(node.text)


def test_extract_questions():
    quiz = StringIO(
        """
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
  """.strip()
    )
    questions = list(extract_questions(quiz))
    assert len(questions) == 1


def test_extract_short_answers():
    question = html_fromstring(
        StringIO(
            """
<p><strong>Nomenklatur</strong></p>
<p><em>Bitte verwenden Sie bei der Eingabe der Namen von Molekül-Teilstrukturen ohne Lokanten <span style="text-decoration: underline;">keine</span> initialen oder terminalen <span style="text-decoration: underline;">Bindestriche</span>.</em></p>
<p><img src="@@PLUGINFILE@@/1a%20%282%29.png" alt="" role="presentation" class="img-responsive atto_image_button_text-bottom" width="220" height="110"><br></p>
<p>{1:SHORTANSWER:=But-2-enal~=2-Butenal~=But-2-en-1-al~=2-Buten-1-al~%50%But-2-enon~%50%2-Butenon~%50%But-2-en-1-on~%50%2-Buten-1-on~xxxxxxxxxxxxxxxxxxxx}</p>
<p><strong>2)</strong> Wie lautet der Stereodeskriptor für obiges Molekül?</p>
<p>{1:MULTICHOICE:R~S~=Z~E~P~M~Re~Si}</p>
<p><strong>3)</strong> Wie lautet der Name des im Molekül enthaltenen Heterocyclus (Name des unsubstituierten Heterocyclus)?</p>
<p>{1:SHORTANSWER:=Piperidin~=Azacyclohexan~=1-Azacyclohexan~xxxxxxxxxxxxxxxxxxxx}</p>
    """.strip()
        )
    )
    short_answers = extract_short_answers(question)
    assert len(short_answers) == 2
    assert (
        short_answers[0]
        == "{1:SHORTANSWER:=But-2-enal~=2-Butenal~=But-2-en-1-al~=2-Buten-1-al~%50%But-2-enon~%50%2-Butenon~%50%But-2-en-1-on~%50%2-Buten-1-on~xxxxxxxxxxxxxxxxxxxx}"
    )
    assert (
        short_answers[1]
        == "{1:SHORTANSWER:=Piperidin~=Azacyclohexan~=1-Azacyclohexan~xxxxxxxxxxxxxxxxxxxx}"
    )


def test_grammar():
    v = AnswerVisitor()
    print(
        v.parse(
            """
{1:SHORTANSWER:=But-2-enal~=2-Butenal~=But-2-en-1-al~=2-Buten-1-al~%50%But-2-enon~%50%2-Butenon~%50%But-2-en-1-on~%50%2-Buten-1-on~xxxxxxxxxxxxxxxxxxxx}
""".strip()
        )
    )


if __name__ == "__main__":
    test_grammar()
    # from sys import argv
    # with open(argv[1]) as quiz:
    #    for question in extract_questions(quiz):
    #        for answer in extract_short_answers(question):
    #            print(answer)
