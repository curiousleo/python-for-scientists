# Introduction

In this series, I will show you how I built data processing pipeline in Python. There will be plenty of code snippets, but my primary goal is to show you the patterns, techniques and tools I used.

I wrote this series so my scientist friends can spend more time doing science and less time wrangling data.

## Problem statement

This series, like every data wrangling project, evolves around some task we want to automate. It is very valuable to have a good understanding of the problem before you start writing any code.

:bulb: **Tip #1: Describe the problem you are trying to solve in terms of relevant concepts, inputs, and outputs.**

The problem we're trying solve in this series is one that Greta faced when she was asked to mark a chemistry exam that students had taken via [Moodle](https://moodle.org/), an online learning platform used by her university.

Let's follow Tip #1 and describe the problem in terms of its relevant concepts, inputs, and outputs.

**Concepts**

- _Student_, identified by e-mail address
- _Exam_, consists of _questions_
- Questions have _parts_
- Some question parts are _multiple choice_
- Multiple choice question parts have _answer options_
- Answer options have a _score_ (100% means exactly correct, 0% means completely wrong)

**Inputs**

- <abbr title="Comma-separated values">CSV</abbr> file with a row for each student and one column per question. The cell in row _s_ and column _q_ contains the answers student _s_ gave for all question parts in question _q_.
- Moodle <abbr title="eXtensible markup language">XML</abbr> file of the exam containing all questions. For each multiple choice question, the answer options and their scores are included.

**Outputs**

- CSV file with one row for the correct answers, followed by one row per student. There is one column per for question part for all question parts that are multiple choice. Cells contain the students' answers.
