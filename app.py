import gradio as gr
import tempfile
import os
from model import ChatPDF

assistant = ChatPDF()

# 状態管理のための初期化
messages = []

def upload_and_process(files):
    global assistant, messages
    assistant.clear()
    messages.clear()

    for file_path in files:  # file_pathはファイルのパスを示す
        with open(file_path, "rb") as file:
            with tempfile.NamedTemporaryFile(delete=False) as tf:
                tf.write(file.read())
                temp_file_path = tf.name

        assistant.ingest(temp_file_path)
        os.remove(temp_file_path)

    return f"{len(files)} file(s) processed successfully. You can now start chatting."

def chat(user_input):
    global messages, assistant
    if user_input.strip():
        agent_response = assistant.ask(user_input)
        messages.append(("User", user_input))
        messages.append(("Assistant", agent_response))
        return [(msg_type, msg_text) for msg_type, msg_text in messages]

# Gradioのインターフェイス
with gr.Blocks() as demo:
    gr.Markdown("# ChatPDF")

    file_input = gr.File(label="Upload a document", file_count="multiple", type="filepath")
    upload_output = gr.Textbox(label="Upload Status")
    chat_input = gr.Textbox(label="Message", placeholder="Type your message here...")
    chat_output = gr.Chatbot()

    file_input.upload(upload_and_process, file_input, upload_output)
    chat_input.submit(chat, chat_input, chat_output)

demo.launch()
