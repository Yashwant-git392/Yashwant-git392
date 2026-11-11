"""Keyword-based complaint router + SLA matrix for Campus Shikayat Setu.

Design goals (kept deliberately simple and explainable for an MCA Sem-I demo):
* every category carries a keyword list; multi-word keywords weigh more;
* the title is weighted double (it usually carries the intent);
* mass-impact phrases bump priority one level; catastrophe words force High;
* if nothing matches, the complaint falls back to General & Administration.
"""
import re

SLA_HOURS = {"High": 24, "Medium": 72, "Low": 168}   # 24h / 72h / 7 days

# One regex, applied to lowercase text, used for both scoring and impact checks.
WORD_RE = re.compile(r"[a-z0-9][a-z0-9\-]*")

SAFETY_WORDS = (
    "ragging", "harass", "threat", "shock", "fire", "short circuit", "electrocut",
    "collapse", "unsafe", "injur", "assault", "leak gas",
)
MASS_IMPACT = (
    "entire", "whole", "everyone", "everybody", "all students", "all rooms",
    "all labs", "all classrooms", "mass", "common area", "everyone", "fully blocked",
)


def _word_count(s: str) -> int:
    return len(WORD_RE.findall(s))


def score_category(text: str, keywords: str) -> int:
    """Return the weighted keyword score of `keywords` against `text`."""
    score = 0
    low = text.lower()
    for kw in (k.strip().lower() for k in keywords.split(",") if k.strip()):
        # word-ish boundary search; substring-safe for phrases with spaces
        pattern = r"(?<![a-z0-9])" + re.escape(kw) + r"(?![a-z0-9])"
        hits = len(re.findall(pattern, low))
        if hits:
            weight = max(1, len(kw.split()) * 2)      # multi-word kws are more specific
            score += weight * hits
    return score


def route(text: str, categories) -> tuple[object, int]:
    """Pick the best category; returns (category, score).

    `categories` is an iterable of sqlite Rows with `keywords`.
    Deterministic tie-break: the category whose declaration came first wins
    only when scores are equal — category order in the seed is curated so that
    rarer/more specific categories are declared before generic ones.
    """
    best_cat, best_score = None, 0
    for cat in categories:
        s = score_category(text, cat["keywords"])
        if s > best_score:
            best_cat, best_score = cat, s
    return best_cat, best_score


def bump_priority(priority: str) -> str:
    return {"Low": "Medium", "Medium": "High", "High": "High"}[priority]


def assign_priority(default_priority: str, title: str, description: str) -> str:
    text = f"{title}. {description}".lower()
    if any(w in text for w in SAFETY_WORDS):
        return "High"
    p = default_priority
    if any(p_ in text for p_ in MASS_IMPACT):
        p = bump_priority(p)
    return p


def route_text(title: str, description: str) -> str:
    """Title counts double when scoring."""
    return f"{title}. {title}. {description}"
