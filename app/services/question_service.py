"""
题库问答服务
识别题目并给出答案和详细讲解
"""
from typing import Dict, List, Optional, Any
import json
from app.core.ocr_handler import get_ocr_handler
from app.core.rag_engine import get_rag_engine
from model_service.inference import get_vllm_client

class QuestionService:
    def __init__(self):
        self.ocr_handler = get_ocr_handler()
        self.rag_engine = get_rag_engine()
        self.vllm_client = get_vllm_client()

    def process_question_image(self, image_bytes: bytes) -> Dict[str, Any]:
        ocr_results = self.ocr_handler.recognize_from_bytes(image_bytes)

        if not ocr_results:
            return {
                'success': False,
                'error': '未能识别图片中的文字'
            }

        structured = self.ocr_handler.parse_question_structure(ocr_results)

        answer_result = self._get_answer_for_question(structured['raw_text'], structured['type'])

        return {
            'success': True,
            'question': structured,
            'answer': answer_result
        }

    def process_question_text(self, question_text: str, question_type: str = None) -> Dict[str, Any]:
        if not question_type:
            structured = {
                'raw_text': question_text,
                'type': self.ocr_handler._detect_question_type(question_text)
            }
        else:
            structured = {
                'raw_text': question_text,
                'type': question_type
            }

        answer_result = self._get_answer_for_question(question_text, structured['type'])

        return {
            'success': True,
            'question': structured,
            'answer': answer_result
        }

    def _get_answer_for_question(
        self,
        question_text: str,
        question_type: str
    ) -> Dict[str, Any]:
        relevant_knowledge = self.rag_engine.get_relevant_context(
            query=question_text,
            n_results=3
        )

        prompt = f"""请解答以下{question_type}：

{question_text}

相关知识点：
{relevant_knowledge}

请给出：
1. 答案
2. 详细解题步骤（分步讲解）
3. 知识点解析
4. 易错点提醒（如有）

请用JSON格式输出：
{{
  "答案": "...",
  "解题步骤": ["步骤1", "步骤2", ...],
  "知识点解析": "...",
  "易错点提醒": "...",
  "适合儿童的解释": "..."
}}
"""

        try:
            result = self.vllm_client.chat(
                messages=[
                    {"role": "system", "content": "你是一位资深的小学教师，擅长解答题目并用儿童能理解的方式讲解。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            answer_text = result['choices'][0]['message']['content']
            answer = self._parse_answer(answer_text)
        except Exception as e:
            print(f"答案生成失败: {e}")
            answer = {
                "答案": "抱歉，暂时无法解答",
                "解题步骤": [],
                "知识点解析": "",
                "易错点提醒": "",
                "适合儿童的解释": ""
            }

        return answer

    def _parse_answer(self, text: str) -> Dict[str, Any]:
        try:
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                json_str = text.split("```")[1].split("```")[0]
            else:
                json_str = text

            return json.loads(json_str.strip())
        except json.JSONDecodeError:
            return {
                "答案": text,
                "解题步骤": [],
                "知识点解析": "",
                "易错点提醒": "",
                "适合儿童的解释": ""
            }

_service = None

def get_question_service() -> QuestionService:
    global _service
    if _service is None:
        _service = QuestionService()
    return _service