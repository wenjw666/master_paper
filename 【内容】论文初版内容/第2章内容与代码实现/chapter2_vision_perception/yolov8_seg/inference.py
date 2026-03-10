"""
YOLOv8-seg 推理接口
用于连接器检测、分割和标签ID识别
"""

from ultralytics import YOLO
import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional
import torch


class YOLOv8SegInference:
    """YOLOv8-seg推理类"""
    
    def __init__(self, model_path: str, conf_threshold: float = 0.5, device: str = 'cuda'):
        """
        初始化推理器
        
        Args:
            model_path: 模型权重路径
            conf_threshold: 置信度阈值
            device: 推理设备 ('cuda' 或 'cpu')
        """
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.device = device
        
    def predict(self, image: np.ndarray, target_tag_id: Optional[str] = None) -> Dict:
        """
        对输入图像进行推理
        
        Args:
            image: 输入RGB图像 (H, W, 3)
            target_tag_id: 目标标签ID（可选，用于筛选特定连接器）
        
        Returns:
            检测结果字典，包含：
            - boxes: 边界框列表
            - masks: 分割掩膜列表
            - class_ids: 类别ID列表
            - scores: 置信度列表
            - tag_ids: 标签ID列表
            - connector_mask: 连接器掩膜（合并所有连接器）
            - cable_mask: 线缆掩膜（合并所有线缆）
        """
        # 推理
        results = self.model(image, conf=self.conf_threshold, device=self.device)
        
        # 解析结果
        output = {
            'boxes': [],
            'masks': [],
            'class_ids': [],
            'scores': [],
            'tag_ids': [],
            'connector_mask': None,
            'cable_mask': None
        }
        
        if len(results) == 0:
            return output
        
        result = results[0]
        h, w = image.shape[:2]
        
        # 初始化掩膜
        connector_mask = np.zeros((h, w), dtype=np.uint8)
        cable_mask = np.zeros((h, w), dtype=np.uint8)
        
        # 类别ID到标签ID的映射（根据数据集配置）
        class_to_tag = {
            0: 'connector_shell',
            1: 'cable',
            2: 'tag_A',
            3: 'tag_B',
            # 可根据实际情况扩展
        }
        
        # 解析每个检测结果
        if result.boxes is not None:
            boxes = result.boxes.xyxy.cpu().numpy()
            scores = result.boxes.conf.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy().astype(int)
            
            # 处理分割掩膜
            masks = None
            if result.masks is not None:
                masks = result.masks.data.cpu().numpy()
            
            for i in range(len(boxes)):
                # 筛选目标标签ID
                tag_id = class_to_tag.get(class_ids[i], 'unknown')
                if target_tag_id is not None and tag_id != target_tag_id:
                    continue
                
                output['boxes'].append(boxes[i])
                output['scores'].append(float(scores[i]))
                output['class_ids'].append(int(class_ids[i]))
                output['tag_ids'].append(tag_id)
                
                # 处理掩膜
                if masks is not None and i < len(masks):
                    mask = masks[i]
                    # 调整掩膜尺寸
                    mask_resized = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)
                    mask_binary = (mask_resized > 0.5).astype(np.uint8) * 255
                    
                    output['masks'].append(mask_binary)
                    
                    # 合并掩膜
                    if tag_id == 'connector_shell':
                        connector_mask = np.maximum(connector_mask, mask_binary)
                    elif tag_id == 'cable':
                        cable_mask = np.maximum(cable_mask, mask_binary)
        
        output['connector_mask'] = connector_mask
        output['cable_mask'] = cable_mask
        
        return output
    
    def extract_roi(self, image: np.ndarray, box: np.ndarray, 
                    margin: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """
        根据边界框提取ROI区域
        
        Args:
            image: 原始图像
            box: 边界框 [x1, y1, x2, y2]
            margin: 边界扩展像素
        
        Returns:
            ROI图像和裁剪坐标
        """
        h, w = image.shape[:2]
        x1, y1, x2, y2 = box.astype(int)
        
        # 扩展边界
        x1 = max(0, x1 - margin)
        y1 = max(0, y1 - margin)
        x2 = min(w, x2 + margin)
        y2 = min(h, y2 + margin)
        
        roi = image[y1:y2, x1:x2]
        crop_coords = np.array([x1, y1, x2, y2])
        
        return roi, crop_coords


def main():
    """测试推理接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='YOLOv8-seg推理测试')
    parser.add_argument('--model', type=str, required=True,
                       help='模型权重路径')
    parser.add_argument('--image', type=str, required=True,
                       help='输入图像路径')
    parser.add_argument('--output', type=str, default='./result.jpg',
                       help='输出图像路径')
    parser.add_argument('--conf', type=float, default=0.5,
                       help='置信度阈值')
    parser.add_argument('--target-tag', type=str, default=None,
                       help='目标标签ID（可选）')
    
    args = parser.parse_args()
    
    # 初始化推理器
    inference = YOLOv8SegInference(args.model, conf_threshold=args.conf)
    
    # 读取图像
    image = cv2.imread(args.image)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # 推理
    results = inference.predict(image_rgb, target_tag_id=args.target_tag)
    
    # 可视化结果
    vis_image = image.copy()
    for i, (box, score, tag_id) in enumerate(zip(
        results['boxes'], results['scores'], results['tag_ids']
    )):
        x1, y1, x2, y2 = box.astype(int)
        cv2.rectangle(vis_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(vis_image, f"{tag_id}: {score:.2f}", 
                   (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # 绘制掩膜
        if i < len(results['masks']):
            mask = results['masks'][i]
            mask_colored = np.zeros_like(vis_image)
            mask_colored[mask > 0] = [0, 255, 0]
            vis_image = cv2.addWeighted(vis_image, 1.0, mask_colored, 0.3, 0)
    
    # 保存结果
    cv2.imwrite(args.output, vis_image)
    print(f"结果已保存到: {args.output}")
    print(f"检测到 {len(results['boxes'])} 个目标")


if __name__ == '__main__':
    main()

