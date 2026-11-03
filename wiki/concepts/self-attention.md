---
title: Self-attention (in vision)
type: concept
sources: [arxiv_2010.11929, arxiv_2103.14030]
tags: [transformer, attention, computer-vision]
updated: 2026-11-03
status: draft
---

In self-attention, each token in a sequence computes weighted interactions
with other tokens (queries, keys and values). It is the core operation of the
Transformer. For images, the main difficulty is cost: global attention is
quadratic in the number of tokens. That has led to patch tokens (ViT) and
local windows (Swin).

## In the sources

- **Origin.** Transformers were proposed for machine translation and became
  the state of the art in NLP [src:arxiv_2010.11929 p.2].
- **Pixel-level attention is too costly.** Having every pixel attend to every
  other pixel is quadratic in the number of pixels and does not scale.
  Earlier work used local neighbourhoods, sparse approximations or axial
  attention [src:arxiv_2010.11929 p.2].
- **ViT.** Global multi-head self-attention over fixed-size image patches
  [src:arxiv_2010.11929 p.3]. For example, ViT-L/16 uses 16×16 patches
  [src:arxiv_2010.11929 p.5]. Its "attention distance", analogous to a
  CNN's receptive field, grows with depth [src:arxiv_2010.11929 p.8].
- **Swin.** Window-based attention, linear in the number of patches for a
  fixed window size M [src:arxiv_2103.14030 p.4], with windows shifted between
  layers [src:arxiv_2103.14030 p.2]. See [[shifted-window-attention]].
- **Hardware latency.** Sliding-window attention is slow on general hardware
  because each query has a different key set. Shifted windows share keys
  within a window [src:arxiv_2103.14030 p.2].

General knowledge, not from these sources: in the standard formulation,
attention is softmax(QKᵀ/√d)V. Both papers' equations were not decoded in the
extraction.

## Related

- [[vision-transformer]]
- [[shifted-window-attention]]
- [[inductive-bias-in-vision-models]]
- [[arxiv-2010-11929]]
- [[arxiv-2103-14030]]
