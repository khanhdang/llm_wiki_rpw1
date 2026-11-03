---
title: Batch normalization
type: method
sources: [arxiv_1512.03385, arxiv_1608.06993, arxiv_1704.04861, arxiv_2004.02806, arxiv_2010.11929, arxiv_2201.03545]
tags: [cnn, training, normalization]
updated: 2026-11-03
status: draft
---

Batch normalization (BN) normalizes layer activations using statistics from
the mini-batch. None of the sources in this wiki introduces it; the original
BN paper, Ioffe & Szegedy 2015, is not a source here. This page records how
the ingested papers use it and what they claim about it.

## Usage in the sources

- **ResNet.** BN after every convolution, before the activation, and no
  dropout [src:arxiv_1512.03385 p.4]. The authors argue that BN keeps forward
  signals and gradient norms healthy, so their plain-network degradation is
  not vanishing gradients [src:arxiv_1512.03385 p.5]. For detection
  fine-tuning, BN statistics are frozen to save memory
  [src:arxiv_1512.03385 p.10].
- **DenseNet.** Each layer is BN → ReLU → 3×3 conv
  [src:arxiv_1608.06993 p.3].
- **MobileNets.** BN and ReLU after both the depthwise and the pointwise
  convolutions [src:arxiv_1704.04861 p.3].
- **Inception v2.** According to the survey, it used BN to handle "internal
  covariate shift" and to allow larger learning rates
  [src:arxiv_2004.02806 p.4].
- **ConvNeXt.** Keeps one normalization layer per block and replaces BN with
  LayerNorm, which slightly helps (81.4% → 81.5%). The authors note that
  swapping LN into an original ResNet is reported to be suboptimal
  [src:arxiv_2201.03545 p.5]. EMA badly hurts models that still use BN
  [src:arxiv_2201.03545 p.9].
- **ViT's ResNet baseline (BiT).** Replaces BN with Group Normalization and
  standardized convolutions, which improves transfer
  [src:arxiv_2010.11929 p.5].

## Related

- [[residual-learning]]
- [[network-depth]]
- [[dense-connectivity]]
- [[convolutional-neural-network]]
- [[arxiv-1512-03385]]
- [[arxiv-1608-06993]]
- [[arxiv-2201-03545]]
