import gradio as gr
from dotenv import load_dotenv

from cv_engine import (
    chat_followup,
    compute_diff,
    evaluate_resume,
    format_report,
    generate_optimized_resume,
)
from document_parser import extract_text

load_dotenv()


def run_evaluation(file, resume_text, jd_text):
    text = ""
    if file is not None:
        try:
            text = extract_text(file.name)
        except Exception as e:
            return f"> 文件解析失败：{e}", "", "", {}, "", ""
    if not text.strip():
        text = resume_text or ""

    if not text.strip():
        return "> 请上传简历文件或粘贴简历文本。", "", "", {}, "", ""

    if len(text.strip()) < 100:
        return "> 简历内容过短（少于100字符），请提供完整简历。", "", "", {}, "", ""

    jd = jd_text.strip() if jd_text else None

    evaluation = evaluate_resume(text, jd)
    report = format_report(evaluation)
    optimized = generate_optimized_resume(text, jd, evaluation)
    diff = compute_diff(text, optimized)

    return report, optimized, diff, evaluation, text, jd or ""


def chat_respond(message, history, evaluation_state, resume_state, jd_state):
    if not evaluation_state:
        return "请先在「简历评估」标签页完成评估后再进行追问。"

    report = format_report(evaluation_state)
    messages = []
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    response = chat_followup(messages, resume_state, jd_state or None, report)
    return response


with gr.Blocks(title="CV-Refiner 简历评估优化") as app:
    gr.Markdown("# CV-Refiner 简历评估与优化\n\n上传简历、输入目标职位描述，获取定制化评估报告和优化建议。")

    evaluation_state = gr.State({})
    resume_state = gr.State("")
    jd_state = gr.State("")

    with gr.Tabs():
        with gr.TabItem("简历评估"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 输入")
                    file_input = gr.File(
                        label="上传简历（PDF / DOCX / TXT）",
                        file_types=[".pdf", ".docx", ".doc", ".txt", ".md"],
                    )
                    resume_input = gr.Textbox(
                        label="或粘贴简历文本",
                        placeholder="将简历内容粘贴在此处（与文件上传二选一）...",
                        lines=10,
                    )
                    jd_input = gr.Textbox(
                        label="目标职位描述（推荐填写）",
                        placeholder="粘贴目标岗位的 JD，评估将针对该岗位进行定制化分析...",
                        lines=6,
                    )
                    eval_btn = gr.Button("开始评估", variant="primary", size="lg")

                with gr.Column(scale=2):
                    gr.Markdown("### 评估结果")
                    report_output = gr.Markdown(label="评估报告")

                    with gr.Accordion("优化后的简历草稿", open=False):
                        optimized_output = gr.Markdown(label="优化简历")

                    with gr.Accordion("修改前后对比", open=False):
                        diff_output = gr.Markdown(label="Diff")

            eval_btn.click(
                fn=run_evaluation,
                inputs=[file_input, resume_input, jd_input],
                outputs=[report_output, optimized_output, diff_output, evaluation_state, resume_state, jd_state],
            )

        with gr.TabItem("对话追问"):
            gr.Markdown("### 针对评估结果进行追问\n\n完成评估后，可以在此询问具体修改建议、要求逐条修改、或对比修改前后差异。")
            chatbot = gr.Chatbot(height=450)
            chat_input = gr.Textbox(
                label="输入问题",
                placeholder="例如：工作经历部分应该怎么改？/ 帮我重写项目经验第一条 / 量化成果有哪些改进空间？",
                lines=2,
            )
            send_btn = gr.Button("发送", variant="primary")

            def user_send(message, history, eval_st, resume_st, jd_st):
                if not message.strip():
                    return history, ""
                response = chat_respond(message, history, eval_st, resume_st, jd_st)
                history = history + [
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": response},
                ]
                return history, ""

            send_btn.click(
                fn=user_send,
                inputs=[chat_input, chatbot, evaluation_state, resume_state, jd_state],
                outputs=[chatbot, chat_input],
            )
            chat_input.submit(
                fn=user_send,
                inputs=[chat_input, chatbot, evaluation_state, resume_state, jd_state],
                outputs=[chatbot, chat_input],
            )


if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, theme=gr.themes.Soft())
