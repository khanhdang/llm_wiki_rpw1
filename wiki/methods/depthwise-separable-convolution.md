---
title: Depthwise separable convolution
type: method
sources: [arxiv_1704.04861, arxiv_1905.11946, arxiv_2004.02806, arxiv_2201.03545]
tags: [cnn, efficient-models]
updated: 2026-11-03
status: draft
---

A depthwise separable convolution splits a standard convolution into two
layers. A depthwise convolution applies one filter to each input channel, and
a 1×1 pointwise convolution then combines the channels. This separates
filtering from combining and cuts computation and model size sharply
[src:arxiv_1704.04861 p.2]. It is the core layer of MobileNets.

## Details

- **Saving.** With 3×3 kernels, it uses 8–9× less computation than a standard
  convolution, at a small cost in accuracy [src:arxiv_1704.04861 p.3].
- **One-layer example.** A 14×14×512 layer costs 462M mult-adds as a standard
  convolution and 52.3M as a depthwise separable one
  [src:arxiv_1704.04861 p.5].
- **Whole-network ablation.** MobileNet scores 70.6% with 569M mult-adds,
  against 71.7% with 4866M for the same network with full convolutions
  [src:arxiv_1704.04861 p.5].
- **Where the work goes.** Almost all of it lands in the 1×1 pointwise layers:
  95% of compute [src:arxiv_1704.04861 p.3]. These run as dense GEMM.
- **Training tip.** Use little or no weight decay on depthwise filters, since
  they have so few parameters [src:arxiv_1704.04861 p.4].
- **ConvNeXt.** Uses a 7×7 depthwise conv in each block. The authors note
  that depthwise convolution mixes only across space, like the weighted sum in
  self-attention, so pairing it with 1×1 convs separates spatial from channel
  mixing as Transformers do [src:arxiv_2201.03545 p.4]. They also note that at
  similar FLOPs, depthwise models are known to be slower and use more memory
  than dense ones; even so, ConvNeXt's throughput matches or beats Swin's
  [src:arxiv_2201.03545 p.8].
- **In later networks.** EfficientNet-B0 is built from MBConv (mobile
  inverted bottleneck) blocks [src:arxiv_1905.11946 p.5]. The survey says
  MobileNet v2's inverted residual blocks expand channels with 1×1, apply a
  depthwise 3×3, then compress with 1×1 [src:arxiv_2004.02806 p.5].

> [!conflict]
> The survey says MobileNet v1 uses depthwise separable convolutions
> "proposed in Xception" [src:arxiv_2004.02806 p.5]. The MobileNets paper says
> they were "initially introduced in [26]" and only later used to scale up in
> Xception [src:arxiv_1704.04861 p.1].

## Related

- [[arxiv-1704-04861]]
- [[efficient-cnn-scaling]]
- [[compound-scaling]]
- [[convolutional-neural-network]]
- [[arxiv-1905-11946]]
- [[arxiv-2004-02806]]
- [[arxiv-2201-03545]]
