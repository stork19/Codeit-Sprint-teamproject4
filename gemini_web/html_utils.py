import re
from flask import Markup

def to_html(text):
    html_output = ""
    lines = text.splitlines()
    category = None
    in_list = False  # 목록 안에 있는지 여부를 추적하는 변수 추가

    for line in lines:
        line = line.strip()
        if not line:
            if in_list: # 빈 줄인데 목록 안에 있었다면 목록 닫기
                html_output += "</ul>"
                in_list = False
            continue

        if line.startswith("**"):
            if in_list: # 새로운 카테고리가 시작되기 전에 이전 목록 닫기
                html_output += "</ul>"
                in_list = False
            category = line.replace("**", "").strip()
            html_output += f"<h2 class='category'>{category}</h2>"
        elif line.startswith("*"):
            if not in_list: # 목록 시작
                html_output += "<ul>"
                in_list = True
            question_text = line.replace("*", "").strip()
            question_text = re.sub(r"\*\*(.*?)\*\*", r"<span class='emphasized'>\1</span>", question_text)
            html_output += f"<li><p class='question'>{question_text}</p></li>"
        else: # 일반 텍스트 처리 (필요한 경우)
            if in_list: # 목록 안에 있었다면 목록 닫기
                html_output += "</ul>"
                in_list = False
            html_output += f"<p>{line}</p>" # 추가된 부분

    if in_list: # 마지막 ul 닫기 (이전 코드와 위치 동일)
        html_output += "</ul>"

    return Markup(html_output)