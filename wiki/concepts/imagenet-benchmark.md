---
title: ImageNet / ILSVRC benchmark
type: concept
sources: [arxiv_1409.0575, arxiv_1409.1556, arxiv_1409.4842, arxiv_1512.03385, arxiv_1608.06993, arxiv_1704.04861, arxiv_1905.11946, arxiv_2010.11929, arxiv_2103.14030]
tags: [computer-vision, benchmark, dataset, image-classification]
updated: 2026-11-03
status: draft
---

ImageNet is an image dataset organized by WordNet synsets. ILSVRC, the
ImageNet Large Scale Visual Recognition Challenge, is the yearly benchmark
built from a subset of it: 1000 classes, about 1.2M training images, 50K
validation and 100K test images [src:arxiv_1409.0575 p.2]
[src:arxiv_1409.0575 p.8]. Most papers in this wiki report results on it.
The test labels are hidden [src:arxiv_1409.0575 p.2].

## Metrics

- **Top-5 error.** The official ranking metric: a prediction is correct if
  any of 5 guesses matches the single ground-truth label
  [src:arxiv_1409.0575 p.15].
- **Top-1 accuracy or error.** Also widely reported. Since about 2017, most
  papers report top-1 *validation* accuracy only [src:arxiv_1905.11946 p.9].
- **Localization.** The label must be right and the predicted box must have
  IoU > 0.5 with the ground truth [src:arxiv_1409.0575 p.15].

## Winning top-5 test error over time

| Year | Entry | Top-5 error | Source |
|------|-------|-------------|--------|
| 2012 | SuperVision (AlexNet) | 16.4% | [src:arxiv_1409.4842 p.9] |
| 2013 | Clarifai | 11.7% | [src:arxiv_1409.4842 p.9] |
| 2014 | GoogLeNet | 6.67% | [src:arxiv_1409.4842 p.9] |
| 2014 | VGG (2nd) | 7.32% | [src:arxiv_1409.4842 p.9] |
| 2015 | ResNet | 3.57% | [src:arxiv_1512.03385 p.6] |

Trained human annotator: 5.1% on a 1500-image sample, against an estimated
6.8% for GoogLeNet on the same images [src:arxiv_1409.0575 p.31].

## Variants and larger pre-training sets

- **ImageNet-21k / 22K.** A superset with 21k classes and 14M images
  [src:arxiv_2010.11929 p.4], described as 14.2M images and 22K classes in
  [src:arxiv_2103.14030 p.6]. Used for pre-training by ViT and Swin.
- **JFT-300M.** An in-house Google dataset with 18k classes and 303M images
  [src:arxiv_2010.11929 p.4].

## Caution when comparing numbers

The same model gets different numbers under different protocols: single crop
vs 10-crop vs multi-scale, validation vs test, and with or without outside
data. For example, ResNet-152 is reported at 5.71% top-5 with 10-crop testing
and 4.49% with multi-scale testing [src:arxiv_1512.03385 p.6]. GoogLeNet goes
from 10.07% (1 model, 1 crop) to 6.67% (7 models, 144 crops)
[src:arxiv_1409.4842 p.9]. Single-crop top-1 for DenseNet-169 is 23.80% error
[src:arxiv_1608.06993 p.6], matching the 76.2% accuracy that EfficientNet
lists for it [src:arxiv_1905.11946 p.6].

> [!conflict]
> GoogLeNet's ImageNet top-1 accuracy is given as 69.8% in
> [src:arxiv_1704.04861 p.6] and as 74.8% in [src:arxiv_1905.11946 p.2]. Both
> give 6.8M parameters. Neither says which evaluation protocol it used, and
> the GoogLeNet paper reports only top-5 [src:arxiv_1409.4842 p.9].

## Related

- [[arxiv-1409-0575]]
- [[convolutional-neural-network]]
- [[vision-transformer]]
- [[arxiv-1409-4842]]
- [[arxiv-1512-03385]]
- [[arxiv-1905-11946]]
- [[arxiv-2010-11929]]
- [[arxiv-1409-1556]]
- [[arxiv-2201-03545]]
