"""Run-Aware Text Replacer Engine for DOCX.

Provides boundary-safe search and replacement across multiple Word runs (<w:r>)
within a paragraph, preserving font styles and document formatting.
"""

import re
from typing import List, Tuple
from docx.text.paragraph import Paragraph


def build_boundary_regex(target: str) -> re.Pattern:
    r"""Builds a boundary-safe regular expression for the target text.
    
    Prevents unintended substring matches (BR-009), e.g. '12345' matching '9123456'.
    Uses word boundary assertions (?<!\w) and (?!\w).
    """
    escaped = re.escape(target)
    # Check if target starts/ends with alphanumeric characters
    prefix = r"(?<!\w)" if target and target[0].isalnum() else ""
    suffix = r"(?!\w)" if target and target[-1].isalnum() else ""
    pattern = f"{prefix}{escaped}{suffix}"
    return re.compile(pattern)


def count_matches_in_paragraph(paragraph: Paragraph, target: str) -> int:
    """Counts the occurrences of target in a paragraph, searching across runs."""
    if not target or not paragraph.runs:
        return 0

    full_text = "".join(r.text for r in paragraph.runs)
    if not full_text:
        return 0

    pattern = build_boundary_regex(target)
    return len(pattern.findall(full_text))


def count_matches_in_text(text: str, target: str) -> int:
    """Counts boundary-safe matches of target in plain text."""
    if not target or not text:
        return 0
    pattern = build_boundary_regex(target)
    return len(pattern.findall(text))


def replace_text_in_paragraph(paragraph: Paragraph, target: str, replacement: str) -> int:
    """Replaces all occurrences of target with replacement across runs in a paragraph.
    
    Preserves the formatting of the runs by:
    1. Mapping character offsets of the paragraph's combined text to specific runs.
    2. Placing the replacement text into the first overlapping run (inheriting its style).
    3. Truncating or clearing the target text from subsequent overlapping runs.
    
    Returns:
        int: Number of replacements made.
    """
    if not target or not paragraph.runs:
        return 0

    # Ensure target and replacement are treated strictly as strings
    target_str = str(target)
    replacement_str = str(replacement)

    runs = paragraph.runs
    full_text = "".join(r.text for r in runs)
    if not full_text:
        return 0

    pattern = build_boundary_regex(target_str)
    matches = list(pattern.finditer(full_text))
    if not matches:
        return 0

    # Process matches in reverse order so character offsets in earlier text remain valid
    for match in reversed(matches):
        match_start, match_end = match.span()

        # Calculate run boundaries in the current full_text
        current_runs = paragraph.runs
        run_bounds: List[Tuple[int, int]] = []
        offset = 0
        for r in current_runs:
            length = len(r.text)
            run_bounds.append((offset, offset + length))
            offset += length

        # Find which runs intersect [match_start, match_end)
        intersecting_indices = []
        for idx, (r_start, r_end) in enumerate(run_bounds):
            if max(match_start, r_start) < min(match_end, r_end):
                intersecting_indices.append(idx)

        if not intersecting_indices:
            continue

        first_idx = intersecting_indices[0]
        last_idx = intersecting_indices[-1]

        # Case 1: Match is entirely within a single run
        if first_idx == last_idx:
            r_start, _ = run_bounds[first_idx]
            run = current_runs[first_idx]
            local_start = match_start - r_start
            local_end = match_end - r_start
            run.text = run.text[:local_start] + replacement_str + run.text[local_end:]
        else:
            # Case 2: Match spans multiple runs
            # 1. Update the first run: keep text before match, add replacement
            r1_start, _ = run_bounds[first_idx]
            run1 = current_runs[first_idx]
            local_start = match_start - r1_start
            run1.text = run1.text[:local_start] + replacement_str

            # 2. Clear matched text from intermediate runs
            for mid_idx in intersecting_indices[1:-1]:
                current_runs[mid_idx].text = ""

            # 3. Update the last run: keep text after match
            rl_start, _ = run_bounds[last_idx]
            run_last = current_runs[last_idx]
            local_end = match_end - rl_start
            run_last.text = run_last.text[local_end:]

    return len(matches)
