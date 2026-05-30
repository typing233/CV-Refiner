import json
import re
import difflib

from openai import OpenAI

from prompts import (
    SYSTEM_OPTIMIZE,
    build_chat_system,
    build_evaluate_system,
    build_evaluate_user,
    build_optimize_user,
)


def _get_client() -> OpenAI:
    return OpenAI()


def evaluate_resume(resume_text: str, jd_text: str | None = None) -> dict:
    client = _get_client()
    system = build_evaluate_system(has_jd=bool(jd_text))
    user_msg = build_evaluate_user(resume_text, jd_text)

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.3,
        max_tokens=4096,
    )
    raw = resp.choices[0].message.content
    return _parse_json(raw)


def generate_optimized_resume(
    resume_text: str, jd_text: str | None, evaluation: dict
) -> str:
    client = _get_client()
    user_msg = build_optimize_user(resume_text, jd_text, json.dumps(evaluation, ensure_ascii=False))

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_OPTIMIZE},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.4,
        max_tokens=4096,
    )
    return resp.choices[0].message.content


def chat_followup(
    messages: list[dict],
    resume_text: str,
    jd_text: str | None,
    report: str,
) -> str:
    client = _get_client()
    system = build_chat_system(resume_text, jd_text, report)

    api_messages = [{"role": "system", "content": system}]
    for msg in messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=api_messages,
        temperature=0.4,
        max_tokens=2048,
    )
    return resp.choices[0].message.content


def format_report(evaluation: dict) -> str:
    if not evaluation:
        return "> 评估结果为空，请重试。"

    report = "# 简历评估报告\n\n"

    overall_score = evaluation.get("overall_score", "N/A")
    report += f"## {_score_emoji(overall_score)} 综合评分：{overall_score}/100\n\n"
    report += f"**评价等级：{_score_level(overall_score)}**\n\n---\n\n"

    report += "## 各维度评分\n\n"
    report += "| 维度 | 评分 | 状态 | 总结 |\n"
    report += "|------|------|------|------|\n"

    dimension_names = {
        "structure": "结构完整性",
        "language": "语言表达",
        "keywords": "关键词覆盖",
        "quantification": "量化成果",
        "redundancy": "冗余内容",
        "job_match": "岗位匹配度",
    }

    dimension_scores = evaluation.get("dimension_scores", {})
    for key, name in dimension_names.items():
        if key not in dimension_scores:
            continue
        dim = dimension_scores[key]
        score = dim.get("score", "N/A")
        summary = dim.get("summary", "-")
        status = _score_bar(score)
        report += f"| {name} | {score}/100 | {status} | {summary} |\n"

    report += "\n---\n\n"

    strengths = evaluation.get("strengths", [])
    if strengths:
        report += "## 简历优点\n\n"
        for s in strengths:
            report += f"- {s}\n"
        report += "\n---\n\n"

    issues = evaluation.get("issues", [])
    if issues:
        report += "## 问题清单\n\n"
        severity_order = {"high": 0, "medium": 1, "low": 2}
        sorted_issues = sorted(issues, key=lambda x: severity_order.get(x.get("severity", "low"), 3))

        for issue in sorted_issues:
            severity = issue.get("severity", "medium")
            severity_label = {"high": "HIGH", "medium": "MEDIUM", "low": "LOW"}.get(severity, "?")
            dimension = dimension_names.get(issue.get("dimension", ""), issue.get("dimension", ""))

            report += f"### [{severity_label}] {issue.get('description', '')}\n\n"
            report += f"- **维度：** {dimension}\n"
            report += f"- **影响：** {issue.get('negative_impact', '')}\n"
            report += f"- **建议：** {issue.get('suggestion', '')}\n"

            example = issue.get("example", "")
            if example:
                report += f"- **示例：** {example}\n"
            report += "\n"

        report += "---\n\n"

    priority_actions = evaluation.get("priority_actions", [])
    if priority_actions:
        report += "## 优先修改事项\n\n"
        for i, action in enumerate(priority_actions, 1):
            report += f"{i}. {action}\n"
        report += "\n"

    return report


def compute_diff(original: str, modified: str) -> str:
    orig_lines = original.splitlines(keepends=True)
    mod_lines = modified.splitlines(keepends=True)

    diff = difflib.unified_diff(
        orig_lines, mod_lines, fromfile="修改前", tofile="修改后", lineterm=""
    )
    diff_text = "".join(diff)
    if not diff_text.strip():
        return "> 无差异"
    return f"```diff\n{diff_text}\n```"


def _parse_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    return {"_raw": raw, "overall_score": "N/A", "dimension_scores": {}, "issues": [], "strengths": [], "priority_actions": []}


def _score_emoji(score):
    if not isinstance(score, (int, float)):
        return ""
    if score >= 90:
        return "S"
    elif score >= 75:
        return "A"
    elif score >= 60:
        return "B"
    elif score >= 40:
        return "C"
    return "D"


def _score_level(score):
    if not isinstance(score, (int, float)):
        return "无法评定"
    if score >= 90:
        return "优秀 - 几乎无需修改"
    elif score >= 75:
        return "良好 - 有小幅优化空间"
    elif score >= 60:
        return "一般 - 存在明显不足"
    elif score >= 40:
        return "较差 - 需要大幅修改"
    return "很差 - 建议重写"


def _score_bar(score):
    if not isinstance(score, (int, float)):
        return "-"
    filled = score // 20
    return "●" * filled + "○" * (5 - filled)
