"""
技能服务
从GitHub仓库读取技能并管理
"""
import os
import json
import requests
from typing import List, Dict, Any
import git
from pathlib import Path

class SkillService:
    def __init__(self):
        self.skills_repo_url = "https://github.com/Destiny916/frequent-skill.git"
        self.skills_dir = Path("/tmp/skills")
        self.skills_file = self.skills_dir / "skills.json"
        self.skills = []
        self.load_skills()

    def load_skills(self):
        """加载技能，优先从本地文件加载，否则从GitHub仓库拉取"""
        try:
            if self.skills_file.exists():
                with open(self.skills_file, 'r', encoding='utf-8') as f:
                    self.skills = json.load(f)
            else:
                self.fetch_skills_from_github()
        except Exception as e:
            print(f"加载技能失败: {e}")
            self.skills = []

    def fetch_skills_from_github(self):
        """从GitHub仓库拉取技能"""
        try:
            # 克隆或更新仓库
            if self.skills_dir.exists():
                repo = git.Repo(self.skills_dir)
                repo.remotes.origin.pull()
            else:
                self.skills_dir.mkdir(parents=True, exist_ok=True)
                git.Repo.clone_from(self.skills_repo_url, self.skills_dir)

            # 查找skills.json文件
            for root, dirs, files in os.walk(self.skills_dir):
                if "skills.json" in files:
                    skills_path = os.path.join(root, "skills.json")
                    with open(skills_path, 'r', encoding='utf-8') as f:
                        self.skills = json.load(f)
                    # 保存到本地
                    with open(self.skills_file, 'w', encoding='utf-8') as f:
                        json.dump(self.skills, f, ensure_ascii=False, indent=2)
                    break
        except Exception as e:
            print(f"从GitHub拉取技能失败: {e}")
            self.skills = []

    def get_all_skills(self) -> List[Dict[str, Any]]:
        """获取所有技能"""
        return self.skills

    def get_skill_by_id(self, skill_id: str) -> Dict[str, Any]:
        """根据ID获取技能"""
        for skill in self.skills:
            if skill.get('id') == skill_id:
                return skill
        return {}

    def use_skill(self, skill_id: str, context: Dict[str, Any] = None) -> str:
        """使用技能"""
        skill = self.get_skill_by_id(skill_id)
        if not skill:
            return "技能不存在"

        # 这里可以根据技能的类型和参数执行不同的操作
        # 目前简单返回技能描述
        return f"使用技能：{skill.get('name')}\n{skill.get('description')}"

_service = None

def get_skill_service() -> SkillService:
    global _service
    if _service is None:
        _service = SkillService()
    return _service
