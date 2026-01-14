"""
YOLOv8-seg 训练脚本
基于Ultralytics YOLOv8实现连接器检测、分割和分类
"""

from ultralytics import YOLO
import argparse
import yaml
from pathlib import Path


def train_yolov8_seg(
    data_config,
    epochs=300,
    batch_size=16,
    img_size=640,
    device=0,
    pretrained=True,
    output_dir="./weights"
):
    """
    训练YOLOv8-seg模型
    
    Args:
        data_config: 数据集配置文件路径（YAML格式）
        epochs: 训练轮数
        batch_size: 批次大小
        img_size: 输入图像尺寸
        device: GPU设备ID
        pretrained: 是否使用预训练权重
        output_dir: 模型输出目录
    """
    # 创建输出目录
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 初始化模型
    if pretrained:
        # 使用预训练的YOLOv8-seg模型
        model = YOLO('yolov8n-seg.pt')  # 可选: yolov8s-seg.pt, yolov8m-seg.pt等
        print("使用预训练模型: yolov8n-seg.pt")
    else:
        # 从头训练
        model = YOLO('yolov8n-seg.yaml')
        print("从头开始训练")
    
    # 训练参数
    train_args = {
        'data': data_config,
        'epochs': epochs,
        'batch': batch_size,
        'imgsz': img_size,
        'device': device,
        'project': output_dir,
        'name': 'yolov8_seg_connector',
        'save': True,
        'save_period': 50,  # 每50个epoch保存一次
        'val': True,  # 训练时验证
        'plots': True,  # 生成训练曲线图
        'optimizer': 'SGD',  # 使用SGD优化器
        'momentum': 0.937,  # 动量
        'lr0': 0.01,  # 初始学习率
        'lrf': 0.1,  # 最终学习率因子 (0.01 * 0.1 = 0.001)
        'cos_lr': True,  # 使用余弦退火学习率
        'weight_decay': 0.0005,
        'warmup_epochs': 3,
        'warmup_momentum': 0.8,
        'warmup_bias_lr': 0.1,
        'box': 7.5,  # 边界框损失权重
        'cls': 0.5,  # 分类损失权重
        'dfl': 1.5,  # DFL损失权重
        'pose': 12.0,  # 姿态损失权重（分割任务）
        'kobj': 1.0,  # 关键点对象损失权重
        'label_smoothing': 0.0,
        'nbs': 64,  # 标称批次大小
        'hsv_h': 0.015,  # 色调增强
        'hsv_s': 0.7,  # 饱和度增强
        'hsv_v': 0.4,  # 明度增强
        'degrees': 0.0,  # 旋转角度（已在数据增强中处理）
        'translate': 0.1,  # 平移
        'scale': 0.5,  # 缩放
        'shear': 0.0,  # 剪切
        'perspective': 0.0,  # 透视变换
        'flipud': 0.0,  # 上下翻转概率
        'fliplr': 0.5,  # 左右翻转概率
        'mosaic': 1.0,  # Mosaic增强概率
        'mixup': 0.0,  # Mixup增强概率
        'copy_paste': 0.0,  # Copy-paste增强概率
    }
    
    # 开始训练
    print("=" * 50)
    print("开始训练YOLOv8-seg模型")
    print(f"数据集配置: {data_config}")
    print(f"训练轮数: {epochs}")
    print(f"批次大小: {batch_size}")
    print(f"图像尺寸: {img_size}x{img_size}")
    print("=" * 50)
    
    results = model.train(**train_args)
    
    # 训练完成
    print("\n" + "=" * 50)
    print("训练完成！")
    print(f"最佳模型保存在: {output_dir}/yolov8_seg_connector/weights/best.pt")
    print("=" * 50)
    
    return results


def main():
    parser = argparse.ArgumentParser(description='YOLOv8-seg训练脚本')
    parser.add_argument('--data', type=str, required=True,
                       help='数据集配置文件路径（YAML格式）')
    parser.add_argument('--epochs', type=int, default=300,
                       help='训练轮数')
    parser.add_argument('--batch-size', type=int, default=16,
                       help='批次大小')
    parser.add_argument('--img-size', type=int, default=640,
                       help='输入图像尺寸')
    parser.add_argument('--device', type=int, default=0,
                       help='GPU设备ID（-1表示CPU）')
    parser.add_argument('--pretrained', action='store_true', default=True,
                       help='使用预训练权重')
    parser.add_argument('--output-dir', type=str, default='./weights',
                       help='模型输出目录')
    
    args = parser.parse_args()
    
    train_yolov8_seg(
        data_config=args.data,
        epochs=args.epochs,
        batch_size=args.batch_size,
        img_size=args.img_size,
        device=args.device,
        pretrained=args.pretrained,
        output_dir=args.output_dir
    )


if __name__ == '__main__':
    main()

