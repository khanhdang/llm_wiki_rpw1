---
title: Efficiency and scaling of CNNs
type: concept
sources: [arxiv_1409.4842, arxiv_1409.1556, arxiv_1512.03385, arxiv_1608.06993, arxiv_1704.04861, arxiv_1905.11946, arxiv_2004.02806]
tags: [cnn, efficient-models, model-scaling]
updated: 2026-11-03
status: draft
---

This page covers how the papers in this wiki trade accuracy against compute,
parameters and latency: deliberate compute budgets, cheaper layer types,
global multipliers, and principled scaling rules. It is the overview page;
[[depthwise-separable-convolution]] and [[compound-scaling]] cover the two
main techniques.

## Approaches in the sources

- **A fixed compute budget.** GoogLeNet was designed for about 1.5 billion
  multiply-adds at inference, partly with mobile and embedded use in mind
  [src:arxiv_1409.4842 p.1].
- **Small filters and bottlenecks.** VGG's stacked 3×3 filters
  [src:arxiv_1409.1556 p.2]. Inception's 1×1 reductions
  [src:arxiv_1409.4842 p.5]. ResNet's bottleneck blocks, which keep
  ResNet-152 at 11.3 GFLOPs, below VGG-16's 15.3 [src:arxiv_1512.03385 p.7].
  DenseNet's narrow layers and compression [src:arxiv_1608.06993 p.4].
- **Factorized convolutions.** MobileNets' depthwise separable layers cost 8–9×
  less than standard 3×3 convolutions [src:arxiv_1704.04861 p.3].
- **Global multipliers.** MobileNets' width multiplier α (cost about α²) and
  resolution multiplier ρ (cost ρ²) [src:arxiv_1704.04861 p.4]
  [src:arxiv_1704.04861 p.5]. Thinner models beat shallower ones at equal cost
  [src:arxiv_1704.04861 p.5].
- **Compound scaling.** Balancing depth, width and resolution beats scaling
  any one of them [src:arxiv_1905.11946 p.4].
- **Model compression.** Low-rank approximation, pruning and quantization
  [src:arxiv_2004.02806 p.16].

## FLOPs are not latency

- **Hardware-friendly operations.** GoogLeNet notes that sparse computation is
  slow on current hardware even when it needs 100× fewer operations
  [src:arxiv_1409.4842 p.3]. MobileNets puts 95% of compute into 1×1
  convolutions because they map directly onto GEMM
  [src:arxiv_1704.04861 p.3].
- **Measured, not just counted.** EfficientNet reports real CPU latency
  [src:arxiv_1905.11946 p.6], but its search optimizes FLOPS
  [src:arxiv_1905.11946 p.5].

## Related

- [[depthwise-separable-convolution]]
- [[compound-scaling]]
- [[inception-module]]
- [[network-depth]]
- [[convolutional-neural-network]]
- [[arxiv-1704-04861]]
- [[arxiv-1905-11946]]
- [[arxiv-1409-4842]]
