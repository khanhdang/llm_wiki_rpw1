---
title: Dense connectivity (DenseNet blocks)
type: method
sources: [arxiv_1608.06993]
tags: [cnn, architecture]
updated: 2026-11-03
status: draft
---

With dense connectivity, every layer in a block receives the concatenated
feature-maps of all earlier layers in that block, so a block of L layers has
L(L+1)/2 connections [src:arxiv_1608.06993 p.1]. It is the core of DenseNet.
It encourages feature reuse and keeps layers narrow, which gives
parameter-efficient models.

## Details

- **Concatenation, not addition.** Layer ℓ receives [x₀, …, x_{ℓ−1}]. This is
  what distinguishes it from [[residual-learning]], which adds
  [src:arxiv_1608.06993 p.3].
- **Growth rate k.** Each layer adds k feature-maps, for example 12 or 32, to
  a shared "collective knowledge" [src:arxiv_1608.06993 p.3].
- **Blocks and transitions.** Concatenation needs equal map sizes, so the
  network is split into dense blocks joined by BN–1×1 conv–2×2 average-pool
  transitions [src:arxiv_1608.06993 p.3].
- **Bottleneck and compression.** DenseNet-B adds 1×1 bottlenecks producing 4k
  maps; DenseNet-C compresses at transitions by θ = 0.5; DenseNet-BC uses both
  [src:arxiv_1608.06993 p.4].
- **Implicit deep supervision.** Every layer is at most two or three
  transition layers from the loss, which the authors liken to deeply
  supervised nets [src:arxiv_1608.06993 p.7].
- **Feature reuse is real.** Trained layers spread weight across many earlier
  layers [src:arxiv_1608.06993 p.8].

## Effect

- **Parameters.** DenseNet-BC needs about one third of a ResNet's parameters
  for the same accuracy on C10+ [src:arxiv_1608.06993 p.7].
- **ImageNet.** DenseNet-201 (20M parameters) matches ResNet-101 (more than
  40M) [src:arxiv_1608.06993 p.7].

## Related

- [[arxiv-1608-06993]]
- [[residual-learning]]
- [[network-depth]]
- [[convolutional-neural-network]]
- [[batch-normalization]]
