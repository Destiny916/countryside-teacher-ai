import pytest
from app.services.lesson_service import get_lesson_service


class TestLessonService:
    def test_generate_lesson_plan(self):
        service = get_lesson_service()
        result = service.generate_lesson_plan(
            grade=1,
            subject="math",
            topic="分数的认识"
        )

        assert result['success'] == True
        assert 'plan' in result
        assert result['topic'] == "分数的认识"
        assert result['grade'] == 1
        assert result['subject'] == "math"

    def test_generate_exercises(self):
        service = get_lesson_service()
        lesson_plan = {
            "教学目标": {
                "知识与技能": "使学生理解和掌握分数的基本概念",
                "过程与方法": "通过讲解、练习、讨论等方式进行教学",
                "情感态度与价值观": "培养学生学习兴趣，养成良好的学习习惯"
            },
            "教学重点": "分数的核心知识点",
            "教学难点": "分数的应用和理解"
        }

        result = service.generate_exercises(lesson_plan)
        assert '选择题' in result
        assert '填空题' in result
        assert '解答题' in result
