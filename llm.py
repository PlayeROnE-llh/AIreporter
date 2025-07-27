import prompt
from prompt import PromptEngine
import requests

def generate_analysis_report(data_snapshot, user_prefs, knowledge_base):
    """生成完整分析报告"""
    engine = PromptEngine(knowledge_base)
    report = {}

    # 获取分析类型列表
    analysis_types = user_prefs.get("analysis_types", ["initial_situation", "force_composition"])

    for a_type in analysis_types:
        # 构建分层提示词
        prompt = engine.build_prompt(a_type, data_snapshot, user_prefs)

        # 调用大模型
        response = query_llm_api(
            prompt=prompt,
            model=user_prefs.get("model", "deepseek-r1"),
            temperature=0.3
        )

        report[a_type] = response

    # 整合完整报告
    full_report = integrate_full_report(report, user_prefs)
    return full_report


def query_llm_api(prompt, model, temperature=0.3):
    """调用大模型API"""
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 2000
    }

    try:
        response = requests.post(API_URL, headers=API_HEADERS, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"API调用错误: {str(e)}"


def integrate_full_report(partial_reports, user_prefs):
    """整合各部分报告为完整战报"""
    # 根据用户偏好调整格式
    if user_prefs.get("report_type") == "brief":
        return generate_brief_summary(partial_reports)
    else:
        return "\n\n".join(
            f"=== {section.upper()} ===\n{content}"
            for section, content in partial_reports.items()
        )


def generate_brief_summary(partial_reports):
    """生成简要摘要"""
    # 可以根据实际需求修改
    summary = []
    for section, content in partial_reports.items():
        # 取内容前 50 个字符作为摘要
        summary.append(f"{section}: {content[:50]}...")
    return "\n".join(summary)