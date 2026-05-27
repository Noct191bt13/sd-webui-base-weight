# sd-webui-base-weight

Set a base attention weight for groups of prompt tags.

Instead of typing `(tag:1.2)` on every single tag, write `BASE=1.2` once and every tag after it inherits that weight. Individual `(tag:W)` overrides are preserved as **offsets** from 1.0.

## Syntax

```
BASE=0.8 1girl, blue_eyes, (smile:1.5)
```

The `BASE=` marker is stripped from the prompt before it reaches the text encoder — it never pollutes your embedding.

## How it works

Weights are **additive offsets** from 1.0:

```
effective_weight = base + (explicit_weight - 1.0)
```

| Prompt | Effective weights |
|---|---|
| `BASE=0.8 cat, dog, bird` | cat=0.8, dog=0.8, bird=0.8 |
| `BASE=0.8 cat, (dog:1.5)` | cat=0.8, dog=0.8+(1.5-1.0)=**1.3** |
| `BASE=0.8 (cat), [dog]` | cat=0.8+0.1=**0.9**, dog=0.8-0.091=**0.709** |
| `BASE=1.2 (cat), [dog]` | cat=1.2+0.1=**1.3**, dog=1.2-0.091=**1.109** |
| `cat BASE=0.8 dog` | cat=1.0, dog=**0.8** |
| `BASE=0.8 cat BASE=1.2 dog` | cat=**0.8**, dog=**1.2** |
| `BASE=0.5 cat, (dog:0.5)` | cat=**0.5**, dog=0.5+(0.5-1.0)=**0.0** |

## With `AND` prompts

`BASE` is scoped to its `AND` segment. This avoids broken weight expressions across conditioning boundaries:

```
cat AND BASE=0.8 dog AND BASE=1.2 bird
```
→ cat=1.0, dog=0.8, bird=1.2

```
BASE=0.8 cat AND BASE=1.2 dog
```
→ cat=0.8, dog=1.2

If you want the same BASE across all AND segments, write it in each one.

## Works with

- Positive & negative prompts
- High-res pass prompts (txt2img hr fix)
- `(tag)` – emphasis, weight 1.1
- `(tag:W)` – explicit weight
- `[tag]` – de-emphasis, weight ~0.909
- `((tag))` – stacked emphasis
- `AND` – multi-condition prompts
- `BREAK` – chunk separator

## Does NOT conflict with

| Syntax | Used by |
|---|---|
| `{cat\|dog}` | dynamic-prompts (wildcards) |
| `<lora:name:w>` | extra networks |
| `[a:b:0.5]` | scheduled prompts |
| `[a\|b]` | alternate prompts |
| `(tag:W)` | emphasis (reconstructed with adjusted weights) |

## Install

**Option A – local copy** (simplest):

```bash
cd extensions/
mkdir sd-webui-base-weight
# copy scripts/base_weight.py into sd-webui-base-weight/scripts/
```

**Option B – git clone** (if you push it to GitHub):

```bash
cd extensions/
git clone https://github.com/Noct191bt13/sd-webui-base-weight.git
```

**Option C – single file**: just drop `base_weight.py` into any existing extension's `scripts/` folder.

No dependencies, no UI settings — works immediately after restarting the WebUI.

## What it looks like in use

Before (manual, error-prone):
```
1girl, (solo:1.2), (looking_at_viewer:1.2), (smile:1.2), (blue_eyes:1.2), (long_hair:1.2)
```

After (clean, adjustable):
```
BASE=1.2 1girl, solo, looking_at_viewer, smile, blue_eyes, long_hair
```

Want to tone it down? Change one number:
```
BASE=0.9 1girl, solo, looking_at_viewer, smile, blue_eyes, long_hair
```
