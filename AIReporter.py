import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
import threading
import requests
import json
import sc2reader
from sentence_transformers import SentenceTransformer, util
import torch
import warnings
import os

warnings.filterwarnings("ignore", category=UserWarning, module="torchvision.io.image")

# API 配置
API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_HEADERS = {
    "Authorization": "Bearer sk-lxgilwqdavngoeescfzsygxtcuzhkgxkcwqmpgaxkmoqeoos",
}
MODEL_CONFIG = {
    "deepseek": "deepseek-ai/DeepSeek-R1",
    "deepseek-distill-qwen32b": "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
    "deepseek-r1-8b": "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B"
}

PROMPT_CONFIG = {
    "想定背景": {
        "system": """你是一位资深的星际争霸2战报撰写专家，对星际争霸2的背景设定、游戏机制、种族特性以及电子竞技赛事有着深入的了解和丰富的实践经验。
        你擅长将比赛数据与游戏背景相结合，创作出引人入胜的战报。你拥有电子竞技赛事分析能力、游戏背景知识、数据解读能力以及创意写作技巧，
        能够将比赛数据转化为具有故事性的战报背景。根据比赛数据生成星际争霸2战报的想定背景部分，使背景内容与比赛数据相匹配，同时具有吸引力和可读性。
        战报的背景内容应基于星际争霸2的官方背景设定，不得出现与官方背景相悖的描述。同时，背景内容应简洁明了，避免冗长和复杂的叙述。"""
    },
    "初始态势": {
        "system": """你是一位资深的星际争霸2赛事分析师，对游戏的各个阶段有着深入的理解和丰富的实战经验。同时，你也是专业的战报撰写专家，
        擅长将复杂的数据和比赛情况转化为生动、易懂的文字。 你具备对星际争霸2游戏机制、种族特点、战术体系的全面掌握，能够精准地分析比赛数据，
        并将其与比赛的初始态势相结合。同时，你拥有出色的写作能力，能够以清晰、逻辑性强的方式呈现比赛的初始态势。依据用户提供的数据，
        撰写《初始态势》这一部分，清晰地描述比赛开始时的地图特点、双方种族的初始优势与劣势以及双方可能的开局策略，为后续战报的撰写奠定基础。
        该部分应保持客观、准确，避免主观臆断。描述应简洁明了，突出重点，同时确保信息的完整性和准确性。不使用“综上所述”，改用“总结”作为结尾。"""
    },
    "作战目标": {
        "system": """你是一位专业的星际争霸2战报撰写专家，对星际争霸2的背景设定、游戏机制和电子竞技赛事有深入研究。
        你擅长以详细、清晰的语言呈现作战目标，并能够根据比赛数据生成分阶段的作战目标描述。你具备数据解读能力、背景知识整合能力以及专业写作技巧，
        能够根据比赛数据生成详细且分阶段的作战目标描述。根据比赛数据生成星际争霸2战报的作战目标部分，内容需详细、清晰，避免过多修辞，
        确保作战目标的准确性和专业性。作战目标应细分为前期、中期和后期。作战目标应基于星际争霸2的官方背景设定和游戏机制，
        语言简洁、清晰，避免使用过多修辞和情感化表达。"""
    },
    "兵力编成": {
        "system": """你是一位资深的星际争霸2赛事分析师，对游戏的种族特性、单位属性以及战术运用有着深入的研究和丰富的实践经验，
        能够精准地从大量数据中提取关键信息，并以清晰、专业的语言进行表述。你具备出色的数据分析能力、对星际争霸2各种族单位的深刻理解以及战术洞察力，
        能够快速甄别多余信息，筛选出与兵力编成最相关的数据，并进行逻辑严谨的分析，同时能够识别兵力编成中的潜在弱点。
        根据用户提供的选手种族选择和兵力单元数据，筛选出关键信息，形成准确、精炼且符合比赛战报要求的《兵力编成》内容，
        重点体现兵力规模、进攻、防御、后勤等要素，并关注用于采矿的农民单位变化，同时分析双方兵力编成的潜在缺点。
        分析过程中仅保留最关键、最有用且最符合兵力编成内容的数据，避免无关信息的干扰，确保分析的准确性和专业性，不按前中后期划分，而是从要素角度进行分类分析。"""
    },
    "作战条令与规则": {
        "system": """你是一位经验丰富的星际争霸2战术分析师和规则制定者，对游戏的各个方面都有深刻的认识，能够制定出既严谨又细致的比赛规则。
        你需要具备出色的分析能力、逻辑思维和规则制定技巧，能够确保规则的公平性和可执行性。制定一套严谨、细致、公平的星际争霸2比赛作战条令与规则，
        确保比赛的顺利进行。规则应保持公平性，避免任何可能影响比赛结果的偏见或漏洞，同时确保规则的清晰性和易于理解。
        呈现形式为文字规则文档，包含比赛的作战条令和详细规则。"""
    },
    "仿真推演过程": {
        "system": """你是一位资深的星际争霸2比赛分析师，对游戏的机制、战术和比赛流程有着深入的理解和丰富的实践经验。你具备高度的专业素养，
        能够从海量的时序数据中筛选出关键信息，并以严谨的逻辑和规范的格式呈现比赛过程。你精通星际争霸2的游戏规则、战术体系和单位特性，
        能够对时序数据进行快速分析和鉴别。你具备出色的数据筛选能力，能够识别并剔除无关信息，保留最符合比赛内容的关键数据。
        你擅长以清晰、严谨的语言描述复杂的比赛过程，并能够按照规范的格式进行排版。
        目标：1. 对提供的时序数据进行详细分析，筛选出关键信息。
        2. 去掉不重要的数据，保留最符合比赛内容的部分。
        3. 以严谨的逻辑和规范的格式复现整个比赛的完整过程。
        你必须确保分析过程的严谨性，避免出现错误或遗漏。你应遵循星际争霸2比赛分析的标准规范，确保输出内容的格式规范、清晰易懂。"""
    },
    "战损消耗统计": {
        "system": """你是一位专业的星际争霸2战损消耗统计专家，对游戏的单位损失、资源消耗以及战术执行的量化分析有着丰富的经验和精准的把握。
        你能够从大量数据中准确提取关键信息，确保统计结果的精确性，并结合整体趋势进行科学合理的分析。
        你具备精准的数据筛选与统计能力、对星际争霸2单位和资源系统的深入理解、全面分析能力以及客观评价能力。能够准确统计单位损失和资源消耗，
        并结合整体趋势进行量化分析和评价。目标：1. 从用户提供的数据中筛选出与战损消耗直接相关的全部重要数据。
        2. 对筛选后的数据进行全面且精准的统计，确保数据的完整性和准确性。
        3. 结合整体趋势进行量化分析，评估资源消耗的合理性、性价比以及战术执行的效果。
        分析应基于用户提供的数据，确保统计结果的全面性和准确性。评价应基于数据的量化分析，避免片面性和主观臆断。"""
    }
}


class ReplayAnalyzerApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("星际争霸2录像分析器 v2.0")
        self.geometry("1000x800")
        self.current_file = None
        self.resource_data = None
        self.selected_kbs = []
        self.analysis_results = None
        self.selected_role = "电竞选手"
        self.analysis_type = tk.StringVar(value="想定背景")
        self.bert_model = None
        self.knowledge_base = []
        self.kb_embeddings = []
        self.selected_embedding_model = "all-MiniLM-L6-v2"
        self.build_ui()
        self.initialize_bert()

    def build_ui(self):
        # ------------------------------------------------------------
        # 主容器：上下分区，防止控件被挤出可视区
        # ------------------------------------------------------------
        self.main_container = tk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        # ------------------------------------------------------------
        # 上区：所有控制面板（滚动框，防止超高）
        # ------------------------------------------------------------
        control_scroll = tk.Frame(self.main_container)
        control_scroll.pack(fill=tk.X, pady=(0, 10))

        # 1. 角色选择
        role_frame = tk.Frame(control_scroll)
        role_frame.pack(fill=tk.X, pady=5)
        tk.Label(role_frame, text="选择报告受众:", font=("微软雅黑", 14)).pack(side=tk.LEFT, padx=10)
        self.role_var = tk.StringVar(value=self.selected_role)
        for role in ["电竞选手", "教练员", "解说员", "普通玩家", "观众"]:
            tk.Radiobutton(role_frame, text=role, variable=self.role_var,
                           value=role, font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)

        # 2. 分析模型
        model_frame = tk.Frame(control_scroll)
        model_frame.pack(fill=tk.X, pady=5)
        tk.Label(model_frame, text="选择分析模型:", font=("微软雅黑", 14)).pack(side=tk.LEFT, padx=10)
        self.model_var = tk.StringVar(value="deepseek")
        for model in ["deepseek", "deepseek-distill-qwen32b", "deepseek-r1-8b"]:
            tk.Radiobutton(model_frame, text=model, variable=self.model_var,
                           value=model, font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)

        # 3. BERT 模型
        bert_frame = tk.Frame(control_scroll)
        bert_frame.pack(fill=tk.X, pady=5)
        tk.Label(bert_frame, text="选择 BERT 模型:", font=("微软雅黑", 14)).pack(side=tk.LEFT, padx=10)
        self.bert_model_var = tk.StringVar(value=self.selected_embedding_model)
        for model in ["all-MiniLM-L6-v2", "all-MiniLM-L12-v2", "all-mpnet-base-v2"]:
            tk.Radiobutton(bert_frame, text=model, variable=self.bert_model_var,
                           value=model, command=self.change_bert_model,
                           font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)

        # 4. 知识库
        kb_frame = tk.Frame(control_scroll)
        kb_frame.pack(fill=tk.X, pady=5)
        tk.Label(kb_frame, text="选择知识库文件:", font=("微软雅黑", 14)).pack(side=tk.LEFT, padx=10)
        self.kb_button = tk.Button(kb_frame, text="选择知识库", command=self.select_knowledge_base)
        self.kb_button.pack(side=tk.LEFT, padx=5)
        self.kb_display = tk.Text(kb_frame, height=1, width=60, state=tk.DISABLED,
                                  font=("Consolas", 12))
        self.kb_display.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # 5. 录像文件
        file_frame = tk.Frame(control_scroll)
        file_frame.pack(fill=tk.X, pady=5)
        self.select_btn = tk.Button(file_frame, text="选择录像文件", command=self.select_replay_file,
                                    font=("微软雅黑", 14))
        self.select_btn.pack(side=tk.LEFT, padx=10)

        # 6. 分析类型
        type_frame = tk.Frame(control_scroll)
        type_frame.pack(fill=tk.X, pady=5)
        tk.Label(type_frame, text="分析类型:", font=("微软雅黑", 14)).pack(side=tk.LEFT, padx=10)
        self.analysis_type = tk.StringVar(value="想定背景")
        self.type_menu = tk.OptionMenu(type_frame, self.analysis_type,
                                       *list(PROMPT_CONFIG.keys()) + ["完整报告"],
                                       command=self.on_analysis_type_change)
        self.type_menu.config(font=("微软雅黑", 12), width=15)
        self.type_menu.pack(side=tk.LEFT, padx=5)

        # 7. 按钮组（居中）
        self.action_frame = tk.Frame(control_scroll)
        self.action_frame.pack(pady=10)
        center_btn = tk.Frame(self.action_frame)
        center_btn.pack()
        self.extract_btn = tk.Button(center_btn, text="📊 数据提取", command=self.start_extract,
                                     state=tk.DISABLED, font=("微软雅黑", 14),
                                     bg="#2196F3", fg="white", width=12, height=2)
        self.extract_btn.pack(side=tk.LEFT, padx=15)

        self.analyze_btn = tk.Button(center_btn, text="🚀 开始分析", command=self.start_analyze,
                                     state=tk.DISABLED, font=("微软雅黑", 14),
                                     bg="#4CAF50", fg="white", width=12, height=2)
        self.analyze_btn.pack(side=tk.LEFT, padx=15)

        # ------------------------------------------------------------
        # 下区：结果显示（可纵向扩展）
        # ------------------------------------------------------------
        self.result_frame = tk.Frame(self.main_container)
        self.result_frame.pack(fill=tk.BOTH, expand=True)

        self.toc_frame = tk.Frame(self.result_frame, width=200)
        self.toc_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.toc_listbox = tk.Listbox(self.toc_frame, font=("Consolas", 12))
        self.toc_listbox.pack(fill=tk.BOTH, expand=True)
        self.toc_listbox.bind('<<ListboxSelect>>', self.on_toc_select)

        self.content_frame = tk.Frame(self.result_frame)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.result_text = tk.Text(self.content_frame, wrap=tk.WORD, state=tk.DISABLED,
                                   font=("Consolas", 12), padx=15, pady=15)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self.scrollbar = tk.Scrollbar(self.content_frame, command=self.result_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=self.scrollbar.set)

        # ------------------------------------------------------------
        # 状态栏（始终固定在底部）
        # ------------------------------------------------------------
        self.status = tk.StringVar()
        self.status_bar = tk.Label(self, textvariable=self.status, relief=tk.SUNKEN,
                                   anchor=tk.W, font=("微软雅黑", 10))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.update_status("就绪")
    def initialize_bert(self):
        self.load_bert_model(self.selected_embedding_model)

    def load_bert_model(self, model_name):
        try:
            model_path = f"D:/Desktop/create/BERTopic/{model_name}"
            if os.path.exists(model_path):
                self.bert_model = SentenceTransformer(model_path)
                self.selected_embedding_model = model_name
                self.update_status(f"BERT 模型 {model_name} 加载成功")
            else:
                self.update_status(f"模型路径 {model_path} 不存在")
        except Exception as e:
            self.update_status(f"BERT 模型加载失败: {str(e)}")

    def change_bert_model(self):
        new_model = self.bert_model_var.get()
        self.load_bert_model(new_model)

    def select_knowledge_base(self):
        file_paths = filedialog.askopenfilenames(
            title="选择知识库文件",
            filetypes=[("JSON files", "*.json")]
        )
        if file_paths:
            self.update_status("📂 开始加载知识库...")
            self.load_knowledge_base(file_paths)

    def load_knowledge_base(self, file_paths):
        self.knowledge_base = []
        self.kb_embeddings = []
        for file_path in file_paths:
            try:
                abs_path = os.path.abspath(file_path)
                with open(abs_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.knowledge_base.extend(data)
                    elif isinstance(data, dict):
                        self.knowledge_base.append(data)
                    else:
                        raise ValueError("JSON 根结构必须是列表或字典")
                self.update_status(f"✅ 已加载：{os.path.basename(abs_path)}")
            except Exception as e:
                self.update_status(f"❌ 加载失败：{os.path.basename(file_path)} - {e}")
                return
        if self.knowledge_base:
            self.kb_embeddings = self.generate_kb_embeddings()
            self.display_selected_kbs(file_paths)
            self.update_status(f"✅ 知识库加载成功，共 {len(self.knowledge_base)} 条记录")
        else:
            self.update_status("⚠️ 知识库为空，请检查文件内容")

    def generate_kb_embeddings(self):
        embeddings = []
        for idx, entry in enumerate(self.knowledge_base):
            try:
                name = str(entry.get("名称", ""))
                race = str(entry.get("种族", ""))
                attributes = ", ".join([str(a) for a in entry.get("属性", [])])
                skills = ", ".join([str(s) for s in entry.get("技能", [])])
                tactics = "; ".join([str(t) for t in entry.get("战术手册", [])])

                weapon = entry.get("武器", {})
                weapon_info = ""
                if isinstance(weapon, dict):
                    weapon_info = f"{weapon.get('名称', '')}: {weapon.get('伤害', weapon.get('基础伤害', ''))}"
                elif isinstance(weapon, list):
                    weapon_info = "; ".join([f"{w.get('名称', '')}: {w.get('伤害', w.get('基础伤害', ''))}" for w in weapon])
                else:
                    weapon_info = str(weapon)

                text = f"{name}（{race}）- 属性[{attributes}] 技能[{skills}] 武器[{weapon_info}] 战术[{tactics}]"
                embedding = self.bert_model.encode(text, convert_to_tensor=True)
                embeddings.append(embedding)
            except Exception as e:
                self.update_status(f"⚠️ 第 {idx+1} 条记录嵌入失败：{e}")
                continue
        return embeddings

    def display_selected_kbs(self, file_paths):
        self.kb_display.config(state=tk.NORMAL)
        self.kb_display.delete(1.0, tk.END)
        self.kb_display.insert(tk.END, ", ".join([os.path.basename(p) for p in file_paths]))
        self.kb_display.config(state=tk.DISABLED)
        self.selected_kbs = list(file_paths)

    def select_replay_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("SC2 录像文件", "*.SC2Replay")])
        if file_path:
            self.current_file = file_path
            self.action_frame.pack(pady=20)
            self.extract_btn.config(state=tk.NORMAL)
            self.analyze_btn.config(state=tk.DISABLED)
            self.display_results("已选择文件：" + file_path)

    def start_extract(self):
        self.update_status("正在提取数据...")
        self.extract_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.extract_data, daemon=True).start()

    def extract_data(self):
        try:
            replay = sc2reader.load_replay(self.current_file)
            self.resource_data = generate_resource_and_population_data(replay)
            write_to_json(self.resource_data, "temp_data.json")

            preview = self.generate_preview(self.resource_data)
            self.after(0, lambda: [
                self.update_status("数据提取完成"),
                self.analyze_btn.config(state=tk.NORMAL),
                self.display_results(f"数据预览：\n\n{preview}\n\n点击下方按钮开始专家分析")
            ])
        except Exception as e:
            error_msg = f"{str(e)}\n\n可能原因：\n- 录像文件损坏\n- 不支持的游戏版本\n- 未找到玩家数据"
            self.after(0, lambda msg=error_msg: self.show_error(f"数据提取失败: {msg}"))

    def update_status(self, message):
        self.status.set(f"状态: {message}")
        self.update_idletasks()

    def start_analyze(self):
        selected_type = self.analysis_type.get()
        if selected_type == "完整报告":
            self.update_status("正在生成完整报告...")
            self.analyze_btn.config(state=tk.DISABLED)
            threading.Thread(target=self.generate_full_report, daemon=True).start()
        else:
            self.update_status("开始分析...")
            self.analyze_btn.config(state=tk.DISABLED)
            threading.Thread(target=self.analyze_data, daemon=True).start()

    def generate_preview(self, data):
        preview = []
        try:
            for player_name, player_data in data.items():
                last_res = {
                    "水晶": player_data.get("水晶储量", [{}])[-1].get("数量", 0) if player_data.get("水晶储量") else 0,
                    "气矿": player_data.get("气矿储量", [{}])[-1].get("数量", 0) if player_data.get("气矿储量") else 0,
                    "人口": f"{player_data.get('人口数', [{}])[-1].get('数量', 0)}/{player_data.get('人口上限', [{}])[-1].get('数量', 0)}" if player_data.get('人口上限') else "0/0"
                }

                army_count = player_data.get("军队单位数量", [{}])[-1].get("数量", 0)
                building_count = player_data.get("建筑单位数量", [{}])[-1].get("数量", 0)

                preview.append(
                    f"玩家 [{player_name}]:\n"
                    f"● 最终资源: 水晶{last_res['水晶']} 气矿{last_res['气矿']}\n"
                    f"● 人口状态: {last_res['人口']}\n"
                    f"● 军事单位: {army_count} 建筑单位: {building_count}\n"
                    "────────────────────"
                )
            return "\n".join(preview)
        except Exception as e:
            return f"生成预览时发生错误：{str(e)}"

    def analyze_data(self):
        try:
            selected_model = MODEL_CONFIG[self.model_var.get()]
            selected_type = self.analysis_type.get()
            role = self.role_var.get()

            with open("temp_data.json", 'r', encoding='utf-8') as f:
                data = json.load(f)

            dynamic_content = f"选手全时段战场数据：{json.dumps(data, ensure_ascii=False, indent=2)}"

            system_prompt = PROMPT_CONFIG[selected_type]["system"].format(role=role)

            response = requests.post(
                API_URL,
                headers=API_HEADERS,
                json={
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": dynamic_content}
                    ],
                    "model": selected_model,
                    "temperature": 0.3,
                    "top_p": 0.95,
                    "stop": ["分析结束"]
                }
            )
            response.raise_for_status()
            analysis = response.json()["choices"][0]["message"]["content"]

            self.after(0, lambda: (
                self.display_results(analysis),
                self.update_status("分析完成")
            ))
        except Exception as e:
            error_msg = f"{str(e)}\n\n可能原因：\n- API服务不可用\n- 网络连接问题\n- 模型响应超时"
            self.after(0, lambda msg=error_msg: self.show_error(f"分析失败: {msg}"))

    def generate_full_report(self):
        try:
            selected_model = MODEL_CONFIG[self.model_var.get()]
            role = self.role_var.get()

            self.analysis_results = {}
            for analysis_type in PROMPT_CONFIG.keys():
                with open("temp_data.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)

                dynamic_content = f"选手全时段战场数据：{json.dumps(data, ensure_ascii=False, indent=2)}"

                system_prompt = PROMPT_CONFIG[analysis_type]["system"].format(role=role)

                response = requests.post(
                    API_URL,
                    headers=API_HEADERS,
                    json={
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": dynamic_content}
                        ],
                        "model": selected_model,
                        "temperature": 0.3,
                        "top_p": 0.95,
                        "stop": ["分析结束"]
                    }
                )
                response.raise_for_status()
                self.analysis_results[analysis_type] = response.json()["choices"][0]["message"]["content"]

            full_report = []
            for analysis_type in PROMPT_CONFIG.keys():
                content = self.analysis_results.get(analysis_type, "无分析结果")
                full_report.append(f"===== {analysis_type} =====\n{content}\n\n")

            self.analysis_results["完整报告"] = "".join(full_report)
            self.update_toc()
            self.after(0, lambda: [
                self.display_results(self.analysis_results["完整报告"]),
                self.update_status("完整报告生成完成")
            ])
        except Exception as e:
            error_msg = f"{str(e)}\n\n可能原因：\n- API服务不可用\n- 网络连接问题\n- 模型响应超时"
            self.after(0, lambda msg=error_msg: self.show_error(f"完整报告生成失败: {msg}"))

    def update_toc(self):
        self.toc_listbox.delete(0, tk.END)
        for analysis_type in list(PROMPT_CONFIG.keys()) + ["完整报告"]:
            self.toc_listbox.insert(tk.END, analysis_type)

    def on_toc_select(self, event):
        selected_index = self.toc_listbox.curselection()
        if selected_index:
            selected_type = self.toc_listbox.get(selected_index)
            content = self.analysis_results.get(selected_type, "无此部分分析结果")
            self.display_results(content)

    def display_results(self, text):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.config(state=tk.DISABLED)

    def show_error(self, message):
        self.display_results(f"错误：{message}")
        self.update_status("就绪")

    def on_analysis_type_change(self, *args):
        selected_type = self.analysis_type.get()
        if selected_type == "完整报告":
            self.analyze_btn.config(text="生成完整报告")
        else:
            self.analyze_btn.config(text="开始分析")

# 辅助函数（与原文件一致，略）
def generate_resource_and_population_data(replay):
    frames_per_second = replay.game_fps
    resource_data = {player.name: {"水晶储量": [], "水晶采集速率": [], "气矿储量": [], "气矿采集速率": [], "人口数": [],
                                   "人口上限": [], "军队单位数量": [], "建筑单位数量": []} for player in replay.players}

    for event in replay.tracker_events:
        if isinstance(event, sc2reader.events.tracker.PlayerStatsEvent):
            player_name = event.player.name
            time = event.frame / frames_per_second
            player_data = resource_data[player_name]
            player_data["水晶储量"].append({"time": time, "数量": event.minerals_current})
            player_data["水晶采集速率"].append({"time": time, "数量": event.minerals_collection_rate})
            player_data["气矿储量"].append({"time": time, "数量": event.vespene_current})
            player_data["气矿采集速率"].append({"time": time, "数量": event.vespene_collection_rate})
            player_data["人口数"].append({"time": time, "数量": event.food_used})
            player_data["人口上限"].append({"time": time, "数量": event.food_made})

    for player in replay.players:
        player_name = player.name
        army_units = [unit for unit in player.units if unit.is_army and unit.finished_at]
        building_units = [unit for unit in player.units if unit.is_building and unit.finished_at]

        for unit_list, data_key in [(army_units, "军队单位数量"), (building_units, "建筑单位数量")]:
            unit_list.sort(key=lambda x: x.finished_at)
            timeline = []
            current_count = 0
            for unit in unit_list:
                time = unit.finished_at / frames_per_second
                current_count += 1
                timeline.append({"time": time, "数量": current_count})
            resource_data[player_name][data_key] = timeline

    return resource_data

def write_to_json(resource_data, filename):
    json_data = []
    max_time = 0
    for player_data in resource_data.values():
        for data_type in ['水晶储量', '水晶采集速率', '气矿储量', '气矿采集速率', '人口数', '人口上限']:
            if player_data[data_type]:
                max_entry_time = player_data[data_type][-1]['time']
                if max_entry_time > max_time:
                    max_time = max_entry_time
        if player_data.get('军队单位数量') and player_data['军队单位数量'][-1]['time'] > max_time:
            max_time = player_data['军队单位数量'][-1]['time']
        if player_data.get('建筑单位数量') and player_data['建筑单位数量'][-1]['time'] > max_time:
            max_time = player_data['建筑单位数量'][-1]['time']

    for time in range(0, int(max_time) + 1, 15):
        time_entry = {"time": time}
        for player_name, player_data in resource_data.items():
            player_entry = {"玩家": player_name}
            for data_type in ['水晶储量', '水晶采集速率', '气矿储量', '气矿采集速率', '人口数', '人口上限']:
                entry = next((entry for entry in reversed(player_data[data_type]) if entry['time'] <= time), None)
                player_entry[data_type] = entry['数量'] if entry else None
            army_entry = next((entry for entry in reversed(player_data['军队单位数量']) if entry['time'] <= time), None)
            building_entry = next((entry for entry in reversed(player_data['建筑单位数量']) if entry['time'] <= time), None)
            player_entry['军队单位数量'] = army_entry['数量'] if army_entry else None
            player_entry['建筑单位数量'] = building_entry['数量'] if building_entry else None
            time_entry[player_name] = player_entry
        json_data.append(time_entry)
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(json_data, jsonfile, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    app = ReplayAnalyzerApp()
    app.mainloop()