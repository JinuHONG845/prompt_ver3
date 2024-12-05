import streamlit as st
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai

# 페이지 설정
st.set_page_config(
    page_title="AI 모델 비교",
    layout="wide"
)

# 사이드바 설정
st.sidebar.title("AI 모델 선택")

# 모델 선택 (다중 선택 가능)
selected_models = st.sidebar.multiselect(
    "비교할 모델을 선택하세요 (다중 선택 가능):",
    [
        "Perplexity",
        "GPT-4 Turbo (최고 성능)",
        "GPT-3.5 Turbo (가성비)",
        "Claude 3 Opus (최고 성능)",
        "Claude 3 Sonnet (가성비)",
        "Gemini Ultra (최고 성능)",
        "Gemini Pro (가성비)"
    ]
)

# 메인 영역
st.title("AI 모델 비교 테스트")

# 사용자 입력
user_input = st.text_area("프롬프트를 입력하세요:", height=200)

# API 클라이언트 초기화 함수들
def get_openai_client():
    try:
        return OpenAI(api_key=str(st.secrets["OPENAI_API_KEY"]))
    except Exception as e:
        st.error("OpenAI API 키 설정에 문제가 있습니다.")
        return None

def get_anthropic_client():
    try:
        return Anthropic(api_key=str(st.secrets["ANTHROPIC_API_KEY"]))
    except Exception as e:
        st.error("Anthropic API 키 설정에 문제가 있습니다.")
        return None

def setup_gemini():
    try:
        genai.configure(api_key=str(st.secrets["GEMINI_API_KEY"]))
        return True
    except Exception as e:
        st.error("Gemini API 키 설정에 문제가 있습니다.")
        return False

def get_perplexity_client():
    try:
        headers = {
            "Authorization": f"Bearer {str(st.secrets['PERPLEXITY_API_KEY'])}",
            "Content-Type": "application/json"
        }
        return headers
    except Exception as e:
        st.error("Perplexity API 키 설정에 문제가 있습니다.")
        return None

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
                            headers = get_perplexity_client()
                            if headers:
                                try:
                                    import requests
                                    url = "https://api.perplexity.ai/chat/completions"
                                    payload = {
                                        "model": "pplx-7b-chat",  # 또는 "pplx-70b-chat", "pplx-7b-online" 등
                                        "messages": [
                                            {
                                                "role": "user",
                                                "content": user_input
                                            }
                                        ]
                                    }
                                    response = requests.post(url, json=payload, headers=headers)
                                    if response.status_code == 200:
                                        response = response.json()["choices"][0]["message"]["content"]
                                    else:
                                        response = f"API 오류: {response.status_code}"
                                except Exception as e:
                                    response = f"오류 발생: {str(e)}"
                            else:
                                continue
                        
                        elif "GPT" in model:
                            client = get_openai_client()
                            if client:
                                model_name = "gpt-4-turbo-preview" if "GPT-4" in model else "gpt-3.5-turbo"
                                response = client.chat.completions.create(
                                    model=model_name,
                                    messages=[{"role": "user", "content": user_input}]
                                ).choices[0].message.content
                            else:
                                continue
                        
                        elif "Claude" in model:
                            client = get_anthropic_client()
                            if client:
                                model_name = "claude-3-opus-20240229" if "Opus" in model else "claude-3-sonnet-20240229"
                                response = client.messages.create(
                                    model=model_name,
                                    messages=[{"role": "user", "content": user_input}]
                                ).content[0].text
                            else:
                                continue
                        
                        elif "Gemini" in model:
                            if setup_gemini():
                                model_name = "gemini-ultra" if "Ultra" in model else "gemini-pro"
                                model = genai.GenerativeModel(model_name)
                                response = model.generate_content(user_input).text
                        
                        st.write(response)
                    
                    except Exception as e:
                        st.error(f"오류가 발생했습니다: {str(e)}") 