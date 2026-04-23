"""
OCR处理器
基于PaddleOCR识别题目图片
"""
import os
from typing import Optional, List, Dict, Any, Tuple
import numpy as np
from PIL import Image
import io

class OCRHandler:
    def __init__(self):
        self.reader = None
        self._initialized = False

    def initialize(self):
        if self._initialized:
            return
        print("Loading OCR model...")
        from paddleocr import PaddleOCR
        self.reader = PaddleOCR(
            use_angle_cls=True,
            lang='ch',
            use_gpu=True,
            show_log=False
        )
        self._initialized = True

    def recognize_from_bytes(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        self.initialize()

        image = Image.open(io.BytesIO(image_bytes))
        img_array = np.array(image)

        result = self.reader.ocr(img_array, cls=True)

        if not result or not result[0]:
            return []

        line_texts = []
        for line in result[0]:
            if line:
                bbox = line[0]
                text = line[1][0]
                confidence = line[1][1]
                line_texts.append({
                    'text': text,
                    'bbox': bbox,
                    'confidence': confidence
                })

        return line_texts

    def recognize_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        self.initialize()
        result = self.reader.ocr(file_path, cls=True)

        if not result or not result[0]:
            return []

        return [
            {
                'text': line[1][0],
                'bbox': line[0],
                'confidence': line[1][1]
            }
            for line in result[0] if line
        ]

    def parse_question_structure(
        self,
        ocr_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        question_text = "\n".join([r['text'] for r in ocr_results])

        question_type = self._detect_question_type(question_text)

        structured = {
            'raw_text': question_text,
            'type': question_type,
            'lines': [r['text'] for r in ocr_results],
            'has_image': self._check_for_image(ocr_results)
        }

        return structured

    def _detect_question_type(self, text: str) -> str:
        text = text.strip()

        if any(marker in text for marker in ['选择题', '选一选', '下列']):
            return '选择题'
        elif any(marker in text for marker in ['填空题', '填空', '（）']):
            return '填空题'
        elif any(marker in text for marker in ['解答题', '应用题', '计算题', '证明题']):
            return '解答题'
        elif any(marker in text for marker in ['判断题', '对的', '错的']):
            return '判断题'
        else:
            return 'unknown'

    def _check_for_image(self, ocr_results: List[Dict[str, Any]]) -> bool:
        return False

_handler = None

def get_ocr_handler() -> OCRHandler:
    global _handler
    if _handler is None:
        _handler = OCRHandler()
    return _handler