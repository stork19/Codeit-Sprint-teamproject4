import os, json, re

import pandas as pd
import google.generativeai as genai

from flask import Flask, render_template, request, Markup
from urllib.parse import unquote # URL 디코딩을 위한 import 추가

## def 함수 모듈 불러오기
from gcs_utils import download_csv_from_gcs # gcs_utils.py 임포트
from html_utils import to_html # html_utils.py 임포트

# 환경 변수에 JSON 키 파일 설정 (Flask 앱 시작 전에 설정)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./config/codeit-project-567b5092fd38.json"

with open("config/gemini_api.json", "r") as f:
    credentials = json.load(f)
    google_api_key = credentials["google_gemini_api_key"]

GOOGLE_API_KEY = google_api_key

# Gemini API 설정
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-pro")

app = Flask(__name__)

# GCS 설정
BUCKET_NAME = "finalproject_sprint" 
PREFIX = "question_data/modified" 

# 데이터 로딩 (앱 시작 시 한 번만 실행)
try:
    dataframes, file_names = download_csv_from_gcs(BUCKET_NAME, PREFIX)
    if dataframes:
        data = pd.concat(dataframes.values(), ignore_index=True)
        # year_month 컬럼이 있는지 확인하고 없다면 생성
        if 'year_month' not in data.columns:
            try:
                data['year_month'] = pd.to_datetime(data['date']).dt.strftime('%Y년 %m월')
            except:
                print('date column 형식이 적절하지 않아 year_month 생성을 실패했습니다.')
                raise
        question_data = {}
        for ym in data['year_month'].unique():
            questions = data[data['year_month'] == ym]
            if not questions.empty:
                # 동일한 year_month가 여러 번 나올 경우, 최신 데이터로 덮어쓰기
                question_data[ym] = {
                    "questions": questions,
                    "keywords": questions.iloc[0].keywords_with_w2v if 'keywords_with_w2v' in questions.columns else None
                }
        print("GCS에서 데이터 로딩 완료")
    else:
        print("GCS에서 데이터를 불러오는데 실패했습니다.")
        question_data = {}
except Exception as e:
    print(f"초기 데이터 로딩 중 오류 발생: {e}")
    question_data = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_date = None
    gemini_response = None

    if request.method == 'POST':
        selected_date = request.form.get('date')
        if selected_date: # 이 조건문 하나만 있으면 됩니다.
            if selected_date in question_data and question_data[selected_date]["keywords"] is not None:
                keywords = question_data[selected_date]["keywords"]
                prompt = f"청소년 친구들이 좋아할 만한 질문을 {keywords}의 단어들을 이용해서 만들어 줘."
                try:
                    response = model.generate_content(prompt)
                    gemini_response = unquote(response.text)
                    gemini_response = to_html(gemini_response)
                except Exception as e:
                    gemini_response = f"Gemini API 호출 중 오류 발생: {e}"
            else:
                gemini_response = f"{selected_date}에 대한 데이터 또는 키워드가 없습니다."

    return render_template('index.html', question_data=question_data, selected_date=selected_date, gemini_response=gemini_response)

if __name__ == '__main__':
    app.run(debug=True)