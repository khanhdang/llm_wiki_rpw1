---
title: Network depth
type: concept
sources: [arxiv_1409.1556, arxiv_1409.4842, arxiv_1512.03385, arxiv_1608.06993, arxiv_1905.11946]
tags: [cnn, architecture, optimization]
updated: 2026-11-03
status: draft
---

Depth is the number of weight layers stacked in a network. From VGG (2014)
to ResNet (2015), making CNNs deeper was the main route to higher ImageNet
accuracy. But plain stacking stops working past a point, and later work
treats depth as one dimension to balance against width and resolution.

## Evidence in the sources

- **VGG.** Error falls from 11 to 19 layers and then saturates. A shallower
  network with 5×5 filters had 7% higher top-1 error than its 3×3 counterpart
  [src:arxiv_1409.1556 p.6].
- **GoogLeNet.** 22 layers with parameters. Concern about propagating
  gradients through this depth motivated its auxiliary classifiers
  [src:arxiv_1409.4842 p.6].
- **The degradation problem.** Deeper plain networks have *higher training
  error*: 28.54% top-1 at 34 layers against 27.94% at 18. Overfitting does not
  explain this [src:arxiv_1512.03385 p.1] [src:arxiv_1512.03385 p.5].
  Residual connections reverse it, giving 25.03% at 34 layers
  [src:arxiv_1512.03385 p.5]. See [[residual-learning]].
- **Not vanishing gradients, per ResNet.** He et al. argue the degradation
  is unlikely to come from vanishing gradients, because batch normalization
  keeps signals healthy [src:arxiv_1512.03385 p.5]. (The CNN survey describes
  ResNet differently; see the conflict on [[residual-learning]].)
- **Very deep but overfitting.** A 1202-layer ResNet trains fine but tests
  worse than a 110-layer one on CIFAR-10 [src:arxiv_1512.03385 p.8].
- **Short paths.** DenseNet observes that ResNets, Highway Networks,
  stochastic depth and FractalNets all add short paths from early to late
  layers [src:arxiv_1608.06993 p.1]. See [[dense-connectivity]].
- **Diminishing returns.** ResNet-1000 is about as accurate as ResNet-101, and
  scaling depth alone saturates [src:arxiv_1905.11946 p.3]. See
  [[compound-scaling]].

## Related

- [[residual-learning]]
- [[dense-connectivity]]
- [[compound-scaling]]
- [[batch-normalization]]
- [[convolutional-neural-network]]
- [[arxiv-1409-1556]]
- [[arxiv-1409-4842]]
- [[arxiv-1512-03385]]
- [[arxiv-1608-06993]]
- [[arxiv-1905-11946]]
- [[efficient-cnn-scaling]]
- [[inception-module]]
- [[doi-10-1109-5-726791]]
