---
title: Residual learning (shortcut connections)
type: method
sources: [arxiv_1512.03385, arxiv_1608.06993, arxiv_2004.02806, arxiv_2010.11929, arxiv_2103.14030]
tags: [cnn, architecture, residual-learning]
updated: 2026-11-03
status: draft
---

In residual learning, a block of layers learns a residual F(x) = H(x) − x,
and an identity shortcut adds the input back, so the block outputs
F(x) + x. Introduced by ResNet, it made networks of 100+ layers trainable by
fixing the degradation problem of plain deep networks
[src:arxiv_1512.03385 p.2]. Residual connections are now standard, including
in Transformers.

## How it works

- **Block.** y = F(x, {Wᵢ}) + x, with the ReLU applied after the addition. If
  dimensions differ, a projection W_s on the shortcut matches them
  [src:arxiv_1512.03385 p.3].
- **Why it should help.** If identity is near optimal, it is easier to push
  F toward zero than to fit identity with non-linear layers
  [src:arxiv_1512.03385 p.3]. Learned residual responses are indeed small
  [src:arxiv_1512.03385 p.8].
- **Cost.** Identity shortcuts add no parameters or FLOPs
  [src:arxiv_1512.03385 p.2], and projections are not essential: shortcut
  options A, B and C differ by only about 0.8 points of top-1
  [src:arxiv_1512.03385 p.6].
- **Bottleneck block.** 1×1 → 3×3 → 1×1 layers for ResNet-50/101/152.
  Replacing the identity shortcut with a projection here would double time
  and model size [src:arxiv_1512.03385 p.6].

## Effect

- **Depth starts to help.** With shortcuts, 34 layers beat 18 (25.03% vs
  27.88% top-1). Without them, 34 layers were worse (28.54% vs 27.94%)
  [src:arxiv_1512.03385 p.5].

## Related designs

- **Highway networks.** Gated shortcuts that can close. ResNet's identity
  shortcuts are never closed [src:arxiv_1512.03385 p.2].
- **DenseNet.** Concatenates instead of summing; its authors argue summation
  "may impede the information flow" [src:arxiv_1608.06993 p.3]. See
  [[dense-connectivity]].
- **Transformers.** ViT and Swin blocks apply a residual connection after
  every attention and MLP module [src:arxiv_2010.11929 p.3]
  [src:arxiv_2103.14030 p.4].

> [!conflict]
> [src:arxiv_2004.02806 p.5] says ResNet "can mitigate the gradient vanishing
> problem" because gradients flow through shortcuts. The ResNet paper itself
> says the problem it addresses is "unlikely to be caused by vanishing
> gradients", since its plain networks use batch normalization and show
> healthy gradient norms [src:arxiv_1512.03385 p.5].

## Related

- [[network-depth]]
- [[dense-connectivity]]
- [[batch-normalization]]
- [[vision-transformer]]
- [[convolutional-neural-network]]
- [[arxiv-1512-03385]]
- [[arxiv-1608-06993]]
- [[arxiv-2004-02806]]
- [[arxiv-2010-11929]]
- [[arxiv-2201-03545]]
