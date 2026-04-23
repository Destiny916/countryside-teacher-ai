"""
对话管理器
处理多轮对话上下文，支持打断与恢复
"""
from typing import Dict, Optional, List, Any
from datetime import datetime
import uuid
from pydantic import BaseModel, Field
from enum import Enum
from app.core.interruption import get_interruption_detector
from model_service.inference import get_vllm_client

class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class Message(BaseModel):
    role: Role
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class TeachingState(BaseModel):
    topic: Optional[str] = None
    current_point: int = 0
    讲解进度: List[str] = Field(default_factory=list)
    explained_points: List[int] = Field(default_factory=list)
    depth_level: int = 1

class ConversationContext(BaseModel):
    session_id: str
    user_id: str
    messages: List[Message] = Field(default_factory=list)
    teaching_state: Optional[TeachingState] = None
    interrupted: bool = False
    last_interruption_point: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

SYSTEM_PROMPT = """你是一位充满爱心、耐心的小学老师，名叫小慧老师。你在和6-12岁的小学生交流。
你的特点是：
1. 说话温柔、亲切，像朋友一样
2. 善于用比喻和例子解释抽象概念
3. 讲解时分步骤，每步讲清楚后再讲下一步
4. 经常鼓励学生，"你真棒"、"很好"等
5. 如果学生说"不懂"，会换一种方式重新讲解
6. 使用简单的词汇，避免太专业的术语

当学生打断你时，先回答他们的问题，然后确认是否可以继续。"""

class DialogueManager:
    def __init__(self):
        self.sessions: Dict[str, ConversationContext] = {}
        self.vllm_client = get_vllm_client()
        self.interruption_detector = get_interruption_detector()

    def create_session(self, user_id: str) -> str:
        session_id = str(uuid.uuid4())
        context = ConversationContext(
            session_id=session_id,
            user_id=user_id,
            messages=[Message(role=Role.SYSTEM, content=SYSTEM_PROMPT)]
        )
        self.sessions[session_id] = context
        return session_id

    def get_session(self, session_id: str) -> Optional[ConversationContext]:
        return self.sessions.get(session_id)

    def process_text_input(
        self,
        session_id: str,
        text: str
    ) -> Dict[str, Any]:
        context = self.get_session(session_id)
        if not context:
            return {'error': 'Session not found'}

        is_interrupted, keyword = self.interruption_detector.detect_interruption(text)

        if is_interrupted:
            context.interrupted = True
            if context.teaching_state:
                context.last_interruption_point = context.teaching_state.current_point

            question = self.interruption_detector.extract_question(text, keyword)
            response = self._generate_response(context, question, is_question=True)

            if self.interruption_detector.detect_continue(response.get('text', '')):
                context.interrupted = False

            return {
                'type': 'interruption',
                'keyword': keyword,
                'question': question,
                'response': response,
                'can_continue': True
            }

        if self.interruption_detector.detect_continue(text) and context.interrupted:
            context.interrupted = False
            return {
                'type': 'continue',
                'response': {'text': '好的，那我们继续！'}
            }

        response = self._generate_response(context, text)

        return {
            'type': 'normal',
            'response': response
        }

    def _generate_response(
        self,
        context: ConversationContext,
        user_input: str,
        is_question: bool = False
    ) -> Dict[str, Any]:
        context.messages.append(Message(role=Role.USER, content=user_input))

        messages = [{"role": m.role.value, "content": m.content} for m in context.messages]

        try:
            result = self.vllm_client.chat(messages=messages)
            assistant_message = result['choices'][0]['message']['content']
        except Exception as e:
            print(f"vLLM调用失败: {e}")
            assistant_message = "抱歉，老师现在有点累，我们等会儿再继续好不好？"

        context.messages.append(Message(role=Role.ASSISTANT, content=assistant_message))
        context.updated_at = datetime.now()

        return {
            'text': assistant_message,
            'session_id': context.session_id
        }

    def start_teaching(
        self,
        session_id: str,
        topic: str,
        outline: List[str]
    ) -> Dict[str, Any]:
        context = self.get_session(session_id)
        if not context:
            return {'error': 'Session not found'}

        context.teaching_state = TeachingState(
            topic=topic,
            current_point=0,
            讲解进度=outline,
            depth_level=1
        )

        intro = f"同学们好，今天我们来学习【{topic}】。这个内容一共有{len(outline)}个部分，让我们一起来看看吧！"
        response = self._generate_response(context, intro)

        return {
            'intro': intro,
            'response': response,
            'outline': outline
        }

    def continue_teaching(self, session_id: str) -> Dict[str, Any]:
        context = self.get_session(session_id)
        if not context or not context.teaching_state:
            return {'error': 'No teaching in progress'}

        state = context.teaching_state
        if state.current_point >= len(state.讲解进度):
            conclusion = f"好的，同学们，关于【{state.topic}】我们就讲完了。大家有什么问题吗？"
            return {
                'text': conclusion,
                'finished': True
            }

        next_point = state.讲解进度[state.current_point]
        prompt = f"现在请讲解第{state.current_point + 1}点：{next_point}。请用简单易懂的方式讲解，分步骤进行。"

        response = self._generate_response(context, prompt)
        state.current_point += 1

        return {
            'text': response.get('text', ''),
            'current_point': state.current_point,
            'total_points': len(state.讲解进度),
            'finished': False
        }

_manager = None

def get_dialogue_manager() -> DialogueManager:
    global _manager
    if _manager is None:
        _manager = DialogueManager()
    return _manager