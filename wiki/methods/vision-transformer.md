---
title: Vision Transformer (ViT)
type: method
sources: [arxiv_2010.11929, arxiv_2103.14030]
tags: [transformer, computer-vision, architecture]
updated: 2026-11-03
status: draft
---

A Vision Transformer splits an image into fixed-size patches, linearly embeds
each one as a token, adds position embeddings and a class token, and feeds
the sequence to a standard Transformer encoder [src:arxiv_2010.11929 p.3]. It
uses almost no image-specific inductive bias and needs large-scale
pre-training to beat CNNs [src:arxiv_2010.11929 p.2].

## Recipe

- **Patch embedding.** N = HW/P² patches, each flattened and projected to
  dimension D [src:arxiv_2010.11929 p.3].
- **Tokens and positions.** A [class] token whose final state feeds the
  classifier, plus learnable 1D position embeddings
  [src:arxiv_2010.11929 p.3].
- **Encoder.** Alternating multi-head self-attention and GELU MLP blocks,
  each with LayerNorm before and a residual connection after
  [src:arxiv_2010.11929 p.3] [src:arxiv_2010.11929 p.4].
- **Fine-tuning at a new resolution.** Keep the patch size and interpolate
  the position embeddings in 2D [src:arxiv_2010.11929 p.4].
- **Sizes.** B (86M), L (307M) and H (632M) parameters
  [src:arxiv_2010.11929 p.5].

## Strengths and weaknesses (from the sources)

- **Strength: scale.** With JFT-300M pre-training it matches or beats CNNs at
  2–4× less pre-training compute [src:arxiv_2010.11929 p.8].
- **Weakness: data.** It underperforms ResNets when pre-trained only on
  ImageNet [src:arxiv_2010.11929 p.6].
- **Weakness: dense tasks.** A single low-resolution feature map, and cost
  quadratic in image size, make ViT unsuitable as a general backbone for
  dense tasks or high resolutions [src:arxiv_2103.14030 p.3].
  [[shifted-window-attention]] (Swin) addresses this.
- **Training without huge data.** DeiT introduced training strategies that
  make ViT work on ImageNet-1K alone, according to Swin's related work
  [src:arxiv_2103.14030 p.3]. DeiT is not a source in this wiki.

## Related

- [[arxiv-2010-11929]]
- [[arxiv-2103-14030]]
- [[self-attention]]
- [[shifted-window-attention]]
- [[inductive-bias-in-vision-models]]
- [[residual-learning]]
- [[convolutional-neural-network]]
- [[imagenet-benchmark]]
- [[arxiv-2201-03545]]
