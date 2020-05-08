# XML and text parsing in Python: extracting answers from a Moodle exam file

In this post we will create a Python program that parses a Moodle exam file and outputs the questions and answers contained within it. Along the way, I'll introduce you to practices, libraries and tools you can use in your own projects. Some programming experience is required to understand this post, but I'll include plenty of links so you can fill in any gaps if needed.

## Problem statement

Let's start by stating in some detail what it is that we are trying to achieve.

The problem we're trying solve here is one that Greta faced when she was asked to mark a chemistry exam. Paraphrasing a little, this is Greta's description of the issue:

> I received this XML file from my professor, which contains the correct exam answers. The file contains all answers for the whole exam. We're trying to extract them. We only need specific answers, not all of them. I would start with splitting by question type. We can ignore all question types apart from 'cloze'. Within cloze, we only need those with `{1:SHORTANSWER}` and NOT `{1:MULTICHOICE}`. And we don't want the ones with `Antwort (Zahl eingeben):` before them since they are checked automatically.

> The answer is always directly after `SHORTANSWER}=`. Occasionally there are saved answers, e.g. exercise 08a: `
{1:SHORTANSWER:=COC(=O)C\C=C(\C)CC=O~%66%COC(=O)C\C=C(/C)CC=O~%50%COC(=O)C\C=C(\C)CC(O)=O~%33%COC(=O)C\C=C(/C)CC(O)=O`

> The first part up until the tilde is completely correct, the next gets 66% etc., so we only need to extract up to the tilde. Careful though: in exercise 01d there are two correct options, Acetal and Ketal `{1:SHORTANSWER:=Acetal*~=Ketal*~xxxxxxxxxxxxxxxxxxxx}` and in the second part, Imin and Aldimin `{1:SHORTANSWER:=Imin*~=Aldimin*~%50%Ketimin*~xxxxxxxxxxxxxxxxxxxx}` - those are marked with an asterisk.

> This means that at the end I should get the solutions for exercises 01a 1 and 3 (2 is multiple choice), 01b, 01c, 01d, 02b, 02c, 03f, 04b, 08a, 08b, 08c 2, 08d, 08e 1, 08f, 08g, 08h, 08i, 08j.

The exam file itself was attached to the description. We'll have a look at it in the next section.

Note that the exam was in German. I won't translate any of the contents since understanding the questions and answers is not important here. (I speak German, but my knowledge of chemistry is very limited. I have very little idea of what is going on.)

To start with, I think that this original problem statement is pretty solid. Greta has clearly looked at the input file, and specified its format well. Still, I think we can improve on this in some ways.

> I need to mark an exam that was conducted via Moodle. I have a CSV file with the students' answers. Now I need to match them with the correct solutions. My professor has exported the exam into an XML file for me (attached).

> The XML file contains a `<quiz>` root element. Its children are `<question>` elements with a `type` attribute. I only care about questions of type `cloze`. Questions of type `cloze` have the following structure:

    <question type="cloze">
      <name>
        <text>Aufgabe 123 Beispiel</text>
      </name>
      <questiontext format="html">
        <text><![CDATA[This contains HTML with the questions embedded, see next example]]></text>
      </questiontext>
    </question>

> The HTML inside the `CDATA` section contains paragraphs, text formatting, images, and the questions themselves:

    <p><strong>Bla</strong></p> <p><img src="img.png" alt=""> <br><br></p> <p><strong>1)</strong>Benennen Sie den Verbindungsstamm (Hauptkette oder -ring + ranghöchste funktionelle Gruppe; ohne Substituenten) der gezeigten Verbindung.</p>
    <p>{1:SHORTANSWER:=But-2-enal~=2-Butenal~=But-2-en-1-al~=2-Buten-1-al~%50%But-2-enon~%50%2-Butenon~%50%But-2-en-1-on~%50%2-Buten-1-on~xxxxxxxxxxxxxxxxxxxx}</p>
    <p><strong>2)</strong> Wie lautet der Stereodeskriptor für obiges Molekül?</p>
    <p>{1:MULTICHOICE:R~S~=Z~E~P~M~Re~Si}</p>
    <p><strong>3)</strong> Wie lautet der Name des im Molekül enthaltenen Heterocyclus (Name des unsubstituierten Heterocyclus)?</p>
    <p>{1:SHORTANSWER:=Piperidin~=Azacyclohexan~=1-Azacyclohexan~xxxxxxxxxxxxxxxxxxxx}</p>

> I need all the answers of type `SHORTANSWER`, but I don't mind filtering out `MULTICHOICE` answers at a later stage. As an example, the program should extract the following information from the example question:

    {
      "Aufgabe 123 Nomenklatur": [
        {
          "type": "SHORTANSWER",
          "answers": [
            { "answer": "But-2-enal", "score": 100 },
            { "answer": "2-Butenal", "score": 100 },
            ...
            { "answer": "But-2-enon", "score": 50 },
            ...
            { "answer": "xxxxxxxxxxxxxxxxxxxx", "score": 0 }
          ]
        },
        {
          "type": "MULTICHOICE",
          "answers": [
            { "answer": "R", "score": 0 },
            { "answer": "S", "score": 0 },
            { "answer": "Z", "score": 100 },
            { "answer": "E", "score": 0 },
            { "answer": "P", "score": 0 },
            { "answer": "M", "score": 0 },
            { "answer": "Re", "score": 0 },
            { "answer": "Si", "score": 0 }
          ]
        },
        ...
      ]
    }

Note how the example _output_ actually helps us understand the _input_: there is scoring information attached to each answer, and we can always translate it into a percentage.

## Exploring the input file

### Environment setup

    nix-shell
    poetry install

- break problem down, write TODOs
- assert judiciously
- comment sparingly
- test first
- single file
- entr test and lint loop
