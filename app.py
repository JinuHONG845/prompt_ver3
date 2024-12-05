import streamlit as st
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
import requests

# API 키 설정 with 예외 처리
try:
    # API 키 존재 여부 확인
    if "api_keys" not in st.secrets:
        st.error("API 키가 설정되지 않았습니다. Streamlit Secrets에서 api_keys 설정을 확인해주세요.")
        st.stop()
    
    # 각 API 키 설정
    openai_client = OpenAI(api_key=st.secrets["api_keys"]["OPENAI_API_KEY"])
    anthropic = Anthropic(api_key=st.secrets["api_keys"]["ANTHROPIC_API_KEY"])
    genai.configure(api_key=st.secrets["api_keys"]["GEMINI_API_KEY"])
    PERPLEXITY_API_KEY = st.secrets["api_keys"]["PERPLEXITY_API_KEY"]
    
except Exception as e:
    st.error(f"API 키 설정 중 오류가 발생했습니다: {str(e)}")
    st.write("현재 설정된 secrets 내용:")
    st.write(st.secrets)
    st.stop()

def get_perplexity_response(prompt):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistral-7b-instruct",
        "messages": [
            {
                "role": "system",
                "content": "Be precise and concise."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.2,
        "top_p": 0.9,
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        
        if 'error' in response_json:
            return f"Perplexity API Error: {response_json['error']}"
            
        if 'choices' in response_json and len(response_json['choices']) > 0:
            return response_json['choices'][0]['message']['content']
        else:
            return "No valid response from Perplexity API"
            
    except requests.exceptions.RequestException as e:
        return f"API Request Error: {str(e)}\nResponse: {response.text if 'response' in locals() else 'No response'}"
    except Exception as e:
        return f"Error processing response: {str(e)}"

def get_chatgpt_response(prompt):
    try:
        client = openai.OpenAI(api_key=st.secrets["api_keys"]["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"ChatGPT Error: {str(e)}"

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
        
        # Create columns based on selected models
        cols = st.columns(len(models))
        
        # 선택된 모델별로 응답 생성
        for col, model in zip(cols, models):
            with col:
                st.markdown(f"### {model}")
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
