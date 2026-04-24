"""
打断检测器
检测学生说"停"、"等一下"等关键词
"""
from typing import List, Tuple, Optional

INTERRUPT_KEYWORDS = [
    "停",
    "等一下",
    "等一等",
    "老师停",
    "停一下",
    "暂停",
    "稍等",
    "等会",
    "不懂",
    "不懂了",
    "不会",
    "不会了",
    "再说一遍",
    "重新说",
    "慢一点",
    "太快了",
    "说清楚",
    "没听懂",
    "听不懂"
]

CONTINUE_KEYWORDS = [
    "继续",
    "可以了",
    "继续说",
    "继续讲",
    "往下说",
    "懂了",
    "知道了",
    "明白",
    "明白了"
]

class InterruptionDetector:
    def __init__(self):
        self.interrupt_keywords = INTERRUPT_KEYWORDS
        self.continue_keywords = CONTINUE_KEYWORDS

    def detect_interruption(self, text: str) -> Tuple[bool, Optional[str]]:
        text_lower = text.lower()
        for keyword in self.interrupt_keywords:
            if keyword in text:
                return True, keyword
        return False, None

    def detect_continue(self, text: str) -> bool:
        for keyword in self.continue_keywords:
            if keyword in text:
                return True
        return False

    def extract_question(self, text: str, interrupt_keyword: str) -> str:
        parts = text.split(interrupt_keyword)
        if len(parts) > 1:
            question = parts[1].strip()
            return question if question else ""
        return text

_detector = None

def get_interruption_detector() -> InterruptionDetector:
    global _detector
    if _detector is None:
        _detector = InterruptionDetector()
    return _detector