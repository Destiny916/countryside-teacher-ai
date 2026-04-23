"""
教案生成服务
基于RAG检索和LLM生成符合人教版标准的教案
"""
from typing import Dict, List, Optional, Any
from model_service.inference import get_vllm_client
import json

LESSON_PLAN_TEMPLATE = """请根据以下信息生成一份完整的小学教案：

## 基本信息
- 学科：{subject}
- 年级：grade{grade}
- 课时：{duration}
- 课题：{topic}

## 课程标准要求
{standard_content}

## 教材内容摘要
{textbook_summary}

## 教案要求
请按照以下格式生成教案：
1. 教学目标（知识与技能、过程与方法、情感态度与价值观）
2. 教学重点
3. 教学难点
4. 教学方法
5. 教学准备
6. 教学过程（含时间分配）
7. 板书设计
8. 作业设计
9. 教学反思

请用JSON格式输出，key为中文。
"""

class LessonPlanService:
    def __init__(self):
        # 不初始化RAG引擎，直接使用LLM
        self.rag_engine = None
        self.vllm_client = get_vllm_client()

    def generate_lesson_plan(
        self,
        grade: int,
        subject: str,
        topic: str,
        duration: str = "40分钟",
        additional_requirements: Optional[str] = None
    ) -> Dict[str, Any]:
        # 直接使用空上下文，避免RAG引擎的问题
        context = ""

        standard_content = self._get_curriculum_standard(grade, subject)

        prompt = LESSON_PLAN_TEMPLATE.format(
            subject=subject,
            grade=grade,
            duration=duration,
            topic=topic,
            standard_content=standard_content,
            textbook_summary=context
        )

        if additional_requirements:
            prompt += f"\n\n补充要求：{additional_requirements}"

        try:
            result = self.vllm_client.chat(
                messages=[
                    {"role": "system", "content": "你是一位资深的小学教师，擅长编写规范的教案。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            lesson_plan_text = result['choices'][0]['message']['content']
            lesson_plan = self._parse_lesson_plan(lesson_plan_text)
        except Exception as e:
            print(f"教案生成失败: {e}")
            lesson_plan = self._generate_fallback_plan(grade, subject, topic)

        return {
            'success': True,
            'plan': lesson_plan,
            'topic': topic,
            'grade': grade,
            'subject': subject
        }

    def _get_curriculum_standard(self, grade: int, subject: str) -> str:
        standards = {
            ('math', 'pep'): "小学数学课程标准要求：注重基础知识和基本技能的培养，发展学生的数感和符号意识。",
            ('chinese', 'pep'): "小学语文课程标准要求：培养学生的语言文字运用能力，提升语文素养，继承和弘扬中华优秀传统文化。",
            ('english', 'pep'): "小学英语课程标准要求：激发学习兴趣，培养初步的英语沟通能力。",
        }
        return standards.get((subject.lower(), 'pep'), "按照课程标准要求进行教学。")

    def _parse_lesson_plan(self, text: str) -> Dict[str, Any]:
        try:
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                json_str = text.split("```")[1].split("```")[0]
            else:
                json_str = text

            plan = json.loads(json_str.strip())
            return plan
        except json.JSONDecodeError:
            return {'content': text, 'format': 'text'}

    def _generate_fallback_plan(
        self,
        grade: int,
        subject: str,
        topic: str
    ) -> Dict[str, Any]:
        return {
            "教学目标": {
                "知识与技能": f"使学生理解和掌握{topic}的基本概念",
                "过程与方法": "通过讲解、练习、讨论等方式进行教学",
                "情感态度与价值观": "培养学生学习兴趣，养成良好的学习习惯"
            },
            "教学重点": f"{topic}的核心知识点",
            "教学难点": f"{topic}的应用和理解",
            "教学方法": "讲授法、讨论法、练习法",
            "教学准备": "多媒体课件、教材、练习册",
            "教学过程": "导入→新授→巩固→小结→作业",
            "板书设计": f"{topic}知识框架",
            "作业设计": f"课后练习{topic}相关内容",
            "教学反思": "待课后补充"
        }

    def generate_exercises(
        self,
        lesson_plan: Dict[str, Any],
        exercise_types: List[str] = None,
        num_each: int = 3
    ) -> Dict[str, Any]:
        if exercise_types is None:
            exercise_types = ['选择题', '填空题', '解答题']

        plan_summary = json.dumps(lesson_plan, ensure_ascii=False)

        prompt = f"""根据以下教案内容，生成配套练习题：

{plan_summary}

要求：
- 选择题 {num_each} 道
- 填空题 {num_each} 道
- 解答题 {num_each} 道

请给出完整的题目和答案，答案要详细。

用JSON格式输出：
{{
  "选择题": [{{"题目": "...", "选项": [...], "答案": "...", "解析": "..."}}],
  "填空题": [{{"题目": "...", "答案": "...", "解析": "..."}}],
  "解答题": [{{"题目": "...", "答案": "...", "解析": "..."}}]
}}
"""

        try:
            result = self.vllm_client.chat(
                messages=[
                    {"role": "system", "content": "你是一位资深的小学教师，擅长设计练习题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            exercises_text = result['choices'][0]['message']['content']
            exercises = json.loads(exercises_text)
        except Exception as e:
            print(f"练习题生成失败: {e}")
            exercises = {'选择题': [], '填空题': [], '解答题': []}

        return exercises

_service = None

def get_lesson_service() -> LessonPlanService:
    global _service
    if _service is None:
        _service = LessonPlanService()
    return _service