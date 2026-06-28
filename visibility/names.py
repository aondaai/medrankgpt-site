from __future__ import annotations
import re
import unicodedata

_DROP = {"dr", "dra", "drs", "dras", "de", "da", "do", "dos", "das", "e"}

# "Dr./Dra. Nome [de] Sobrenome ..." — allows lowercase connectives (de/da/do/das/dos/e)
# between capitalized words so full names are captured as ONE span.
_NAME_RE = re.compile(
    r"\bDr[a]?s?\.?\s+[A-ZÀ-Ý][\wÀ-ÿ]+(?:\s+(?:d[aeo]s?\s+|e\s+)?[A-ZÀ-Ý][\wÀ-ÿ]+){0,3}")

def _norm(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower()

def tokens(name: str) -> set[str]:
    return {t for t in _norm(name).replace(".", " ").split() if t and t not in _DROP}

def same_person(a: set[str], b: set[str]) -> bool:
    """True if two token sets plausibly refer to the same doctor.
    Requires ≥2 shared tokens (first+last), avoiding cross-name false matches
    like 'Ana Silva' vs 'Ana Costa'. Single-token names match only if identical."""
    if not a or not b:
        return False
    if len(a & b) >= 2:
        return True
    if len(a) == 1 and len(b) == 1:
        return a == b
    return False

def mentioned_names(text: str) -> list[str]:
    """Distinct 'Dr./Dra. Nome' spans in first-seen order, whitespace-normalized."""
    seen: list[str] = []
    for raw in _NAME_RE.findall(text):
        name = re.sub(r"\s+", " ", raw).strip()
        if name not in seen:
            seen.append(name)
    return seen
