import difflib
import streamlit as st
from search_light import compare_revisions

st.set_page_config(page_title="Revision Grounding Eval", layout="wide")
st.title("Håller din AI-sökning koll på att reglerna ändrats?")
st.caption("Testat på amerikanska drönarregler, 14 CFR Part 107, 2017 vs 2021")


def render_diff(text_a, text_b):
    words_a = text_a.split()
    words_b = text_b.split()
    matcher = difflib.SequenceMatcher(None, words_a, words_b)
    parts = []
    for opcode, i1, i2, j1, j2 in matcher.get_opcodes():
        if opcode == "equal":
            parts.append(" ".join(words_a[i1:i2]))
        elif opcode == "delete":
            parts.append(f":red[~~{' '.join(words_a[i1:i2])}~~]")
        elif opcode == "insert":
            parts.append(f":green[{' '.join(words_b[j1:j2])}]")
        elif opcode == "replace":
            parts.append(f":red[~~{' '.join(words_a[i1:i2])}~~] :green[{' '.join(words_b[j1:j2])}]")
    return " ".join(parts)


examples = [
    "waiver for night operations",
    "do I need to retake the knowledge test",
    "remote pilot certificate age requirement",
]

query = st.text_input("Skriv en fråga, eller välj ett exempel nedan:")
cols = st.columns(len(examples))
for c, ex in zip(cols, examples):
    if c.button(ex):
        query = ex

if query:
    results = compare_revisions(query, k=3)
    top_2017 = results["2017-01-01"][0]
    top_2021 = results["2021-04-21"][0]
    weak_2017 = top_2017["score"] < 0.3
    weak_2021 = top_2021["score"] < 0.3

    if not weak_2017 and not weak_2021:
        if top_2017["identifier"] == top_2021["identifier"]:
            if top_2017["body"] == top_2021["body"]:
                st.success(f"Samma paragraf ({top_2017['identifier']}), oförändrad text mellan 2017 och 2021.")
            else:
                st.error(f"Samma paragrafnummer ({top_2017['identifier']}), men innehållet skiljer sig mellan 2017 och 2021.")
                st.markdown(render_diff(top_2017["body"], top_2021["body"]))
        else:
            st.warning(f"Bästa träffen är olika paragrafer i de två versionerna: 2017 hittar {top_2017['identifier']}, 2021 hittar {top_2021['identifier']}. Den paragraf som faktiskt ändrats kanske inte ens är top-träffen.")

    col_2017, col_2021 = st.columns(2)
    for col, top, label, weak in [(col_2017, top_2017, "2017", weak_2017), (col_2021, top_2021, "2021", weak_2021)]:
        with col:
            st.subheader(label)
            if weak:
                st.info("Ingen stark träff i det här dokumentsettet")
            else:
                st.markdown(f"**{top['identifier']}: {top['heading']}**")
                st.write(top["body"])
                if top["revision_gate_flag"]:
                    st.warning("Flaggad som ändrad mellan årtalen")