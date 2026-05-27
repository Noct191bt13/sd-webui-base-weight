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
effective = base + (explicit_weight - 1.0)
```

| Prompt | Effective weights |
|---|---|
| `BASE=0.8 cat, dog` | cat=0.8, dog=0.8 |
| `BASE=0.8 cat, (dog:1.5)` | cat=0.8, dog=0.8+(1.5-1.0)=**1.3** |
| `BASE=0.8 (cat), [dog]` | cat=0.8+0.1=**0.9**, dog=0.8-0.091=**0.709** |
| `cat BASE=0.8 dog` | cat=1.0, dog=**0.8** |
| `BASE=0.8 cat BASE=1.2 dog` | cat=**0.8**, dog=**1.2** |
| `BASE=0.5 cat, (dog:0.5)` | cat=**0.5**, dog=0.5+(0.5-1.0)=**0.0** |

## Examples

Before — applying the same weight to every tag:
```
1girl, (solo:1.2), (looking_at_viewer:1.2), (smile:1.2), (blue_eyes:1.2)
```

After — one number controls the whole group:
```
1girl, BASE=1.2 solo, looking_at_viewer, smile, blue_eyes
```
Tags before the first `BASE=` stay at default weight (1.0).

If you want 1girl at 1.2 too, just move `BASE` to the front:
```
BASE=1.2 1girl, solo, looking_at_viewer, smile, blue_eyes
```

Want to tone down the whole prompt? Change one number:
```
BASE=0.9 1girl, solo, looking_at_viewer, smile, blue_eyes
```

## Install

- **From the WebUI**: go to Extensions → Install from URL, paste `https://github.com/Noct191bt13/sd-webui-base-weight.git`
- **Manually**: `git clone https://github.com/Noct191bt13/sd-webui-base-weight.git` inside your `extensions/` folder
