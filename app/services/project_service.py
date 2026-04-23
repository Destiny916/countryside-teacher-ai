"""
项目计划书生成服务
根据学校基本信息生成乡村教育数字化项目计划书
"""
from typing import Dict, List, Optional, Any
import json
from model_service.inference import get_vllm_client

PROJECT_PLAN_TEMPLATE = """请为以下乡村学校生成一份教育数字化项目计划书：

## 学校基本信息
- 学校名称：{school_name}
- 学生人数：{student_count}人
- 教师人数：{teacher_count}人
- 年级设置：{grade_settings}
- 当前网络状况：{network_status}
- 现有设备情况：{existing_equipment}
- 预算范围：{budget_range}

## 建设目标
{construction_goals}

## 项目类型
{project_type}

请生成完整的项目计划书，包括以下章节：
1. 项目背景与必要性
2. 建设目标与内容
3. 技术方案设计
4. 设备清单与预算明细
5. 实施进度计划
6. 风险评估与对策
7. 预期效果与评估指标

请用JSON格式输出。
"""

PROJECT_TYPES = {
    "infrastructure": "基础设施建设（网络、机房、多媒体教室）",
    "informationization": "教育信息化升级（智慧校园、在线教学平台）",
    "hybrid": "混合方案（基础设施+信息化）"
}

class ProjectPlanService:
    def __init__(self):
        self.vllm_client = get_vllm_client()

    def generate_project_plan(
        self,
        school_name: str,
        student_count: int,
        teacher_count: int,
        grade_settings: str,
        network_status: str,
        existing_equipment: str,
        budget_range: str,
        construction_goals: str = None,
        project_type: str = "hybrid"
    ) -> Dict[str, Any]:
        if construction_goals is None:
            construction_goals = "提升学校信息化教学水平，改善教学环境"

        project_type_desc = PROJECT_TYPES.get(project_type, PROJECT_TYPES["hybrid"])

        prompt = PROJECT_PLAN_TEMPLATE.format(
            school_name=school_name,
            student_count=student_count,
            teacher_count=teacher_count,
            grade_settings=grade_settings,
            network_status=network_status,
            existing_equipment=existing_equipment,
            budget_range=budget_range,
            construction_goals=construction_goals,
            project_type=project_type_desc
        )

        try:
            result = self.vllm_client.chat(
                messages=[
                    {"role": "system", "content": "你是一位教育信息化专家，擅长撰写乡村教育数字化项目计划书。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            plan_text = result['choices'][0]['message']['content']
            plan = self._parse_plan(plan_text)
        except Exception as e:
            print(f"项目计划书生成失败: {e}")
            plan = self._generate_fallback_plan(school_name, student_count, teacher_count)

        return {
            'success': True,
            'plan': plan,
            'school_name': school_name,
            'project_type': project_type
        }

    def _parse_plan(self, text: str) -> Dict[str, Any]:
        try:
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                json_str = text.split("```")[1].split("```")[0]
            else:
                json_str = text

            return json.loads(json_str.strip())
        except json.JSONDecodeError:
            return {'content': text, 'format': 'text'}

    def _generate_fallback_plan(
        self,
        school_name: str,
        student_count: int,
        teacher_count: int
    ) -> Dict[str, Any]:
        student_per_teacher = student_count / teacher_count if teacher_count > 0 else 0

        return {
            "项目背景与必要性": f"{school_name}现有学生{student_count}人，教师{teacher_count}人，亟需推进教育数字化转型。",
            "建设目标与内容": [
                "建设高速校园网络",
                "部署多媒体教学设备",
                "搭建在线教学平台",
                "培训教师信息化能力"
            ],
            "技术方案设计": "采用云端+本地混合架构，确保系统稳定性和数据安全。",
            "设备清单与预算明细": {
                "网络设备": f"约{student_count * 100}元",
                "多媒体设备": f"约{teacher_count * 2000}元",
                "服务器": "约50000元",
                "软件平台": "约30000元",
                "培训费用": "约20000元",
                "总计": "约150000-200000元"
            },
            "实施进度计划": [
                "第1-2月：需求调研与方案设计",
                "第3-4月：设备采购与安装",
                "第5-6月：平台部署与调试",
                "第7-8月：人员培训与试运行",
                "第9月：正式上线与验收"
            ],
            "风险评估与对策": [
                "风险1：网络基础设施不完善 → 提前进行网络改造",
                "风险2：教师接受度低 → 加强培训与激励"
            ],
            "预期效果与评估指标": f"建成后，师生比达到1:{int(student_per_teacher)}，多媒体教室覆盖率达到100%。"
        }

_service = None

def get_project_service() -> ProjectPlanService:
    global _service
    if _service is None:
        _service = ProjectPlanService()
    return _service