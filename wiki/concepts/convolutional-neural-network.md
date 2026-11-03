---
title: Convolutional neural network (CNN)
type: concept
sources: [doi_10.1109_5.726791, arxiv_2004.02806, arxiv_1409.0575, arxiv_1409.1556, arxiv_1409.4842, arxiv_1512.03385, arxiv_1608.06993, arxiv_1704.04861, arxiv_1905.11946, arxiv_2010.11929, arxiv_2103.14030, arxiv_2201.03545]
tags: [computer-vision, cnn]
updated: 2026-11-03
status: draft
---

A convolutional neural network is a feed-forward network that extracts
features from data with convolutions. Unlike hand-built pipelines, it learns
its features rather than having them designed [src:arxiv_2004.02806 p.2].
From 2012 to about 2020, CNNs were the dominant architecture for large-scale
image recognition. Since then, Transformer-based models have competed with
them ([[vision-transformer]]), and ConvNeXt argues that a modernized pure
ConvNet can still match them [src:arxiv_2201.03545 p.9].

## Building blocks

- **The original argument.** Convolutional networks combine local receptive
  fields, shared weights and sub-sampling for some shift, scale and
  distortion invariance, and learn their own feature extractor
  [src:doi_10.1109_5.726791 p.6] [src:doi_10.1109_5.726791 p.7]. Weight
  sharing cuts free parameters, reducing the gap between training and test
  error [src:doi_10.1109_5.726791 p.7].
- **Layers.** Convolution produces feature maps. Padding controls border
  effects, stride controls how densely the kernel is applied, and pooling
  (max or average) downsamples [src:arxiv_2004.02806 p.2].
- **Built-in assumptions.** Locality, two-dimensional neighbourhood structure
  and translation equivariance are built into every layer of a CNN
  [src:arxiv_2010.11929 p.4]. See [[inductive-bias-in-vision-models]].

## Lineage in this wiki

| Year | Model | Main idea | Page |
|------|-------|-----------|------|
| 1998 | LeNet-5 | 7 trainable layers, 60,000 parameters; local receptive fields, shared weights, sub-sampling; 0.8% error on MNIST [src:doi_10.1109_5.726791 p.7] [src:doi_10.1109_5.726791 p.14] | [[doi-10-1109-5-726791]] |
| 2012 | AlexNet (SuperVision) | Deep CNN, 60M parameters, GPUs, dropout; won ILSVRC 2012 [src:arxiv_1409.0575 p.18] | — |
| 2014 | VGG | Depth through stacked 3×3 convolutions, 16–19 weight layers [src:arxiv_1409.1556 p.1] | [[arxiv-1409-1556]] |
| 2014 | GoogLeNet | [[inception-module]], 22 layers, compute budget [src:arxiv_1409.4842 p.1] | [[arxiv-1409-4842]] |
| 2015 | ResNet | [[residual-learning]], up to 152 layers on ImageNet [src:arxiv_1512.03385 p.1] | [[arxiv-1512-03385]] |
| 2016 | DenseNet | [[dense-connectivity]] [src:arxiv_1608.06993 p.1] | [[arxiv-1608-06993]] |
| 2017 | MobileNets | [[depthwise-separable-convolution]], width and resolution multipliers [src:arxiv_1704.04861 p.1] | [[arxiv-1704-04861]] |
| 2019 | EfficientNet | [[compound-scaling]] of depth, width and resolution [src:arxiv_1905.11946 p.1] | [[arxiv-1905-11946]] |
| 2022 | ConvNeXt | ResNet modernized toward Swin's design, with no attention; matches Swin [src:arxiv_2201.03545 p.2] | [[arxiv-2201-03545]] |

By 2014, every top ILSVRC entry relied heavily on CNNs
[src:arxiv_1409.0575 p.22].

## Recurring design themes

- **Going deeper.** See [[network-depth]].
- **1×1 convolutions.** Used to reduce dimensions or mix channels: in VGG
  configuration C [src:arxiv_1409.1556 p.3], in Inception
  [src:arxiv_1409.4842 p.2], in ResNet bottlenecks
  [src:arxiv_1512.03385 p.6], in DenseNet-B [src:arxiv_1608.06993 p.4], and as
  the pointwise half of MobileNet layers [src:arxiv_1704.04861 p.2].
- **Global average pooling instead of large fully connected heads.**
  GoogLeNet [src:arxiv_1409.4842 p.6], ResNet [src:arxiv_1512.03385 p.3] and
  DenseNet [src:arxiv_1608.06993 p.4].
- **Efficiency.** See [[efficient-cnn-scaling]].

## Gaps

- **LeNet layer count.** Sources disagree. The LeNet paper says 7 layers
  [src:doi_10.1109_5.726791 p.7]; DenseNet says 5 [src:arxiv_1608.06993 p.1].
  See the conflict on [[doi-10-1109-5-726791]].
- **Limitations named by the survey.** Poor generalization to rotated or
  rescaled views without much data, and loss of spatial relationships through
  pooling, which motivates capsule networks [src:arxiv_2004.02806 p.17]
  [src:arxiv_2004.02806 p.18].

## Related

- [[network-depth]]
- [[residual-learning]]
- [[inception-module]]
- [[dense-connectivity]]
- [[depthwise-separable-convolution]]
- [[compound-scaling]]
- [[efficient-cnn-scaling]]
- [[batch-normalization]]
- [[inductive-bias-in-vision-models]]
- [[vision-transformer]]
- [[imagenet-benchmark]]
- [[arxiv-2004-02806]]
- [[arxiv-1409-0575]]
