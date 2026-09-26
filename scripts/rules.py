"""House copy rules (see references/content-rules.md), shared by build.py (checks page.json) and lint_output.py (checks dist/).

check_text(text) returns a list of Finding(level, code, message, excerpt).
level is "error" (build or lint fails) or "warn" (reported, does not fail).
"""
import re
from collections import namedtuple

Finding = namedtuple("Finding", "level code message excerpt")

EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U00002B00-\U00002BFF"
    "\U00002300-\U000023FF\U0000FE0F\U0000200D\U000020E3]"
)
FLAG_PAIR = re.compile("[\U0001F1E6-\U0001F1FF]{2}")
ARROW_CHARS = re.compile("[\u2190-\u21FF\u27F0-\u27FF\u2900-\u297F\u00BB\u203A]")
ARROW_TEXT = re.compile(r"(-->|->|<--|<-(?!-)|=>|&rarr;|&larr;|&raquo;|&rsaquo;|&#8594;)")
DASH_CHARS = re.compile("[\u2012\u2013\u2014\u2015]")
DASH_TEXT = re.compile(r"(&mdash;|&ndash;|&#8212;|&#8211;|\s--\s)")
CURLY = re.compile("[\u2018\u2019\u201A\u201B\u201C\u201D\u201E\u201F]")

# Words and phrases banned by the house style (stock AI vocabulary, inflation, verb avoidance).
BANNED = [
    r"additionally", r"align(?:s|ed)? with", r"bolster(?:s|ed|ing)?", r"crucial(?:ly)?",
    r"deep[- ]dive", r"delv(?:e|es|ed|ing)", r"emphasi[sz](?:e|es|ed|ing)", r"enduring",
    r"enhanc(?:e|es|ed|ing|ement|ements)", r"foster(?:s|ed|ing)?", r"garner(?:s|ed|ing)?",
    r"highlight(?:s|ed|ing)", r"interplay", r"intricate", r"intricac(?:y|ies)",
    r"landscapes?", r"meticulous(?:ly)?", r"pivotal", r"quietly", r"robust(?:ly|ness)?",
    r"showcas(?:e|es|ed|ing)", r"tapestr(?:y|ies)", r"testament", r"underscor(?:e|es|ed|ing)",
    r"valuable", r"vibrant", r"boast(?:s|ed|ing)?", r"breathtaking", r"nestled", r"stunning",
    r"renowned", r"diverse array", r"groundbreaking", r"serves as", r"stands as",
    r"functions as", r"operates as", r"at its core", r"fundamentally", r"what really matters",
    r"let(?:'s| us) dive in", r"here(?:'s| is) what you need to know", r"without further ado",
    r"real talk", r"look, here(?:'s| is) the thing", r"let that sink in", r"read that again",
    r"marking a new era", r"the future looks bright",
]
BANNED_RE = re.compile(r"\b(" + "|".join(BANNED) + r")\b", re.I)
WARN_WORDS_RE = re.compile(r"\b(key|highlight|seamless(?:ly)?|world-class|cutting-edge|unlock|elevate|empower(?:s|ing)?)\b", re.I)

CHATBOT_RE = re.compile(
    r"(certainly!|great question|i hope this helps|let me know if you need|would you like me to|sure, here is|sure, here's|honestly\?)",
    re.I,
)
NOT_X_BUT_Y = [
    re.compile(r"\bnot (?:just|only|merely|simply)\b", re.I),
    re.compile(r"\bisn't (?:just|only|merely|about)\b", re.I),
    re.compile(r"\b(?:it's|it is|this is|that's|that is) not (?:about|just|a|an)\b[^.!?]{0,80}\b(?:it's|it is|but)\b", re.I),
    re.compile(r"\bdoes(?: not|n't) mean\b[^.!?]{0,60}[.;]\s*it means\b", re.I),
]


def _excerpt(text, m, width=28):
    a = max(0, m.start() - width)
    b = min(len(text), m.end() + width)
    return text[a:b].replace("\n", " ").strip()


def check_text(text, check_arrow_text=True):
    """Check one piece of user-visible copy."""
    out = []
    if not text:
        return out
    for m in FLAG_PAIR.finditer(text):
        out.append(Finding("error", "emoji-flag", "Emoji flag found. Use a flag field so the SVG flag is rendered.", _excerpt(text, m)))
    for m in EMOJI.finditer(text):
        out.append(Finding("error", "emoji", "Emoji or pictograph U+%04X found. Remove it; icons come from icon fields." % ord(m.group()), _excerpt(text, m)))
    for m in ARROW_CHARS.finditer(text):
        out.append(Finding("error", "arrow", "Arrow character U+%04X found. Remove it; buttons and links add the SVG arrow themselves." % ord(m.group()), _excerpt(text, m)))
    if check_arrow_text:
        for m in ARROW_TEXT.finditer(text):
            out.append(Finding("error", "arrow", "Text arrow '%s' found. Remove it; buttons and links add the SVG arrow themselves." % m.group(), _excerpt(text, m)))
    for m in DASH_CHARS.finditer(text):
        out.append(Finding("error", "dash", "Em dash or en dash found. Use a comma, colon, parentheses or a plain hyphen for ranges (14-21).", _excerpt(text, m)))
    for m in DASH_TEXT.finditer(text):
        out.append(Finding("error", "dash", "Dash substitute '%s' found. Use a comma or colon instead." % m.group().strip(), _excerpt(text, m)))
    for m in CURLY.finditer(text):
        out.append(Finding("error", "curly-quote", "Curly quote found. Use straight quotes ' and \".", _excerpt(text, m)))
    for m in BANNED_RE.finditer(text):
        out.append(Finding("error", "banned-word", "Banned AI-style word '%s'. Rewrite with a plain verb or a concrete fact." % m.group(), _excerpt(text, m)))
    for m in CHATBOT_RE.finditer(text):
        out.append(Finding("error", "chatbot", "Chatbot phrase '%s'. Delete it." % m.group(), _excerpt(text, m)))
    for rx in NOT_X_BUT_Y:
        for m in rx.finditer(text):
            out.append(Finding("error", "not-x-but-y", "'Not X, but Y' framing. State the positive claim directly.", _excerpt(text, m)))
    for m in WARN_WORDS_RE.finditer(text):
        out.append(Finding("warn", "weak-word", "Weak or overused word '%s'. Prefer a concrete term." % m.group(), _excerpt(text, m)))
    return out


def check_raw_file(text):
    """Characters that must never appear anywhere in shipped files, code included."""
    out = []
    for rx, code, msg in (
        (EMOJI, "emoji", "Emoji in file"),
        (FLAG_PAIR, "emoji-flag", "Emoji flag in file"),
        (DASH_CHARS, "dash", "Em or en dash in file"),
        (CURLY, "curly-quote", "Curly quote in file"),
        (ARROW_CHARS, "arrow", "Unicode arrow in file"),
    ):
        for m in rx.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            out.append((line, Finding("error", code, msg, _excerpt(text, m))))
    return out
