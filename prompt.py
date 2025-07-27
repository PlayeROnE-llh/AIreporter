import json


class PromptEngine:
    def __init__(self, knowledge_base):
        self.knowledge_base = knowledge_base
        self.templates = self.load_templates()

    def load_templates(self):
        """加载分层提示模板"""
        return {
            "initial_situation": {
                "system": """你是一位资深的星际争霸2赛事分析师，对游戏的各个阶段有着深入的理解和丰富的实战经验。同时，你也是专业的战报撰写专家，
        擅长将复杂的数据和比赛情况转化为生动、易懂的文字。 你具备对星际争霸2游戏机制、种族特点、战术体系的全面掌握，能够精准地分析比赛数据，
        并将其与比赛的初始态势相结合。同时，你拥有出色的写作能力，能够以清晰、逻辑性强的方式呈现比赛的初始态势。依据用户提供的数据，
        撰写《初始态势》这一部分，清晰地描述比赛开始时的地图特点、双方种族的初始优势与劣势以及双方可能的开局策略，为后续战报的撰写奠定基础。
        该部分应保持客观、准确，避免主观臆断。描述应简洁明了，突出重点，同时确保信息的完整性和准确性。""",
                "structure": {
                    "map_analysis": "地图特点分析",
                    "race_advantages": "种族优劣势分析",
                    "opening_strategy": "开局策略预测"
                }
            },
            "force_composition": {
                "system": """你是一位资深的星际争霸2赛事分析师，对游戏的种族特性、单位属性以及战术运用有着深入的研究和丰富的实践经验，
        能够精准地从大量数据中提取关键信息，并以清晰、专业的语言进行表述。你具备出色的数据分析能力、对星际争霸2各种族单位的深刻理解以及战术洞察力，
        能够快速甄别多余信息，筛选出与兵力编成最相关的数据，并进行逻辑严谨的分析，同时能够识别兵力编成中的潜在弱点。
        根据用户提供的选手种族选择和兵力单元数据，筛选出关键信息，形成准确、精炼且符合比赛战报要求的《兵力编成》内容，
        重点体现兵力规模、进攻、防御、后勤等要素，并关注用于采矿的农民单位变化，同时分析双方兵力编成的潜在缺点。
        分析过程中仅保留最关键、最有用且最符合兵力编成内容的数据，避免无关信息的干扰，确保分析的准确性和专业性，不按前中后期划分，而是从要素角度进行分类分析。""",
                "structure": {
                    "unit_composition": "单位组成分析",
                    "offensive_capability": "进攻能力评估",
                    "defensive_vulnerability": "防御弱点识别"
                }
            }
            # 其他分析类型模板...
        }

    def build_prompt(self, analysis_type, data_snapshot, user_prefs):
        """构建分层提示词"""
        template = self.templates[analysis_type]

        # RAG知识检索
        context = self.retrieve_relevant_knowledge(data_snapshot, analysis_type)

        # 动态模板填充
        prompt = template["system"] + "\n\n"
        prompt += f"## 比赛数据快照:\n{json.dumps(data_snapshot, indent=2)}\n\n"
        prompt += f"## 相关战术知识:\n{context}\n\n"

        # 提示增强（添加示例）
        prompt += self.add_reinforcement_examples(analysis_type, data_snapshot)

        # 答案工程约束
        prompt += "## 输出要求:\n"
        prompt += self.add_output_constraints(template, user_prefs)

        return prompt

    def retrieve_relevant_knowledge(self, data, analysis_type):
        """RAG知识检索"""
        # 根据比赛数据和类型检索相关知识
        race_matchup = f"{data['players'][0]['race']}v{data['players'][1]['race']}"
        query = f"{race_matchup} {analysis_type}"

        # 向量相似度检索
        results = self.knowledge_base.search(query, top_k=3)
        return "\n".join([f"- {res['content']}（来源: {res['source']}）" for res in results])

    def add_reinforcement_examples(self, analysis_type, data):
        """添加增强示例"""
        examples = {
            "initial_situation": [
                {
                    "pattern": "12工蜂连续生产",
                    "tactic": "经济优先开局",
                    "data": "在[t=0-60s]检测到连续SCV生产指令"
                },
                {
                    "pattern": "早期兵营建造",
                    "tactic": "速攻策略",
                    "data": "在t=45s检测到兵营建造指令"
                }
            ]
            # 其他分析类型的示例...
        }

        prompt_section = "## 操作模式参考:\n"
        for example in examples.get(analysis_type, []):
            prompt_section += (
                f"- 模式: {example['pattern']}\n"
                f"  数据表现: {example['data']}\n"
                f"  战术解读: {example['tactic']}\n\n"
            )
        return prompt_section

    def add_output_constraints(self, template, user_prefs):
        """添加输出约束"""
        constraints = "1. 格式: JSON格式\n"
        constraints += "2. 结构要求:\n"

        # 动态结构约束
        for key, desc in template["structure"].items():
            constraints += f"   - {key}: {desc}\n"

        # 受众特定约束
        audience = user_prefs.get("audience", "player")
        if audience == "coach":
            constraints += "3. 必须包含至少1个隐性参数分析(如'经济转化率')\n"
        elif audience == "caster":
            constraints += "3. 突出戏剧性转折点，使用生动叙事\n"

        constraints += f"4. 语言风格: {self.get_style_guidance(audience)}\n"
        return constraints

    def get_style_guidance(self, audience):
        """获取语言风格指导"""
        styles = {
            "player": "专业术语+具体操作建议",
            "coach": "战术深度分析+量化指标",
            "caster": "戏剧性叙事+高潮点突出"
        }
        return styles.get(audience, "专业分析")