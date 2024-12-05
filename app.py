import streamlit as st
import openai
from anthropic import Anthropic
import google.generativeai as genai
import requests
import json

# API 키 설정
openai.api_key = st.secrets["api_keys"]["OPENAI_API_KEY"]
anthropic = Anthropic(api_key=st.secrets["api_keys"]["ANTHROPIC_API_KEY"])
genai.configure(api_key=st.secrets["api_keys"]["GEMINI_API_KEY"])
PERPLEXITY_API_KEY = st.secrets["api_keys"]["PERPLEXITY_API_KEY"]

def get_perplexity_response(prompt):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mixtral-8x7b-instruct",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

def get_chatgpt_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def get_claude_response(prompt):
    message = anthropic.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

def get_gemini_response(prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text

def main():
    st.title("🤖 LLM 비교 애플리케이션")
    
    # 사이드바에 모델 선택
    models = st.sidebar.multiselect(
        "비교할 모델 선택",
        ["Perplexity", "ChatGPT", "Claude", "Gemini"],
        default=["Perplexity", "ChatGPT", "Claude", "Gemini"]
    )
    
    # 프롬프트 입력
    prompt = st.text_area("프롬프트를 입력하세요:", height=100)
    
    if st.button("응답 생성"):
        if not prompt:
            st.warning("프롬프트를 입력해주세요!")
            return
            
        # 선택된 모델별로 응답 생성
        for model in models:
            with st.expander(f"{model} 응답"):
                with st.spinner(f"{model} 응답 생성 중..."):
                    try:
                        if model == "Perplexity":
                            response = get_perplexity_response(prompt)
                        elif model == "ChatGPT":
                            response = get_chatgpt_response(prompt)
                        elif model == "Claude":
                            response = get_claude_response(prompt)
                        else:  # Gemini
                            response = get_gemini_response(prompt)
                        
                        st.write(response)
                    except Exception as e:
                        st.error(f"{model} 에러 발생: {str(e)}")

if __name__ == "__main__":
    main()
