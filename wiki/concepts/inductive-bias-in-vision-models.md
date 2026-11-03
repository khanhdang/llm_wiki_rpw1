---
title: Inductive bias in vision models
type: concept
sources: [arxiv_2010.11929, arxiv_2103.14030, arxiv_2201.03545]
tags: [computer-vision, cnn, transformer]
updated: 2026-11-03
status: draft
---

An inductive bias is an assumption built into an architecture, such as
locality or translation equivariance, that steers what the model learns from
limited data. The ViT and Swin papers frame the CNN-versus-Transformer
question in these terms: how much image-specific structure to build in, and
how much to learn from data.

## In the sources

- **CNN vs ViT.** CNNs build locality, 2D neighbourhood structure and
  translation equivariance into every layer. In ViT, only the MLP layers are
  local and translation equivariant, and the 2D structure is used only for
  patching and for resizing position embeddings [src:arxiv_2010.11929 p.4].
- **Data decides which wins.** Without strong regularization, ViT trained on
  mid-sized data (ImageNet) is a few points behind comparable ResNets
  [src:arxiv_2010.11929 p.1]. With 14M–300M images, "large scale training
  trumps inductive bias" [src:arxiv_2010.11929 p.2]. On a 9M-image subset ViT
  overfits more than ResNets; from 90M images up, it does better
  [src:arxiv_2010.11929 p.7].
- **Swin's counterpoint.** Swin's authors conclude that a bias toward
  translation invariance is "still preferable for general-purpose visual
  modeling", particularly for detection and segmentation. Its relative
  position bias beats absolute position embeddings on those tasks
  [src:arxiv_2103.14030 p.8].
- **ConvNeXt's counterpoint to ViT.** With ImageNet-22K pre-training, a
  "properly designed" pure ConvNet performs on par with or better than Swin of
  similar size. This challenges the view that Transformers' weaker inductive
  bias is what lets them win at scale [src:arxiv_2201.03545 p.7]. ConvNeXt
  also credits the efficiency of both Swin and ConvNeXt over vanilla ViT to the
  ConvNet inductive bias (local computation), not to self-attention
  [src:arxiv_2201.03545 p.8].
- **Locality learned anyway.** Some ViT heads attend very locally in early
  layers, which may serve a similar function to early convolutions
  [src:arxiv_2010.11929 p.8].

## Related

- [[vision-transformer]]
- [[shifted-window-attention]]
- [[convolutional-neural-network]]
- [[self-attention]]
- [[arxiv-2010-11929]]
- [[arxiv-2103-14030]]
- [[arxiv-2201-03545]]
