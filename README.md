# MosaicOS
**Mosaic** of **O**bject-centric Images as **S**cene-centric Images (**MosaicOS**) for long-tailed object detection and instance segmentation.

![](image/mosaicos.png)

## Introduction
Many objects do not appear frequently enough in complex scenes (e.g., certain handbags in living rooms) for 
training an accurate object detector, but are often found frequently by themselves (e.g., in product images). 
Yet, these object-centric images are not effectively leveraged for improving object detection in scene-centric 
images. 

We propose Mosaic of Object-centric images as Scene-centric images (MosaicOS), a simple and novel framework that is surprisingly effective at tackling the challenges of long-tailed object detection. Keys to our approach
are three-fold: (i) pseudo scene-centric image construction from object-centric images for mitigating domain differences, (ii) high-quality bounding box imputation using
the object-centric images’ class labels, and (iii) a multistage training procedure. Check our paper for further details:

Cheng Zhang*, Tai-Yu Pan*, Yandong Li, Hexiang Hu, Dong Xuan, Soravit Changpinyo, Boqing Gong, Wei-Lun Chao. 
[MosaicOS: 
A Simple and Effective Use of Object-Centric Images for Long-Tailed Object Detection](https://arxiv.org/abs/2102.08884).
Preprint 2021.

## Pre-trained models

All models are trained on [LVIS](https://www.lvisdataset.org/) training set with [Repeated Factor 
Sampling (RFS)](https://arxiv.org/abs/1908.03195). Our impelementation is based on [Detectron2](https://github.com/facebookresearch/detectron2).

### LVIS v0.5 validation set
#### Object detection
| Backbone | Method | APb | APbr | APbc | APbf | Download |
| :----: | :----: | :----:|:----: |:----: |:----: |:----: |
|[R50-FPN]() | Faster R-CNN | | | | | [model]() &#124; [metrics]() |
|[R50-FPN]() | MosaicOS | | | | | [model]() &#124; [metrics]() |

#### Instance segmentation
|Backbone| Method | AP | APr | APc | APf | APb | Download |
| :----:| :----: | :----: |:----: |:----: |:----: |:----: |:----: |
|[R50-FPN]() |Mask R-CNN| | | | | | [model]() &#124; [metrics]() |
|[R50-FPN]() | MosaicOS | | | | | | [model]() &#124; [metrics]() |
|[R101-FPN]() |Mask R-CNN| | | | | | [model]() &#124; [metrics]() |
|[R101-FPN]() | MosaicOS | | | | | | [model]() &#124; [metrics]() |
|[X101-FPN]() |Mask R-CNN| | | | | | [model]() &#124; [metrics]() |
|[X101-FPN]() | MosaicOS | | | | | | [model]() &#124; [metrics]() |


### LVIS v1.0 validation set

#### Object detection
| Backbone | Method | APb | APbr | APbc | APbf | Download |
| :----: | :----: | :----:|:----: |:----: |:----: |:----: |
|[R50-FPN]() | Faster R-CNN | | | | | [model]() &#124; [metrics]() |
|[R50-FPN]() | MosaicOS | | | | | [model]() &#124; [metrics]() |

#### Instance segmentation
|Backbone| Method | AP | APr | APc | APf | APb | Download |
| :----:| :----: | :----: |:----: |:----: |:----: |:----: |:----: |
|[R50-FPN]() |Mask R-CNN| | | | | | [model]() &#124; [metrics]() |
|[R50-FPN]() | MosaicOS | | | | | | [model]() &#124; [metrics]() |
|[R101-FPN]() |Mask R-CNN| | | | | | [model]() &#124; [metrics]() |
|[R101-FPN]() | MosaicOS | | | | | | [model]() &#124; [metrics]() |
|[X101-FPN]() |Mask R-CNN| | | | | | [model]() &#124; [metrics]() |
|[X101-FPN]() | MosaicOS | | | | | | [model]() &#124; [metrics]() |

## Citation
Please cite with the following bibtex if you find it useful.
```
@article{zhang2021mosaicos,
  title={{MosaicOS}: A Simple and Effective Use of Object-Centric Images for Long-Tailed Object Detection},
  author={Zhang, Cheng and Pan, Tai-Yu and Li, Yandong and Hu, Hexiang and Xuan, Dong and Changpinyo, Soravit and Gong, Boqing and Chao, Wei-Lun},
  journal={arXiv preprint arXiv:2102.08884},
  year={2021}
}
```
