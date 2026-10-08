# Question to CSV Converter

A simple Streamlit application for converting pasted multiple-choice questions into a structured CSV file.

## Features

- Paste questions directly into a text box — no Word file upload required.
- Automatically numbers questions 1, 2, 3, ...
- Detects `(a)`, `(b)`, `(c)`, `(d)` options.
- Supports numbered questions such as `1.` and `1)`.
- Also supports unnumbered questions separated by blank lines.
- Lets the user select:
  - Question Type
  - Question Group
  - Question Level
  - Marks
- Shows a preview before downloading.
- Exports CSV with:
  - question_number
  - question_type
  - question_group
  - question_level
  - marks
  - question
  - option_1
  - option_2
  - option_3
  - option_4
  - answer

## Run locally

Install Python, then:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app will open in your browser.

## Input example

```text
1. What is an office?
(a) A place of work
(b) A market
(c) A farm
(d) A house

2. Who performs office duties?
(a) Manager
(b) Tailor
(c) Clerical staff
(d) Miner
```

The output will contain automatic question numbers and separate columns for each option.
