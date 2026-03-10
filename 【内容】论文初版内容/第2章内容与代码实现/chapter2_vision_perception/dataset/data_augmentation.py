"""
数据增强工具
实现论文中描述的高斯噪声、随机旋转、色彩抖动等增强策略
"""

import cv2
import numpy as np
import albumentations as A
from albumentations.pytorch import ToTensorV2
import os
from pathlib import Path
import argparse
import json


def create_augmentation_pipeline():
    """
    创建数据增强流水线
    按照论文要求：
    - 高斯噪声：概率0.5，标准差σ=0.1
    - 随机旋转：±180度
    - 色彩抖动：亮度、对比度、饱和度均为0.5
    """
    transform = A.Compose([
        # 高斯噪声
        A.GaussNoise(var_limit=(0.0, 0.1), p=0.5),
        
        # 随机旋转
        A.Rotate(limit=180, p=1.0, border_mode=cv2.BORDER_CONSTANT),
        
        # 色彩抖动
        A.ColorJitter(
            brightness=0.5,
            contrast=0.5,
            saturation=0.5,
            hue=0.1,
            p=0.8
        ),
        
        # 随机水平/垂直翻转
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        
        # 随机裁剪与缩放
        A.RandomResizedCrop(
            height=640,
            width=640,
            scale=(0.8, 1.0),
            p=0.5
        ),
    ])
    
    return transform


def augment_image(image, mask=None, transform=None):
    """
    对单张图像进行增强
    
    Args:
        image: 输入图像 (numpy array)
        mask: 可选的分割掩膜
        transform: 增强变换对象
    
    Returns:
        增强后的图像和掩膜
    """
    if transform is None:
        transform = create_augmentation_pipeline()
    
    if mask is not None:
        augmented = transform(image=image, mask=mask)
        return augmented['image'], augmented['mask']
    else:
        augmented = transform(image=image)
        return augmented['image'], None


def augment_dataset(input_dir, output_dir, transform=None):
    """
    对整个数据集进行增强
    
    Args:
        input_dir: 输入数据集目录
        output_dir: 输出目录
        transform: 增强变换对象
    """
    if transform is None:
        transform = create_augmentation_pipeline()
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "masks"), exist_ok=True)
    
    # 获取所有图像文件
    image_dir = os.path.join(input_dir, "images")
    mask_dir = os.path.join(input_dir, "masks")
    
    image_files = sorted([f for f in os.listdir(image_dir) 
                         if f.endswith(('.jpg', '.png', '.jpeg'))])
    
    print(f"找到 {len(image_files)} 张图像")
    
    augmented_count = 0
    for img_file in image_files:
        # 读取图像
        img_path = os.path.join(image_dir, img_file)
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 读取掩膜（如果存在）
        mask = None
        mask_file = img_file.replace('.jpg', '.png').replace('.jpeg', '.png')
        mask_path = os.path.join(mask_dir, mask_file)
        if os.path.exists(mask_path):
            mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        
        # 增强
        aug_image, aug_mask = augment_image(image, mask, transform)
        
        # 保存
        output_img_path = os.path.join(output_dir, "images", img_file)
        cv2.imwrite(output_img_path, 
                   cv2.cvtColor(aug_image, cv2.COLOR_RGB2BGR))
        
        if aug_mask is not None:
            output_mask_path = os.path.join(output_dir, "masks", mask_file)
            cv2.imwrite(output_mask_path, aug_mask)
        
        augmented_count += 1
        if augmented_count % 100 == 0:
            print(f"已处理: {augmented_count}/{len(image_files)}")
    
    print(f"增强完成，共处理 {augmented_count} 张图像")


def main():
    parser = argparse.ArgumentParser(description='数据增强工具')
    parser.add_argument('--input_dir', type=str, required=True,
                       help='输入数据集目录')
    parser.add_argument('--output_dir', type=str, required=True,
                       help='输出目录')
    parser.add_argument('--config', type=str, default=None,
                       help='增强配置文件（YAML格式）')
    
    args = parser.parse_args()
    
    # 如果提供了配置文件，从文件加载
    if args.config and os.path.exists(args.config):
        import yaml
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
        # 根据配置创建transform（这里简化处理）
        transform = create_augmentation_pipeline()
    else:
        transform = create_augmentation_pipeline()
    
    augment_dataset(args.input_dir, args.output_dir, transform)


if __name__ == '__main__':
    main()

