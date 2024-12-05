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

# API 키 검증 및 초기화 함수들
def validate_api_keys():
    """API 키 존재 여부 확인 및 검증"""
    required_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "PERPLEXITY_API_KEY", "GEMINI_API_KEY"]
    missing_keys = [key for key in required_keys if key not in st.secrets]
    if missing_keys:
        st.error(f"Missing API keys: {', '.join(missing_keys)}")
        return False
    return True

def get_perplexity_client():
    """Perplexity API 클라이언트 설정"""
    if "PERPLEXITY_API_KEY" not in st.secrets:
        st.error("Perplexity API key is missing")
        return None
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {st.secrets['PERPLEXITY_API_KEY']}"
    }
    return headers

def get_openai_client():
    """OpenAI 클라이언트 설정"""
    try:
        return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    except Exception as e:
        st.error(f"OpenAI client error: {str(e)}")
        return None

def get_anthropic_client():
    """Anthropic 클라이언트 설정"""
    try:
        return Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    except Exception as e:
        st.error(f"Anthropic client error: {str(e)}")
        return None

def setup_gemini():
    """Gemini 설정"""
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return True
    except Exception as e:
        st.error(f"Gemini setup error: {str(e)}")
        return False

# API 키 검증
if not validate_api_keys():
    st.stop()

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
                                url = "https://api.perplexity.ai/chat/completions"
                                payload = {
                                    "model": "llama-2-70b-chat",
                                    "messages": [{"role": "user", "content": user_input}],
                                    "max_tokens": 1024,
                                    "temperature": 0.7
                                }
                                
                                # 디버깅 정보 출력
                                st.write("요청 헤더:", headers)
                                st.write("요청 페이로드:", payload)
                                
                                response = requests.post(url, json=payload, headers=headers)
                                st.write("API 응답 상태:", response.status_code)
                                
                                if response.status_code == 200:
                                    result = response.json()
                                    st.write(result["choices"][0]["message"]["content"])
                                else:
                                    st.error(f"API 오류: {response.status_code}")
                                    st.error(f"오류 상세: {response.text}")
                            
                        elif "GPT" in model:
                            client = get_openai_client()
                            if client:
                                model_name = "gpt-4-turbo-preview" if "GPT-4" in model else "gpt-3.5-turbo"
                                completion = client.chat.completions.create(
                                    model=model_name,
                                    messages=[{"role": "user", "content": user_input}]
                                )
                                st.write(completion.choices[0].message.content)
                            
                        elif "Claude" in model:
                            client = get_anthropic_client()
                            if client:
                                model_name = "claude-3-opus-20240229" if "Opus" in model else "claude-3-sonnet-20240229"
                                response = client.messages.create(
                                    model=model_name,
                                    messages=[{"role": "user", "content": user_input}]
                                )
                                st.write(response.content[0].text)
                            
                        elif "Gemini" in model:
                            if setup_gemini():
                                model_name = 'gemini-ultra' if "Ultra" in model else 'gemini-pro'
                                model = genai.GenerativeModel(model_name)
                                response = model.generate_content(user_input)
                                st.write(response.text)
                            
                    except Exception as e:
                        st.error(f"오류 발생: {str(e)}") 