"""
sd-webui-base-weight  –  BASE= syntax for prompt emphasis

Lets you set a base attention weight that all subsequent tags are relative to:

    BASE=0.8 cat, (dog:1.5), BASE=1.2 bird, [fish]

Instead of typing (tag:W) on every token, BASE adjusts the whole segment:

  •  Base 0.8:  cat → 0.8,  dog → 0.8+(1.5-1.0)=1.3
  •  Base 1.2:  bird → 1.2,  fish → 1.2+(0.909-1.0)=1.109

Place in  extensions/sd-webui-base-weight/scripts/base_weight.py
"""

import re

from modules import scripts, shared
from modules.prompt_parser import parse_prompt_attention

# ── regexes ───────────────────────────────────────────────────────────────

RE_BASE = re.compile(r'\b[Bb][Aa][Ss][Ee]\s*=\s*([+-]?(?:\d+\.?\d*|\.\d+))\b')
RE_AND = re.compile(r'(\s*\bAND\b\s*)')
RE_LEAD_WS = re.compile(r'^(\s+)')

# ── core logic ────────────────────────────────────────────────────────────


def apply_base_weight(prompt: str) -> str:
    """Scan *prompt* for ``BASE=X`` markers, strip them and rewrite weights.

    AND segments are processed independently so the reconstructed weights
    never cross AND boundaries (which would break the engine's AND split).
    """
    # ── split on AND, process each segment independently ────────────
    parts = RE_AND.split(prompt)
    if len(parts) == 1:
        return _process_base(prompt)

    result: list[str] = []
    for part in parts:
        if RE_AND.fullmatch(part):
            result.append(part)          # keep the AND delimiter as-is
        else:
            result.append(_process_base(part))
    return "".join(result)


def _process_base(text: str) -> str:
    """Strip BASE markers from *text*, rewrite weights, return new string."""
    parts = RE_BASE.split(text)
    if len(parts) == 1:                     # no BASE markers
        return text

    chunks: list[str] = []

    # ── text before the first BASE marker  (default base = 1.0) ────
    chunks.append(_adjust_segment(parts[0], 1.0))

    # ── every pair (base_value, text_after) ─────────────────────────
    for i in range(1, len(parts), 2):
        base = float(parts[i]) if parts[i] else 1.0
        text_after = parts[i + 1] if i + 1 < len(parts) else ""

        # preserve leading whitespace unchanged (it's just a separator)
        ws = _consume_leading_ws(text_after)
        if ws:
            chunks.append(ws)
            text_after = text_after[len(ws):]

        chunks.append(_adjust_segment(text_after, base))

    return "".join(chunks)


def _consume_leading_ws(text: str) -> str:
    """Return leading whitespace of *text*, or empty string."""
    m = RE_LEAD_WS.match(text)
    return m.group(1) if m else ""


def _adjust_segment(text: str, base: float) -> str:
    """Parse *text*, shift every token weight relative to *base*, reconstruct."""
    if not text:
        return text

    parsed = parse_prompt_attention(text)
    out_parts: list[str] = []

    for token, weight in parsed:
        # ── BREAK: preserve verbatim (it's a special delimiter) ────
        if token == "BREAK":
            out_parts.append(" BREAK ")
            continue

        # additive offset: a token that was normally 1.3 keeps +0.3
        new_w = base + (weight - 1.0)

        if abs(new_w - 1.0) < 1e-6:
            out_parts.append(token)
        else:
            out_parts.append(f"({token}:{new_w:.4g})")

    return "".join(out_parts)


# ── Script that hooks into the processing pipeline ────────────────────────


class Script(scripts.Script):
    def title(self):
        return "Base Weight"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def process(self, p, *args):
        # Skip if user has emphasis disabled entirely – weights are ignored
        if getattr(shared.opts, "emphasis", "Original") == "None":
            return

        for i, prompt in enumerate(p.all_prompts):
            p.all_prompts[i] = apply_base_weight(prompt)

        for i, prompt in enumerate(p.all_negative_prompts):
            p.all_negative_prompts[i] = apply_base_weight(prompt)

        hr_prompts = getattr(p, "all_hr_prompts", None)
        if hr_prompts is not None:
            for i, prompt in enumerate(hr_prompts):
                p.all_hr_prompts[i] = apply_base_weight(prompt)

        hr_neg_prompts = getattr(p, "all_hr_negative_prompts", None)
        if hr_neg_prompts is not None:
            for i, prompt in enumerate(hr_neg_prompts):
                p.all_hr_negative_prompts[i] = apply_base_weight(prompt)
