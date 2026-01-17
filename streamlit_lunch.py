import streamlit as st
import pandas as pd
import os, json
import random

# --- 상수 정의 ---
RESTAURANT_DB_FILE = "restaurant_db.csv"
REQUIRED_COLUMNS = {
    "맛집": "", "메뉴": "", "거리": "", "네이버지도링크": "", "대표사진": "", "득표수": 0
}
INITIAL_DATA = {
    "맛집": ["성수족발 본점", "꿉당 성수점", "소문난성수감자탕"],
    "메뉴": ["족발", "꿉당 목살, K-목살", "감자탕"],
    "거리": ["500m", "400m", "600m"],
    "네이버지도링크": [
        "https://naver.me/GvctmbhI",
        "https://naver.me/54PqGPbE",
        "https://naver.me/F1Yv1tON"
    ],
    "대표사진": [
        "https://search.pstatic.net/common/?autoRotate=true&quality=95&type=w750&src=https://ldb-phinf.pstatic.net/20200824_105/1598237583093cbAkg_JPEG/7V5I-S2mXv_p8a2v_bnI40sE.jpg",
        "https://search.pstatic.net/common/?autoRotate=true&quality=95&type=w750&src=https://ldb-phinf.pstatic.net/20240125_205/1706173019183qfT0M_JPEG/20240123_180436.jpg",
        "https://search.pstatic.net/common/?autoRotate=true&quality=95&type=w750&src=https://ldb-phinf.pstatic.net/20231116_13/1700120257904s6bAj_JPEG/KakaoTalk_20231116_163618429.jpg"
    ],
    "득표수": [10, 5, 15]
}

# --- 함수 정의 ---

def load_data(file_path):
    """데이터를 로드하고, 파일이 없거나 컬럼이 누락된 경우 초기화합니다."""
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        missing_cols = set(REQUIRED_COLUMNS.keys()) - set(df.columns)
        if missing_cols:
            st.warning(f"DB 파일에 다음 열이 없어 추가합니다: {', '.join(missing_cols)}")
            for col in missing_cols:
                df[col] = REQUIRED_COLUMNS[col]
            df = df[list(REQUIRED_COLUMNS.keys())]
            save_data(df, file_path)
    else:
        st.info("맛집 데이터 파일이 없어 샘플 데이터로 새로 생성합니다.")
        df = pd.DataFrame(INITIAL_DATA)
        save_data(df, file_path)
    
    df['득표수'] = pd.to_numeric(df['득표수'], errors='coerce').fillna(0).astype(int)
    return df

def save_data(df, file_path):
    """데이터프레임을 CSV 파일로 저장합니다."""
    df.to_csv(file_path, index=False)

# --- 페이지 설정 ---
st.set_page_config(page_title="점심 메뉴 맛집 투표", page_icon="🍴", layout="wide")

# --- 사이드바 ---
st.sidebar.title("메뉴")
page = st.sidebar.radio("페이지를 선택하세요:", ("오늘의 점심 메뉴", "맛집 데이터 관리"))

# --- 데이터 로드 ---
df = load_data(RESTAURANT_DB_FILE)

# --- "오늘의 점심 메뉴" 페이지 ---
if page == "오늘의 점심 메뉴":
    st.title("🍴 오늘 점심 뭐 먹지?")
    st.write("마음에 드는 맛집에 투표하거나, 새로운 맛집을 추천 받아보세요!")

    if st.button("🔄 랜덤 맛집 추천받기"):
        if not df.empty:
            random_restaurant = df.sample(1).iloc[0]
            st.success(f"**오늘의 랜덤 추천 맛집: {random_restaurant['맛집']}**")
            col1, col2 = st.columns([1, 2])
            with col1:
                if pd.notna(random_restaurant['대표사진']) and random_restaurant['대표사진']:
                    st.image(random_restaurant['대표사진'], use_column_width=True)
            with col2:
                st.markdown(f"### {random_restaurant['맛집']}")
                st.markdown(f"**메뉴:** {random_restaurant['메뉴']}")
                st.markdown(f"**거리:** {random_restaurant['거리']}")
                st.markdown(f"[네이버 지도로 보기]({random_restaurant['네이버지도링크']})")
        else:
            st.warning("맛집 데이터가 비어있습니다. 관리자 페이지에서 맛집을 추가해주세요.")

    st.divider()
    st.subheader("⭐ 오늘의 추천 맛집")
    
    if not df.empty:
        num_recommendations = st.slider("보여줄 맛집 개수를 선택하세요:", 1, min(5, len(df)), 3)
        recommended_restaurants = df.sort_values(by="득표수", ascending=False).head(num_recommendations)

        for i in range(0, len(recommended_restaurants), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(recommended_restaurants):
                    restaurant = recommended_restaurants.iloc[i+j]
                    with cols[j]:
                        with st.container(border=True):
                            if pd.notna(restaurant['대표사진']) and restaurant['대표사진']:
                                st.image(restaurant['대표사진'], use_column_width=True)
                            st.markdown(f"#### {restaurant['맛집']}")
                            st.markdown(f"**{restaurant['메뉴']}** ({restaurant['거리']})")
                            
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                if st.button(f"❤️ 투표하기", key=f"vote_{restaurant['맛집']}"):
                                    df.loc[df['맛집'] == restaurant['맛집'], '득표수'] += 1
                                    save_data(df, RESTAURANT_DB_FILE)
                                    st.success(f"'{restaurant['맛집']}'에 투표 완료!")
                                    st.balloons()
                                    st.rerun()
                            with col2:
                                st.link_button("📍 지도로 보기", restaurant['네이버지도링크'])
    else:
        st.warning("맛집 데이터가 비어있습니다. 관리자 페이지에서 맛집을 추가해주세요.")

    st.divider()
    st.subheader("📊 현재 투표 결과")
    if not df.empty and '맛집' in df.columns:
        st.bar_chart(df.set_index('맛집')['득표수'])
        st.table(df[['맛집', '득표수']].sort_values(by="득표수", ascending=False))

# --- "맛집 데이터 관리" 페이지 ---
elif page == "맛집 데이터 관리":
    st.title("🔐 맛집 데이터 관리")
    st.info("여기에 Notion 이미지 링크와 같은 **직접적인 이미지 URL**을 `대표사진` 컬럼에 붙여넣어 주세요. 네이버 지도 URL은 `네이버지도링크` 컬럼에 넣어주세요.")

    password = st.text_input("관리자 비밀번호를 입력하세요:", type="password")
    
    if password == "admin": 
        st.success("관리자 인증 완료!")
        st.subheader("맛집 목록 편집")
        
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "대표사진": st.column_config.ImageColumn("대표 사진", help="맛집의 대표 사진 URL을 여기에 입력하세요. 입력 후 다른 셀을 클릭하면 미리보기가 나타납니다."),
                "네이버지도링크": st.column_config.LinkColumn("네이버 지도 링크", help="네이버 지도 URL")
            }
        )

        if st.button("변경사항 저장"):
            save_data(edited_df, RESTAURANT_DB_FILE)
            st.success("데이터베이스 저장이 완료되었습니다.")
            st.rerun()

    elif password:
        st.error("비밀번호가 틀렸습니다.")