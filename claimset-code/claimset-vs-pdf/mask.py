"""claimset-vs-pdf: mask an answer so that nobody grading it can tell the condition from its words (plan §9, item 2).

The same rules apply in both conditions:

    claimset identifiers of every kind (claims C12, definitions D4, evidence E3 and its tables and rows E3.T1.r2,
    warrants W2, limitations L2, artefacts A1, references B3, steps S1, ...) and paragraph markers ([p3.2]),
    with the word naming them ("claim C12", "limitation L2"), and locators (page, section, table, figure,
    appendix, equation, definition, theorem and other numbered parts of a paper)         -> "[location]"
    phrases naming the document's form ("the claimset", "the reading view", "the PDF",
    "the .txt file", "the text file", "this record")                                      -> "the paper"
    EntryLib citations (entrylib:2026.000003@v4#C12) and links                            -> "[location]"
    a bracket holding only locations ("(C3)", "(see Table 2)"); a bold label that is only one -> removed
    the reading view's headings in capitals (EVIDENCE, LIMITATIONS, ...)                  -> lower case
    file names, file references ([file: name]) and the apps' citation tags                -> removed

Runs of "[location]" joined by commas or "and" become one. M3, M4 and N2703 (competition data and series) are
names, not identifiers, and are kept: the claimset prefixes are C, D, E, B, W, L, A, S, P and O.

    python3 mask.py FILE   prints FILE's text masked
    leaks(text)            what may still tell the condition after masking, for review before grading

Standard library only.
"""

import re
import sys

ID = r"[CDEBWLASPO]\d+(?:\.(?:[TRr]\d+|statement|definition|tables))*(?:\s+r\d+\b)?"
ITEM_WORDS = (r"claims?|definitions?|evidence|warrants?|limitations?|artefacts?|artifacts?|references?|sources?|"
              r"steps?|items?|entr(?:y|ies)|rows?")
ITEM = re.compile(rf"\b(?:(?i:{ITEM_WORDS})\s+)?(?<![\w.]){ID}\b(?![\w(])")
PARAGRAPH = re.compile(r"\[\s*p\d+(?:\.\d+)*(?:\s*[-–,]\s*p?\d+(?:\.\d+)*)*\s*\]")
# A locator's number: 3, 4.2, 2b, S1, A.2, (12), IV; never a decimal such as 0.812 (figures as numbers).
NUMBER = r"(?-i:\([1-9]\d*(?:\.\d+)*[a-z]?\)|[A-Z]?[1-9]\d*(?:\.\d+)*[a-z]?(?:\([a-z]\))?|[A-Z](?:\.\d+)+|[IVX]+\b)"
NUMBERS = rf"{NUMBER}(?:\s*(?:[-–—/,&]|\band\b|\bto\b|\bor\b)\s*{NUMBER})*"
PART_WORDS = (r"pages?|pp?\.|sections?|sects?\.|§+|tables?|tabs?\.|figures?|figs?\.|appendi(?:x|ces)|app\.|"
              r"equations?|eqs?\.|eqn\.?|definitions?|defs?\.|theorems?|thms?\.|propositions?|props?\.|lemmas?|"
              r"corollar(?:y|ies)|remarks?|examples?|assumptions?|algorithms?|footnotes?|lines?|paragraphs?|paras?\.")
PART = re.compile(rf"(?<![\w-])(?:{PART_WORDS})\s*{NUMBERS}(?!\.?\w)", re.I)
APPENDIX = re.compile(r"\bappendi(?:x|ces)\s+(?-i:[A-Z])\b(?:\s*(?:and|,)\s*(?-i:[A-Z])\b)*", re.I)
SECTION_SIGN = re.compile(rf"§+\s*{NUMBERS}")
FORM = re.compile(r"(?:(?<!\w)\.txt|\b(?:claim[- ]?set|reading[- ]view|PDF|pdf|txt|plain[- ]text|text))(?:\s+(?:file|document|"
                  r"version|view|format|record))?\b|(?<=\bthis )record\b|(?<=\bthe )record\b(?= (?:says|"
                  r"states|does|gives|lists|reports|notes|records))", re.I)
FORM_STRICT = re.compile(r"\b(?:claim[- ]?sets?|reading[- ]views?|PDFs?|\.?txt)\b", re.I)
FILE_NAME = re.compile(r"`?[\w.-]+\.(?:claimset\.txt|pdf|txt|md|json)\b`?", re.I)
FILE_REF = re.compile(r"\[file:[^\]]*\]")
# A claimset's own citation of itself, entrylib:2026.000003@v4#C12, or a link to its page.
ENTRYLIB = re.compile(r"(?:https?://)?(?:entrylib\.org/\S*|entrylib:[\w.@#-]*\w)", re.I)
APP_TAG = re.compile(r"</?(?:FileCite|grok-card)\b[^>]*>", re.I)
# A citation that is only locations, in brackets: "(C3)", "(see [p3.2], Table 2)", "[C4; L2]"; dropped whole.
CITATION = re.compile(r"\s*[(\[](?:\s*(?:see|cf\.?|per|in|from|also|e\.g\.,?|and|or|[,;&/–-])?\s*\[location\])+\s*[)\]]")
# The reading view's section headings, written in capitals ("the EVIDENCE tables"), put in lower case.
HEADING = re.compile(r"\b(?:CLAIMS|DEFINITIONS|EVIDENCE|WARRANTS|LIMITATIONS|ARTEFACTS|REFERENCES|CORRECTIONS|SECTIONS)\b")
RUN = re.compile(r"\[location\](?:\s*(?:,|;|&|/|\band\b|\bor\b|[-–—])\s*\[location\])+")


def form(m):
    """'the PDF', 'the .txt file', 'this claimset' -> 'the paper'; a bare 'text' is left alone."""
    word = m.group(0)
    if re.fullmatch(r"(?:plain[- ])?text", word, re.I):
        return word
    return "paper"


def mask(text):
    text = APP_TAG.sub("", text)
    text = FILE_REF.sub("", text)
    text = ENTRYLIB.sub("[location]", text)
    text = FILE_NAME.sub("", text)
    text = PARAGRAPH.sub("[location]", text)
    text = PART.sub("[location]", text)
    text = APPENDIX.sub("[location]", text)
    text = ITEM.sub("[location]", text)
    text = SECTION_SIGN.sub("[location]", text)
    text = re.sub(r"\b(?:plain[- ])?text\s+file\b", "paper", text, flags=re.I)
    text = FORM.sub(form, text)
    text = re.sub(rf"(?<![\w-])(?:{PART_WORDS}|{ITEM_WORDS})\s*\[location\]", "[location]", text, flags=re.I)
    text = RUN.sub("[location]", text)
    text = CITATION.sub("", text)
    text = re.sub(r"\(\[location\][:;,]\s*", "(", text)  # "([location]: 0.89-1.26)" -> "(0.89-1.26)"
    text = re.sub(r"\s*[,;]\s*\[location\](?=\s*\))", "", text)  # "(0.99 + 0.98i, [location])" -> "(0.99 + 0.98i)"
    text = re.sub(r"\*\*\[location\]:?\*\*:?[ \t]*", "", text)  # a bold label that is only a location
    text = HEADING.sub(lambda m: m.group(0).lower(), text)
    text = re.sub(r"\bpaper\s*\(\s*(?:the\s+)?paper\s*\)|\bpaper\s+paper\b", "paper", text)
    text = re.sub(r"\(\s*\)|\[\s*\]|``", "", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r" +([,.;:)])", r"\1", text)
    return text


LEAK = re.compile(rf"(?<![\w.]){ID}\b(?!\()|\bp\d+\.\d+\b|claim[- ]?set|reading[- ]view|\bpdf\b|\btxt\b|\brecord\b|"
                  r"\bwarrant|\bartefact|\bpage\b|\bsection\b|\btable\b|\bfigure\b|\bappendix\b|\bequation\b|"
                  r"\bfile\b|\bupload|\battach|\bdocument\b|\btext\b|\bdefinitions?\b|\bevidence\b|\blimitations?\b|"
                  r"\bentry\b|\bmarker|\bsource\b|entrylib|\bclaims?\b|\bstatement\b", re.I)


def leaks(text, width=40):
    """[(match, context)] of what may still tell the condition in a masked text."""
    return [(m.group(0), text[max(0, m.start() - width):m.end() + width].replace("\n", " "))
            for m in LEAK.finditer(text)]


if __name__ == "__main__":
    print(mask(open(sys.argv[1], encoding="utf-8").read()))
