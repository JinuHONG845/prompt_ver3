import streamlit as st
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai

# API 키 설정 부분 수정
try:
    openai_client = OpenAI(api_key=str(st.secrets["OPENAI_API_KEY"]))
    anthropic_client = Anthropic(api_key=str(st.secrets["ANTHROPIC_API_KEY"]))
    genai.configure(api_key=str(st.secrets["GEMINI_API_KEY"]))
except Exception as e:
    st.error("API 키 설정에 문제가 있습니다. 관리자에게 문의하세요.")
    st.stop()

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
                            # Perplexity API 구현 필요
                            response = "Perplexity API 구현 필요"
                        
                        elif model == "GPT-4 Turbo (최고 성능)":
                            response = openai_client.chat.completions.create(
                                model="gpt-4-turbo-preview",
                                messages=[{"role": "user", "content": user_input}]
                            ).choices[0].message.content
                        
                        elif model == "GPT-3.5 Turbo (가성비)":
                            response = openai_client.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=[{"role": "user", "content": user_input}]
                            ).choices[0].message.content
                        
                        elif model == "Claude 3 Opus (최고 성능)":
                            response = anthropic_client.messages.create(
                                model="claude-3-opus-20240229",
                                messages=[{"role": "user", "content": user_input}]
                            ).content[0].text
                        
                        elif model == "Claude 3 Sonnet (가성비)":
                            response = anthropic_client.messages.create(
                                model="claude-3-sonnet-20240229",
                                messages=[{"role": "user", "content": user_input}]
                            ).content[0].text
                        
                        elif model == "Gemini Ultra (최고 성능)":
                            model = genai.GenerativeModel('gemini-ultra')
                            response = model.generate_content(user_input).text
                        
                        elif model == "Gemini Pro (가성비)":
                            model = genai.GenerativeModel('gemini-pro')
                            response = model.generate_content(user_input).text
                        
                        st.write(response)
                    
                    except Exception as e:
                        st.error(f"오류가 발생했습니다: {str(e)}") 