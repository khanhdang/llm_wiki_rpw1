---
title: Compound scaling
type: method
sources: [arxiv_1905.11946, arxiv_1704.04861]
tags: [cnn, model-scaling, efficient-models]
updated: 2026-11-03
status: draft
---

Compound scaling enlarges a network's depth, width and input resolution
together, with fixed ratios set by one coefficient φ. It replaces the usual
practice of scaling one dimension by hand. It was introduced with
EfficientNet [src:arxiv_1905.11946 p.1].

## Details

- **Rule.** Depth scales by α^φ, width by β^φ and resolution by γ^φ, with
  α·β²·γ² ≈ 2, so FLOPS grow by about 2^φ. FLOPS are proportional to
  d·w²·r² [src:arxiv_1905.11946 p.5].
- **Finding the coefficients.** A small grid search at φ = 1 on the baseline
  gave α = 1.2, β = 1.1, γ = 1.15 for EfficientNet-B0. They are then held
  fixed to produce B1–B7 [src:arxiv_1905.11946 p.5].
- **Why balance.** Higher resolution needs more depth, for a larger receptive
  field, and more width, for finer patterns [src:arxiv_1905.11946 p.4].
  Scaling one dimension alone saturates around 80% top-1
  [src:arxiv_1905.11946 p.4].

## Evidence

- **On EfficientNet-B0.** At about 1.8B FLOPS: 81.1% for compound scaling
  against 79.0%, 78.9% and 79.1% for depth, width or resolution alone
  [src:arxiv_1905.11946 p.8].
- **On other networks.** MobileNetV1 75.6% vs 74.2% (width only); ResNet-50
  78.8% vs 78.1% (depth only) [src:arxiv_1905.11946 p.6].

## Predecessor

MobileNets already had two separate knobs, a width multiplier α and a
resolution multiplier ρ, set by hand [src:arxiv_1704.04861 p.4]. (Note that
EfficientNet uses α for depth, a different meaning.)

## Related

- [[arxiv-1905-11946]]
- [[efficient-cnn-scaling]]
- [[network-depth]]
- [[depthwise-separable-convolution]]
- [[arxiv-1704-04861]]
- [[convolutional-neural-network]]
