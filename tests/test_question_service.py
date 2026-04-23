import pytest
from app.services.question_service import get_question_service


class TestQuestionService:
    def test_process_question_text(self):
        service = get_question_service()
        result = service.process_question_text(
            question_text="1+1等于多少？",
            question_type="计算题"
        )

        assert result['success'] == True
        assert 'question' in result
        assert 'answer' in result
        assert result['question']['raw_text'] == "1+1等于多少？"
        assert result['question']['type'] == "计算题"

    def test_process_question_text_without_type(self):
        service = get_question_service()
        result = service.process_question_text(
            question_text="下列哪个是质数？A. 4 B. 5 C. 6 D. 8"
        )

        assert result['success'] == True
        assert 'question' in result
        assert 'answer' in result
        assert result['question']['raw_text'] == "下列哪个是质数？A. 4 B. 5 C. 6 D. 8"
