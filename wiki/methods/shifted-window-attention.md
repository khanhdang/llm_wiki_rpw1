---
title: Shifted window attention (Swin)
type: method
sources: [arxiv_2103.14030]
tags: [transformer, attention, computer-vision]
updated: 2026-11-03
status: draft
---

Shifted window attention computes self-attention within non-overlapping
M×M windows, so its cost is linear in image size. Successive layers shift the
window grid by ⌊M/2⌋, which connects neighbouring windows
[src:arxiv_2103.14030 p.4]. It is the core of Swin Transformer, combined with
patch merging to give a hierarchical, CNN-like feature pyramid
[src:arxiv_2103.14030 p.3].

## Details

- **Complexity.** Global multi-head self-attention is quadratic in the number
  of patches hw. Window attention is linear for fixed M, with M = 7 by
  default [src:arxiv_2103.14030 p.4].
- **Cross-window connections.** Without the shift, windows never exchange
  information, which limits modelling power [src:arxiv_2103.14030 p.4].
- **Cyclic shift with masking.** Lets the shifted layout be computed as
  efficiently as the regular one, without padding extra windows
  [src:arxiv_2103.14030 p.5].
- **Relative position bias.** A bias B is added inside each window, drawn
  from a (2M−1)×(2M−1) table [src:arxiv_2103.14030 p.5].
- **Latency.** All queries in a window share one key set, which suits
  hardware, unlike sliding windows [src:arxiv_2103.14030 p.2].

## Evidence (Swin-T ablations)

- **Shift vs no shift.** +1.1% ImageNet top-1, +2.8 box AP on COCO and +2.8
  mIoU on ADE20K [src:arxiv_2103.14030 p.8].
- **Shifted vs sliding windows.** About as accurate: 81.3% vs 81.4% top-1
  [src:arxiv_2103.14030 p.9], but 4.1× faster than a naive sliding-window
  implementation [src:arxiv_2103.14030 p.8].

## Related

- [[arxiv-2103-14030]]
- [[self-attention]]
- [[vision-transformer]]
- [[inductive-bias-in-vision-models]]
- [[arxiv-2201-03545]]
