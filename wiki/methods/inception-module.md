---
title: Inception module
type: method
sources: [arxiv_1409.4842, arxiv_2004.02806]
tags: [cnn, architecture]
updated: 2026-11-03
status: draft
---

An Inception module runs 1×1, 3×3 and 5×5 convolutions and a max-pooling
branch in parallel and concatenates their outputs. 1×1 convolutions reduce
dimensions before the expensive branches. GoogLeNet stacks nine of them
[src:arxiv_1409.4842 p.5] [src:arxiv_1409.4842 p.6]. The aim is to widen and
deepen a network under a fixed compute budget.

## Details

- **Motivation.** Approximate an optimal sparse local structure with dense
  building blocks that run efficiently on current hardware
  [src:arxiv_1409.4842 p.4].
- **The naive version is too costly.** Without reductions, 5×5 convolutions
  and pooling outputs make compute blow up within a few stages
  [src:arxiv_1409.4842 p.4] [src:arxiv_1409.4842 p.5].
- **1×1 reductions.** They cut channels before the 3×3 and 5×5 convolutions
  and add a ReLU [src:arxiv_1409.4842 p.5].
- **Multi-scale processing.** Features are processed at several scales and
  then aggregated [src:arxiv_1409.4842 p.5].
- **Speed trade-off.** Tuning the module's knobs can give networks 2–3× faster
  than similarly accurate non-Inception networks, but this takes careful
  manual design [src:arxiv_1409.4842 p.5].

## Later versions (from the survey)

- **v2.** Batch normalization, and factorizing a 5×5 convolution into two 3×3s
  [src:arxiv_2004.02806 p.4].
- **v3.** Asymmetric factorizations (1×n then n×1), 299×299 input
  [src:arxiv_2004.02806 p.4].
- **v4 and Inception-ResNet.** More modules, and residual connections
  [src:arxiv_2004.02806 p.4].

## Related

- [[arxiv-1409-4842]]
- [[efficient-cnn-scaling]]
- [[convolutional-neural-network]]
- [[network-depth]]
- [[arxiv-2004-02806]]
