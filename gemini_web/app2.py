from flask import Flask, render_template, request, Markup, redirect, url_for
import google.generativeai as genai
import json, re, os
from urllib.parse import unquote  # URL 디코딩을 위한 import

app = Flask(__name__)

# API 키 로드
try:
    with open(os.path.join(os.path.dirname(__file__), "config/gemini_api.json"), "r") as f:
        credentials = json.load(f)
        google_api_key = credentials["google_gemini_api_key"]
except FileNotFoundError:
    print("Error: gemini_api.json not found in config directory")
    exit()
except KeyError:
    print("Error: google_gemini_api_key not found in gemini_api.json")
    exit()

GOOGLE_API_KEY = google_api_key
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')


def to_html(text):
    text = unquote(text) # URL 디코딩 추가
    html_output = ""
    lines = text.splitlines() # 줄 단위로 분리

    for line in lines:
        line = line.strip()
        if not line: # 빈 줄은 무시
            continue
        if line.startswith("#"):
            level = line.count("#")
            html_output += f"<h{level}>{line.lstrip('#').strip()}</h{level}>"
        elif re.match(r"^\d+\.\s*\*\*.*?\*\*\s*(\(.*\))?$", line): # 번호, 굵은 글씨, 괄호 패턴 매치
            match = re.match(r"^(\d+\.)\s*\*\*(.*?)\*\*\s*(\(.*\))?$", line)
            number = match.group(1)
            question = match.group(2)
            explanation = match.group(3) if match.group(3) else ""
            html_output += f"<p><strong>{number}</strong> <strong>{question}</strong> {explanation}</p>"
        else: # 그 외 모든 줄은 문단으로 처리
            html_output += f"<p>{line}</p>"

    return Markup(html_output)

@app.route("/", methods=["GET", "POST"])
def index():
    prompt = ""
    if request.method == "POST":
        prompt = request.form["prompt"]
        try:
            response = model.generate_content(prompt)
            return redirect(url_for('result', generated_text=response.text))
        except Exception as e:
            return render_template("index2.html", error=str(e), prompt=prompt)
    return render_template("index2.html", prompt=prompt)

@app.route("/result")
def result():
    generated_text = request.args.get('generated_text', '')
    html_text = to_html(generated_text)
    return render_template("result.html", generated_text=html_text)

if __name__ == "__main__":
    app.run(debug=True)