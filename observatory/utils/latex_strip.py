"""
LaTeX -> plain text stripper for RAG corpus building.
================================================================
Regex-based, not a real LaTeX parser (same "adequate MVP proxy" philosophy as
the char-count chunker already used for the markdown corpus in
rag_build_corpus.py). Maps \\section/\\subsection/\\subsubsection to
markdown-style ##/###/#### markers so the same heading-based chunking logic
can be reused, keeps figure/table \\caption text (the only semantically
useful part of those environments), inlines \\footnote text, and strips
formatting/layout commands down to their plain argument text.
"""
import re

_BALANCED_ARG = r"((?:[^{}]|\{[^{}]*\})*)"


def _strip_environment_keep_captions(text: str, envs: list[str]) -> str:
    for env in envs:
        pattern = re.compile(rf"\\begin\{{{env}\}}.*?\\end\{{{env}\}}", re.DOTALL)

        def _replace(match):
            caps = re.findall(rf"\\caption\{{{_BALANCED_ARG}\}}", match.group(0))
            return "\n".join(caps)

        text = pattern.sub(_replace, text)
    return text


def _strip_environment_drop(text: str, envs: list[str]) -> str:
    for env in envs:
        text = re.sub(rf"\\begin\{{{env}\*?\}}.*?\\end\{{{env}\*?\}}", "", text, flags=re.DOTALL)
    return text


def strip_latex(text: str) -> str:
    """Converts raw LaTeX source into plain, chunkable text."""
    # Line comments (unescaped %)
    text = re.sub(r"(?<!\\)%.*", "", text)

    # Figures/tables: keep only the caption, drop the raw markup/grid.
    text = _strip_environment_keep_captions(text, ["figure\\*?", "subfigure", "table\\*?"])

    # Raw table grids, equations, code listings, callout boxes: low retrieval
    # value as-is, drop entirely.
    text = _strip_environment_drop(text, ["tabular", "tabularx", "equation", "lstlisting", "tcolorbox"])

    # Footnotes carry real content (see the cGAN-limitation footnote) — inline.
    text = re.sub(rf"\\footnote\{{{_BALANCED_ARG}\}}", r" (Note: \1)", text)

    # Section headings -> markdown-style markers for the shared chunker.
    text = re.sub(r"\\section\*?\{([^}]*)\}", r"\n## \1\n", text)
    text = re.sub(r"\\subsection\*?\{([^}]*)\}", r"\n### \1\n", text)
    text = re.sub(r"\\subsubsection\*?\{([^}]*)\}", r"\n#### \1\n", text)

    # Formatting commands -> plain argument text.
    for cmd in ["textbf", "textit", "texttt", "emph", "text"]:
        text = re.sub(rf"\\{cmd}\{{{_BALANCED_ARG}\}}", r"\1", text)

    # Lists -> plain bullets.
    text = re.sub(r"\\begin\{(?:itemize|enumerate|description)\}(?:\[[^\]]*\])?", "", text)
    text = re.sub(r"\\end\{(?:itemize|enumerate|description)\}", "", text)
    text = re.sub(r"\\item\[([^\]]*)\]", r"\n- \1: ", text)
    text = re.sub(r"\\item\b", r"\n- ", text)

    # Labels/refs: labels have no retrieval value, refs get a neutral placeholder.
    text = re.sub(r"\\label\{[^}]*\}", "", text)
    text = re.sub(r"\\ref\{[^}]*\}", "[ref]", text)

    # Layout/formatting noise with no useful argument text.
    for cmd in ["centering", "noindent", "small", "sffamily", "newpage", "hfill"]:
        text = re.sub(rf"\\{cmd}\b", "", text)
    text = re.sub(r"\\vspace\{[^}]*\}", "", text)
    text = re.sub(r"\\rule\{[^}]*\}\{[^}]*\}", "", text)
    text = re.sub(r"\\(?:textwidth|linewidth)\b", "", text)

    # Escaped special characters.
    for esc, plain in [("\\&", "&"), ("\\%", "%"), ("\\_", "_"), ("\\#", "#"), ("\\$", "$")]:
        text = text.replace(esc, plain)

    # Collapse whitespace left behind by all the above.
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()


def chunk_latex(text: str, max_chars: int = 1500, overlap: int = 150):
    """Split on the ##/###/#### markers strip_latex() produced, then hard-cap
    any oversized section with overlap. Mirrors chunk_markdown()'s logic,
    extended to the 4th heading level (LaTeX \\subsubsection)."""
    clean = strip_latex(text)
    sections = re.split(r"\n(?=#{2,4}\s)", clean)
    chunks = []
    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue
        heading_match = re.match(r"#{2,4}\s*(.+)", sec)
        heading = heading_match.group(1).strip() if heading_match else ""
        if len(sec) <= max_chars:
            chunks.append((heading, sec))
        else:
            start = 0
            while start < len(sec):
                end = start + max_chars
                chunks.append((heading, sec[start:end]))
                if end >= len(sec):
                    break
                start = end - overlap
    return chunks
