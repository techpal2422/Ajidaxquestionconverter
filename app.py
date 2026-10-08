import streamlit as st
import pandas as pd
import re
from io import StringIO

st.set_page_config(page_title="Question to CSV Converter", page_icon="📝", layout="wide")

st.title("📝 Multiple-Choice Question to CSV Converter")
st.write("Paste your questions below. The app will automatically number them, separate the options, and create a CSV file.")

# -------------------------
# Sidebar metadata
# -------------------------
st.sidebar.header("Question Settings")

question_type = st.sidebar.selectbox(
    "Question Type",
    ["single_choice", "multiple_choice", "true_false"],
    index=0
)

question_group = st.sidebar.text_input("Question Group", value="119")
question_level = st.sidebar.selectbox(
    "Question Level",
    ["easy", "medium", "hard"],
    index=0
)
marks = st.sidebar.number_input("Marks per Question", min_value=0, value=1, step=1)

st.sidebar.markdown("---")
st.sidebar.info(
    "Tip: Your questions can be numbered or unnumbered. "
    "Options such as (a), (b), (c), (d) are detected automatically."
)

# -------------------------
# Parser
# -------------------------
def normalize_text(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u00a0", " ")
    return text

def split_questions(text):
    """
    Supports:
      1. Question...
      2) Question...
    and also unnumbered questions separated by blank lines.
    """
    text = normalize_text(text).strip()

    if not text:
        return []

    # Detect numbered question starts anywhere at the beginning of a line.
    numbered = list(re.finditer(r'(?m)^\s*(\d+)\s*[\.\)]\s+', text))

    if numbered:
        chunks = []
        for i, m in enumerate(numbered):
            start = m.end()
            end = numbered[i + 1].start() if i + 1 < len(numbered) else len(text)
            body = text[start:end].strip()
            if body:
                chunks.append((m.group(1), body))
        return chunks

    # If no numbering exists, split on blank lines.
    blocks = re.split(r'\n\s*\n+', text)
    blocks = [b.strip() for b in blocks if b.strip()]
    return [(str(i + 1), b) for i, b in enumerate(blocks)]

def parse_question(number, body):
    body = re.sub(r'\s+', ' ', body).strip()

    # Find option markers: (a), (b), (c), (d)
    matches = list(re.finditer(r'\(\s*([a-dA-D])\s*\)', body))

    # Also support A), A., A: and Option A:
    if len(matches) < 2:
        matches = list(re.finditer(
            r'(?:^|\s)(?:Option\s*)?([a-dA-D])\s*[\)\.:]\s*',
            body,
            flags=re.IGNORECASE
        ))

    if matches:
        question_text = body[:matches[0].start()].strip(" -:")
        options = ["", "", "", ""]

        for i, match in enumerate(matches[:4]):
            letter = match.group(1).lower()
            idx = ord(letter) - ord("a")
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
            value = body[start:end].strip(" ;")
            if 0 <= idx <= 3:
                options[idx] = value

        # Detect answer if written like "Answer: C" or "Ans: C"
        answer = ""
        ans_match = re.search(
            r'\b(?:answer|ans)\s*[:\-]\s*\(?([a-dA-D])\)?\b',
            body,
            flags=re.IGNORECASE
        )
        if ans_match:
            answer = ans_match.group(1).upper()

        return {
            "question_number": int(number) if str(number).isdigit() else number,
            "question": question_text,
            "option_1": options[0],
            "option_2": options[1],
            "option_3": options[2],
            "option_4": options[3],
            "answer": answer
        }

    return {
        "question_number": int(number) if str(number).isdigit() else number,
        "question": body,
        "option_1": "",
        "option_2": "",
        "option_3": "",
        "option_4": "",
        "answer": ""
    }

# -------------------------
# Main input
# -------------------------
sample = """Which one of the following is not an office commonly found in an organization
(a) Staff room
(b) Account office
(c) Typing room
(d) Bedroom

Someone who performs office duties is known as a ______
(a) Manager
(b) Tailor
(c) Clerical staff
(d) Miner"""

questions_text = st.text_area(
    "Paste your questions here",
    height=420,
    placeholder="Paste all your questions here...\n\nExample:\n1. What is an office?\n(a) A place of work\n(b) A market\n(c) A farm\n(d) A house",
    help="You can paste numbered or unnumbered questions. The app detects (a), (b), (c), and (d) automatically."
)

col1, col2 = st.columns([1, 1])

with col1:
    convert = st.button("🔄 Convert Questions", type="primary", use_container_width=True)

with col2:
    clear = st.button("🗑️ Clear", use_container_width=True)

if clear:
    st.rerun()

if convert:
    if not questions_text.strip():
        st.warning("Please paste your questions into the box first.")
    else:
        raw_questions = split_questions(questions_text)

        rows = []
        for seq, (original_number, body) in enumerate(raw_questions, start=1):
            parsed = parse_question(seq, body)
            # Always renumber sequentially: 1, 2, 3...
            parsed["question_number"] = seq
            parsed.update({
                "question_type": question_type,
                "question_group": question_group,
                "question_level": question_level,
                "marks": marks
            })
            rows.append(parsed)

        columns = [
            "question_number",
            "question_type",
            "question_group",
            "question_level",
            "marks",
            "question",
            "option_1",
            "option_2",
            "option_3",
            "option_4",
            "answer"
        ]

        df = pd.DataFrame(rows)[columns]

        st.success(f"Successfully converted {len(df)} question(s).")

        st.subheader("Preview")
        st.dataframe(df, use_container_width=True, hide_index=True)

        csv_data = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download CSV",
            data=csv_data,
            file_name="converted_questions.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )

st.markdown("---")
st.caption("Automatic numbering • Question and option extraction • CSV export")
