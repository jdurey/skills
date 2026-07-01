#!/usr/bin/env python3
"""lint.py — deterministic first pass for the ai-proof skill.

Does the part of ai-proofing that has ONE right answer, so the model never has to spend judgment
(or forget) on it: AUTO-FIXES the hard bans, and FLAGS the judgment calls with line numbers for the
model to rewrite. It is content-agnostic and never adds claims, numbers, or URLs.

AUTO-FIX (applied):
  • em/en dashes  ' — ' → ', '   (and tight —/– → ', ')
  • quiet / quietly  (Category 7 hard ban) → removed, spacing repaired
FLAG (reported, NOT changed — these need a human/model rewrite):
  • power-drained vocabulary (crucial, robust, leverage, delve, tapestry, seamless, …)
  • formal transitions (Furthermore, Moreover, Therefore, …)
  • hedge openers / meta-commentary ("It's worth noting", "In this post", "Let's unpack")
  • AI slop openers / frames ("I keep catching myself…", "Here's why…", "The thing is…",
      intrigue frames "the part nobody warns you about", appositive "the kind where…",
      fake landings "that's the whole idea", softener "and honestly,")
  • pseudo-cleft reframes ("What I've gotten better at is …" → "I've gotten better at …")
  • rhythm slop ("just as sure, just as wrong"; "First I … then I …"; "X, not Y"; adverb echoes)
  • manufactured symmetry — antithesis both same-sentence ("not X, it's Y") AND across a
      sentence boundary ("X isn't A. It's B." / "They aren't A. They're B."); "not only … but also"
  • anaphora runs (3+ consecutive sentences with the same opening word)
  • low burstiness (5+ consecutive sentences all 10–20 words — too even)
  • readability: Flesch-Kincaid grade (always reported; FLAGGED outside the 6–9 band, sweet spot ~8)

Usage:
  lint.py FILE [--write]     # report to stdout; --write applies the autofix back to FILE
  lint.py < text             # read stdin; prints report then '---AUTOFIXED---' then the fixed text
  lint.py FILE --json        # {autofixed, flags:[{line,type,snippet,fix}], counts}
"""
import argparse, json, re, sys

VOCAB = [
    "ensure", "delve", "crucial", "critical", "essential", "vital", "significant", "meaningful",
    "impactful", "powerful", "utilize", "leverage", "facilitate", "robust", "innovative",
    "cutting-edge", "comprehensive", "nuanced", "multifaceted", "tapestry", "holistic", "empower",
    "seamless", "seamlessly", "game-changer", "paradigm shift", "best practices", "moving forward",
    "thought leadership", "dive into", "unpack", "in today's world", "in today's landscape",
    "sit with",  # therapy/AI cliché — "sit with your output / the discomfort / it"; name the actual action
]
TRANSITIONS = ["Furthermore", "Moreover", "Additionally", "In conclusion", "Therefore", "Thus",
               "Hence", "Consequently", "Nevertheless", "Nonetheless", "Notwithstanding"]
HEDGES = ["it's worth noting", "it is worth noting", "it's important to", "it is important to",
          "it should be noted", "one thing to keep in mind", "as we can see", "it goes without saying"]
META = ["in this post", "in this article", "in this piece", "in this essay", "let's unpack",
        "let's explore", "let's take a closer look", "let's dive", "here's the thing"]
# Category 8 — AI slop: formulaic openers / frames AI reaches for to manufacture a hook
# or a fake "and here's the striking part" turn.
SLOP = ["i keep catching myself", "i catch myself", "i keep finding myself", "i found myself",
        "i keep coming back to", "here's why", "here is why", "here's what", "here's how",
        "here's the part", "here's the kicker", "the thing is",
        # manufactured-significance turns ("and the part that still gets me: …")
        "the part that gets me", "the part that still gets me", "what gets me", "what still gets me",
        "the part that kills me", "what kills me", "the part that surprises me", "what surprises me",
        "the wild part", "the crazy part", "the best part is", "the funny thing is", "the kicker is",
        # intrigue frames — promise a secret instead of delivering the content
        "the part nobody", "nobody warns you", "nobody tells you", "no one tells you",
        "no one warns you", "what they don't tell you", "what nobody tells you",
        "what they never tell you", "the part they don't",
        # "the kind where / the kind that" appositive elaboration cliché
        "the kind where", "the kind that", "the sort where", "the sort that", "the kind of thing where",
        # fake summative landings — narrator announces the takeaway
        "that's the whole idea", "that's the whole point", "that's the entire point",
        "that's the real point", "that's the beauty of", "that's the magic of", "that's the trick",
        "that's the whole thing", "that's the point, really", "and that's the idea",
        # confessional softener used as an opener (bare "honestly" stays allowed — a real candor signal)
        "and honestly,", "but honestly,", "honestly, that's", "honestly, it's",
        # announce-the-significance frames — narrator telegraphs a mic-drop instead of landing it.
        # "But that's the uncomfortable part." / "This is the part I can't get past." /
        # "the broader lesson is worth saying out loud." Just deliver the thing.
        "the uncomfortable part", "the part i can't get past", "the part i keep coming back to",
        "the broader lesson", "the bigger lesson", "the real lesson", "the broader point",
        "the bigger picture here", "worth saying out loud", "worth stating plainly",
        "the part that matters here"]

# manufactured-antithesis halves ("X isn't A, it's B" / "They aren't A. They're B.")
# NEG = the negated setup; AFF = the affirmative copula that re-describes the same subject.
_ANTI_NEG = (r"(it'?s not|it is not|that'?s not|that is not|they'?re not|they are not"
             r"|is not|are not|was not|were not|isn'?t|aren'?t|wasn'?t|weren'?t|not just)")
_ANTI_AFF = r"(it'?s|it is|they'?re|they are|that'?s|that is)"


def _syllables(w):
    w = re.sub(r"[^a-z]", "", w.lower())
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", w)
    w = re.sub(r"^y", "", w)
    return max(1, len(re.findall(r"[aeiouy]{1,2}", w)))


def fk_grade(text):
    """Flesch-Kincaid grade level + reading ease. Hard target: grade < 10 (adult, but not a chore).
    Depth lives in the IDEAS; FK only measures surface (sentence length + syllables/word)."""
    text = re.sub(r"https?://\S+", "link", text)
    sents = [s for s in re.split(r"(?<=[.!?])\s+", text.replace("\n", " ")) if s.strip()]
    words = re.findall(r"[A-Za-z']+", text)
    if not words or not sents:
        return None
    W, S = len(words), len(sents)
    syl = sum(_syllables(w) for w in words)
    grade = 0.39 * (W / S) + 11.8 * (syl / W) - 15.59
    ease = 206.835 - 1.015 * (W / S) - 84.6 * (syl / W)
    return {"grade": round(grade, 1), "ease": round(ease), "wps": round(W / S, 1), "spw": round(syl / W, 2)}


def autofix(text):
    n_dash = len(re.findall(r" [—–] |[—–]", text))
    text = re.sub(r" [—–] ", ", ", text)
    text = text.replace("—", ", ").replace("–", ", ")
    n_quiet = len(re.findall(r"(?i)\bquiet(ly)?\b", text))
    text = re.sub(r"(?i)\bquietly\b", "", text)
    text = re.sub(r"(?i)\bquiet\b ", "", text)
    text = re.sub(r"(?i) \bquiet\b", "", text)
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r" ([,.;:])", r"\1", text)
    return text, n_dash, n_quiet


def flags(text):
    out = []
    lines = text.splitlines()
    for i, ln in enumerate(lines, 1):
        low = ln.lower()
        for w in VOCAB:
            for m in re.finditer(r"\b" + re.escape(w) + r"\b", ln, re.I):
                out.append({"line": i, "type": "vocab", "snippet": w,
                            "fix": "name the specific thing, or cut it"})
        for w in TRANSITIONS:
            if re.search(r"\b" + re.escape(w) + r"\b", ln):
                out.append({"line": i, "type": "transition", "snippet": w,
                            "fix": "replace with 'And'/'But'/'So' or just start the sentence"})
        for h in HEDGES + META:
            if h in low:
                out.append({"line": i, "type": "hedge/meta", "snippet": h,
                            "fix": "delete the opener, start with the actual statement"})
        for s in SLOP:
            if s in low:
                out.append({"line": i, "type": "slop", "snippet": s,
                            "fix": "cut the formulaic opener/frame; start with the actual statement"})
        # manufactured antithesis. Two forms, both flagged:
        #   same sentence:  "X isn't A, it's B"
        #   across ONE sentence boundary:  "X isn't A. It's B." / "They aren't A. They're B."
        # The cross-sentence form is the common one and is what slipped through the Grok post —
        # the old single-sentence regex stopped at the '.' and never saw the affirmative half.
        if re.search(r"\b" + _ANTI_NEG + r"\b[^.?!]{1,40}\b" + _ANTI_AFF + r"\b", low) or \
           re.search(r"\b" + _ANTI_NEG + r"\b[^.?!]{0,70}[.?!]+\s+" + _ANTI_AFF + r"\b", low):
            out.append({"line": i, "type": "symmetry", "snippet": "not X, it's Y (manufactured antithesis)",
                        "fix": "break the balance — two separate claims, or drop one side; "
                               "the cross-sentence 'X isn't A. It's B.' form counts too"})
        if re.search(r"\bnot only\b[^.?!]{1,60}\bbut also\b", low):
            out.append({"line": i, "type": "symmetry", "snippet": "not only … but also",
                        "fix": "rewrite as one direct claim"})
        # pseudo-cleft reframe — "What I('ve) X is Y" / "What matters/changed is Y"
        # anchored to clause start so a mid-sentence relative clause ("audit what they hand you")
        # is NOT a false positive.
        if re.search(r"(?:^|[.!?]\s+)what (i|i've|i have|we|we've|you|they|matters|changed|happened|got better)\b"
                     r"[^.?!]{1,60}\bis\b", low):
            out.append({"line": i, "type": "cleft", "snippet": "What … is … (pseudo-cleft reframe)",
                        "fix": "state it directly — 'I've gotten better at X', not 'What I've gotten better at is X'"})
        # --- rhythm slop: the balanced/punchy cadence the burstiness rule can ACCIDENTALLY induce ---
        # manufactured doubled echo — "just as sure, just as wrong" / "more X, more Y"
        if re.search(r"\bjust as \w+,?\s+just as \w+", low) or re.search(r"\b(no|the) \w+,?\s+no \w+\.", low):
            out.append({"line": i, "type": "parallelism", "snippet": "doubled 'just as …, just as …'",
                        "fix": "drop the echo; say it once, plainly"})
        # enumeration scaffolding — "First I … then I …"
        if re.search(r"\bfirst,?\s+i\b.{0,120}\bthen,?\s+i\b", low):
            out.append({"line": i, "type": "scaffold", "snippet": "First I … then I …",
                        "fix": "cut the first/then scaffolding; just say what you do"})
        # "X, not Y" antithesis (a quieter cousin of "it's not X, it's Y")
        if re.search(r",\s+not\s+(the|a|an|one|because|to|by)\b", low):
            out.append({"line": i, "type": "antithesis", "snippet": "X, not Y contrast",
                        "fix": "the 'X, not Y' swing is an AI rhythm; make it one plain claim"})
        # quantifier swing — "Almost everyone can X. Far fewer people can Y." A cross-sentence
        # antithesis built from quantifiers; reads earned, but it's the same manufactured balance.
        if re.search(r"\balmost (every|everyone|anyone|all|nobody|no one)\b[^.?!]{0,80}[.?!]\s+"
                     r"(far fewer|fewer|few|hardly|almost no|most people|the rest)\b", low):
            out.append({"line": i, "type": "symmetry", "snippet": "quantifier swing (almost everyone … / far fewer …)",
                        "fix": "drop the 'almost everyone X / far fewer Y' contrast; state the point once, plainly"})
        # imperative reversal — "Don't ask whether it works. Ask someone to prove it doesn't."
        # A negated imperative followed by the SAME verb as a positive imperative. Manufactured pivot.
        m_rev = re.search(r"\b(?:don'?t|do not|never)\s+(\w+)\b[^.?!]{0,80}[.?!]\s+\1\b", low)
        if m_rev:
            out.append({"line": i, "type": "antithesis",
                        "snippet": f"imperative reversal ('don't {m_rev.group(1)} … {m_rev.group(1)} …')",
                        "fix": "the 'Don't X. X-instead' reversal is an AI rhythm; give one straight instruction"})
        # adverb echo for balance — "differently … differently", "quickly … quickly"
        em = re.search(r"\b(\w{5,}ly)\b[^.?!]{0,50}\b\1\b", low)
        if em:
            out.append({"line": i, "type": "echo", "snippet": f"'{em.group(1)}' repeated for rhythm",
                        "fix": "don't echo the same adverb to balance a sentence; reword one side"})
    # anaphora + burstiness over sentences
    sents = re.split(r"(?<=[.?!])\s+", re.sub(r"\s+", " ", text).strip())
    sents = [s for s in sents if s]
    openers, run = [], 1
    for s in sents:
        w = re.match(r"\W*(\w+)", s)
        openers.append(w.group(1).lower() if w else "")
    for k in range(2, len(openers)):
        if openers[k] and openers[k] == openers[k - 1] == openers[k - 2]:
            out.append({"line": 0, "type": "anaphora", "snippet": f"3+ sentences open with '{openers[k]}'",
                        "fix": "change the third opener (subordinate clause, time marker, or flip subject/verb)"})
    counts = [len(s.split()) for s in sents]
    streak = 0
    for c in counts:
        streak = streak + 1 if 10 <= c <= 20 else 0
        if streak == 5:
            out.append({"line": 0, "type": "burstiness", "snippet": "5+ sentences all 10–20 words",
                        "fix": "vary rhythm by saying it more plainly — do NOT bolt on a terse contrast punch "
                               "('X. But not Y.') or a balanced echo; that's its own AI tell (see SKILL 3n)"})
            streak = 0
    # readability — hard target BAND: Flesch-Kincaid grade 6–9 (sweet spot ~8).
    # Adult audience: not a chore (>=10) and not clipped/childish (<6). Depth lives in the ideas.
    fk = fk_grade(text)
    if fk and fk["grade"] >= 10:
        out.append({"line": 0, "type": "readability",
                    "snippet": f"Flesch-Kincaid grade {fk['grade']} — too dense (target 6–9; {fk['wps']} words/sentence)",
                    "fix": "shorten sentences and swap multi-syllable words for plain ones; keep the ideas, simplify the surface"})
    elif fk and fk["grade"] < 6:
        out.append({"line": 0, "type": "readability",
                    "snippet": f"Flesch-Kincaid grade {fk['grade']} — too simple/choppy (target 6–9)",
                    "fix": "reads clipped for adults; combine some short sentences and use a few more precise words, without padding"})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    src = open(a.file).read() if a.file else sys.stdin.read()

    fixed, n_dash, n_quiet = autofix(src)
    fl = flags(fixed)  # flag against the autofixed text so removed markers aren't re-reported

    if a.json:
        print(json.dumps({"autofixed": fixed, "flags": fl,
                          "counts": {"em_dashes_fixed": n_dash, "quiet_removed": n_quiet,
                                     "flags": len(fl)}}, ensure_ascii=False))
        return
    if a.write and a.file:
        open(a.file, "w").write(fixed)

    print(f"AUTOFIX: {n_dash} dash(es) → comma, {n_quiet} quiet/quietly removed"
          + (f"  [written to {a.file}]" if a.write and a.file else ""))
    _fk = fk_grade(fixed)
    if _fk:
        mark = "✓" if 6 <= _fk["grade"] < 10 else "✗ (target band 6–9)"
        print(f"READABILITY: Flesch-Kincaid grade {_fk['grade']} {mark}  ·  reading ease {_fk['ease']}  ·  {_fk['wps']} words/sentence")
    if fl:
        print(f"\nFLAGS — {len(fl)} item(s) need a judgment rewrite (the model's job):")
        for f in fl:
            loc = f"L{f['line']}" if f["line"] else "—"
            print(f"  {loc:>5} [{f['type']}] {f['snippet']}  →  {f['fix']}")
    else:
        print("\nFLAGS: none. Clean after autofix.")
    if not a.write:
        print("\n---AUTOFIXED---")
        print(fixed)


if __name__ == "__main__":
    main()
