import pytest
from app.core.dialogue_manager import DialogueManager
from app.core.interruption import InterruptionDetector


class TestInterruptionDetector:
    def test_detect_interruption(self):
        detector = InterruptionDetector()

        assert detector.detect_interruption("老师停一下")[0] == True
        assert detector.detect_interruption("等一下")[0] == True
        assert detector.detect_interruption("不懂")[0] == True
        assert detector.detect_interruption("继续讲")[0] == False

    def test_detect_continue(self):
        detector = InterruptionDetector()

        assert detector.detect_continue("继续") == True
        assert detector.detect_continue("可以了") == True
        assert detector.detect_continue("懂了") == True

    def test_extract_question(self):
        detector = InterruptionDetector()

        question = detector.extract_question("老师停一下，为什么天是蓝色的？", "停一下")
        assert "为什么天是蓝色的" in question


class TestDialogueManager:
    def test_create_session(self):
        manager = DialogueManager()
        session_id = manager.create_session("test_user")

        assert session_id is not None
        assert manager.get_session(session_id) is not None

    def test_session_isolation(self):
        manager = DialogueManager()
        session1 = manager.create_session("user1")
        session2 = manager.create_session("user2")

        context1 = manager.get_session(session1)
        context2 = manager.get_session(session2)

        assert context1.session_id != context2.session_id
