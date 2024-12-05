import streamlit as st
import openai
from anthropic import Anthropic
import google.generativeai as genai
from perplexity import Perplexity

# API 키 설정
openai.api_key = st.secrets["OPENAI_API_KEY"]
anthropic = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
perplexity = Perplexity(api_key=st.secrets["PERPLEXITY_API_KEY"])

# 페이지 설정
st.set_page_config(page_title="LLM 성능 비교", layout="wide")
st.title("LLM 성능 비교 도구")

# 모델 선택
models = {
    "Perplexity": "pplx-7b-online",
    "GPT-4": "gpt-4",
    "GPT-3.5-Turbo": "gpt-3.5-turbo",
    "Claude-3 Sonnet": "claude-3-sonnet",
    "Claude-3 Haiku": "claude-3-haiku",
    "Gemini Pro": "gemini-pro",
    "Gemini Nano": "gemini-nano"
}

# 사용자 입력
user_input = st.text_area("질문을 입력하세요:", height=100)
selected_models = st.multiselect("비교할 모델을 선택하세요:", list(models.keys()))

if st.button("응답 생성") and user_input and selected_models:
    # 각 모델별 응답 생성
    for model_name in selected_models:
        st.subheader(f"{model_name} 응답:")
        
        try:
            if model_name.startswith("GPT"):
                response = openai.ChatCompletion.create(
                    model=models[model_name],
                    messages=[{"role": "user", "content": user_input}]
                )
                st.write(response.choices[0].message.content)
                
            elif model_name.startswith("Claude"):
                response = anthropic.messages.create(
                    model=models[model_name],
                    messages=[{"role": "user", "content": user_input}]
                )
                st.write(response.content[0].text)
                
            elif model_name.startswith("Gemini"):
                model = genai.GenerativeModel(models[model_name])
                response = model.generate_content(user_input)
                st.write(response.text)
                
            elif model_name == "Perplexity":
                response = perplexity.chat(user_input)
                st.write(response['output'])
                
        except Exception as e:
            st.error(f"{model_name} 에러 발생: {str(e)}")
            
    # 응답 비교를 위한 표 추가
    st.subheader("응답 비교")
    comparison_data = []
    for model_name in selected_models:
        comparison_data.append({
            "모델": model_name,
            "토큰 수": len(user_input.split()),  # 간단한 예시, 실제로는 더 정확한 토큰 계산이 필요
            "응답 시간": "측정 필요"  # 실제 구현시 시간 측정 로직 추가 필요
        })
    
    st.table(comparison_data)

# 사용 안내
with st.expander("사용 방법"):
    st.markdown("""
    1. 질문을 입력창에 입력하세요.
    2. 비교하고 싶은 모델들을 선택하세요.
    3. '응답 생성' 버튼을 클릭하세요.
    4. 각 모델의 응답을 비교해보세요.
    """)
