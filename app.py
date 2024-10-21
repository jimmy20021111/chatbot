from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate

import tempfile, os
import datetime
import openai
import time

# 初始化 LINE Bot API
#LINE_CHANNEL_ACCESS_TOKEN = 'RBddbMauukL3lZ+ryEsnw91JVq0TJE+RB9+Q0zkplX15Otz2DE0qDcgasVF2vQj+ddb2ALFpDFYVmWflvnYtRWTkrubiSic4rAyBEu7YLnQQNJQ0I24JApAmBJUVO6ddu7VgZMi5XwqX2FYZdRmB/AdB04t89/1O/w1cDnyilFU='
#LINE_CHANNEL_SECRET = 'e17f3f4bd01d523cfb56a2ce34084699'
line_bot_api = LineBotApi('LINE_CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('LINE_CHANNEL_SECRET')

# 初始化 Ollama 模型和 Prompt 模板
template = """
Answer the question below.

Here is the conversation history: {context}

Question: {question}

Answer:
"""
model = OllamaLLM(model="llama3")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

conversation_context = ""  # 存儲對話歷史

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global conversation_context
    user_message = event.message.text  # 獲取用戶的訊息

    # 使用 Ollama 模型進行回應
    try:
        result = chain.invoke({"context": conversation_context, "question": user_message})
        reply = result.strip()
        
        # 更新對話歷史
        conversation_context += f"\nUser: {user_message}\nAI: {reply}"
        
        # 回覆用戶訊息
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )
    except Exception as e:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"發生錯誤：{str(e)}")
        )

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=8000)
