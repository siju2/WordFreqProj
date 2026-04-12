import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from wordcloud import WordCloud
from collections import Counter
import re
import os
import colorsys

st.set_page_config(page_title="단어 빈도수 분석", layout="wide")

# 한글 폰트 설정
font_path = None
font_list = [
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "C:/Windows/Fonts/malgun.ttf",
    "/Library/Fonts/AppleGothic.ttf"
]
for f in font_list:
    if os.path.exists(f):
        font_path = f
        break

if font_path:
    fm.fontManager.addfont(font_path)
    plt.rcParams["font.family"] = fm.FontProperties(fname=font_path).get_name()
plt.rcParams["axes.unicode_minus"] = False

# 제목
st.title("단어 빈도수 분석 웹 대시보드")

# 사이드바
st.sidebar.header("파일 선택")
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

col_name = st.sidebar.text_input("분석할 열 이름", value="review")

chart_type = st.sidebar.radio("차트 종류", ["빈도수 그래프", "워드클라우드"])

word_count = st.sidebar.slider("단어 수", min_value=5, max_value=50, value=20)

if st.sidebar.button("분석 시작"):

    if uploaded_file is None:
        st.warning("파일을 먼저 업로드해주세요!")
    else:
        # 파일 읽기
        try:
            df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
        except:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding="cp949")

        if col_name not in df.columns:
            st.error(f"'{col_name}' 열이 없습니다. 열 이름을 확인해주세요.")
            st.write("사용 가능한 열:", list(df.columns))
        else:
            # 단어 추출
            text = " ".join(df[col_name].dropna().astype(str).tolist())
            words = re.findall(r"[가-힣]{2,}", text)

            # 빈도 계산
            word_freq = Counter(words)
            top_words = word_freq.most_common(word_count)

            st.success(f"분석 완료! 총 {len(df)}개 리뷰, {len(word_freq)}개 단어")

            # 차트 그리기
            if chart_type == "빈도수 그래프":
                labels = [w for w, c in top_words][::-1]
                values = [c for w, c in top_words][::-1]

                fig, ax = plt.subplots(figsize=(8, word_count * 0.4))
                ax.barh(labels, values, color="steelblue", height=0.6)
                ax.set_xlabel("빈도수")
                ax.set_title("단어 빈도수")
                st.pyplot(fig)

            else:
                wc = WordCloud(
                    font_path=font_path,
                    background_color="white",
                    max_words=word_count,
                    width=800,
                    height=400
                ).generate_from_frequencies(dict(top_words))

                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wc)
                ax.axis("off")
                st.pyplot(fig)
