import streamlit as st
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
import requests
import json

# 페이지 설정
st.set_page_config(
    page_title="AI 모델 비교",
    layout="wide"
)

# API 클라이언트 초기화 함수들
def init_openai():
    try:
        return OpenAI(api_key=str(st.secrets["OPENAI_API_KEY"]))
    except Exception as e:
        st.error("OpenAI API 키 설정에 문제가 있습니다.")
        return None

def init_anthropic():
    try:
        return Anthropic(api_key=str(st.secrets["ANTHROPIC_API_KEY"]))
    except Exception as e:
        st.error("Anthropic API 키 설정에 문제가 있습니다.")
        return None

def init_gemini():
    try:
        genai.configure(api_key=str(st.secrets["GOOGLE_API_KEY"]))
        return True
    except Exception as e:
        st.error("Google API 키 설정에 문제가 있습니다.")
        return False

def get_perplexity_headers():
    try:
        return {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {str(st.secrets['PERPLEXITY_API_KEY'])}"
        }
    except Exception as e:
        st.error("Perplexity API 키 설정에 문제가 있습니다.")
        return None

# API 클라이언트 초기화
openai_client = init_openai()
anthropic_client = init_anthropic()
gemini_initialized = init_gemini()

# 사이드바 설정
st.sidebar.title("AI 모델 선택")

# 모델 선택 (다중 선택 가능)
selected_models = st.sidebar.multiselect(
    "비교할 모델을 선택하세요 (다중 선택 가능):",
    [
        "Perplexity",
        "GPT-4 Turbo",
        "GPT-3.5 Turbo",
        "Claude 3 Sonnet",
        "Claude 3 Haiku",
        "Gemini Pro",
        "Gemini Nano"
    ]
)

# 메인 영역
st.title("AI 모델 비교 테스트")

# 사용자 입력
user_input = st.text_area("프롬프트를 입력하세요:", height=200)

# 전송 버튼
if st.button("전송"):
    if not user_input:
        st.warning("프롬프트를 입력해주세요.")
    elif not selected_models:
        st.warning("최소 하나의 모델을 선택해주세요.")
    else:
        # 선택된 각 모델에 대해 응답 생성
        for model in selected_models:
            with st.expander(f"{model} 응답", expanded=True):
                with st.spinner("응답 생성 중..."):
                    try:
                        if model == "Perplexity":
                            headers = get_perplexity_headers()
                            if headers:
                                url = "https://api.perplexity.ai/chat/completions"
                                payload = {
                                    "model": "pplx-70b",
                                    "messages": [{"role": "user", "content": user_input}],
                                    "max_tokens": 1024,
                                    "temperature": 0.7
                                }
                                
                                response = requests.post(url, json=payload, headers=headers)
                                
                                if response.status_code == 200:
                                    result = response.json()
                                    st.write(result["choices"][0]["message"]["content"])
                                else:
                                    st.error(f"API 오류: {response.status_code}")
                                    st.error(f"오류 상세: {response.text}")
                        
                        elif "GPT" in model and openai_client:
                            model_name = "gpt-4-turbo-preview" if "GPT-4" in model else "gpt-3.5-turbo"
                            completion = openai_client.chat.completions.create(
                                model=model_name,
                                messages=[{"role": "user", "content": user_input}]
                            )
                            st.write(completion.choices[0].message.content)
                        
                        elif "Claude" in model and anthropic_client:
                            model_name = "claude-3-sonnet-20240229" if "Sonnet" in model else "claude-3-haiku-20240307"
                            response = anthropic_client.messages.create(
                                model=model_name,
                                messages=[{"role": "user", "content": user_input}]
                            )
                            st.write(response.content[0].text)
                        
                        elif "Gemini" in model and gemini_initialized:
                            model_name = 'gemini-pro' if "Pro" in model else 'gemini-nano'
                            model = genai.GenerativeModel(model_name)
                            response = model.generate_content(user_input)
                            st.write(response.text)
                    
                    except Exception as e:
                        st.error(f"오류 발생: {str(e)}") 