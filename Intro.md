# Introduction

In this series, I will show you how I built data processing pipeline in Python. There will be plenty of code snippets, but my primary goal is to show you the patterns, techniques and tools I used.

I wrote this series so my scientist friends can spend more time doing science and less time wrangling data.

## The problem statement

This series, and every data wrangling project, evolves around some task we want to automate. It is very valuable to have a good understanding of the problem before you start writing any code.

**Tip #1: Describe the problem you are trying to solve in terms of its inputs and outputs.**

The problem we're trying solve in this series is one that Greta faced when she was asked to mark a chemistry exam that students had taken via [Moodle](https://moodle.org/), an online learning platform used by her university.

*Inputs*

- <abbr title="Comma-separated values">CSV</abbr> file with a row for each student and one column per question. The cell in row _s_ and column _q_ contains the answer student _s_ gave for question _q_.
- Moodle <abbr title="eXtensible markup language">XML</abbr> file of the exam, containing all questions. For each multiple choice question, the answer options and their scores are included.

Note that a question can have multiple parts. The answers to all parts of a question are put in the same cell in the CSV input file.

*Outputs*

- CSV file with one row for the correct answers, followed by one row per student. There is one column per for each part of all multiple choice questions. Cells contain the students' answers.
