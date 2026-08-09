import streamlit as st
import pandas as pd
import re

# ==========================================
# 1. 구글 스프레드시트 연동 설정
# ==========================================
# 여기에 구글 시트 [웹에 게시(CSV)] 링크를 붙여넣으십시오.
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQvHn3sGjNkCyLuvBYcC_z8qshngxNAWmqfKieDarv_3TOyzxlmrSY7B5WHwhASoTi5AA_dKAXZ5Atb/pub?output=csv"

st.set_page_config(page_title="로테이션 면접 타임테이블 조회", page_icon="🕒", layout="wide")

# 데이터를 가져오는 함수 (구글 서버 부하 방지를 위해 60초마다 새로 갱신)
@st.cache_data(ttl=60)
def load_data_from_sheet(url):
    try:
        df = pd.read_csv(url)
        # 필수 열이 잘 작성되었는지 확인
        if all(col in df.columns for col in ["학생 이름", "부여된 번호", "소속"]):
            return df.dropna(subset=["학생 이름", "부여된 번호"])
        else:
            return pd.DataFrame()
    except Exception:
        return None

# ==========================================
# 2. 타임테이블 규칙 (하드코딩 사전)
# ==========================================
TIMETABLE_DICT = {
    1: {1: "면접자(구상실)", 2: "면접자(A반 1번 면접실)", 3: "면접관(B반 3번 면접실)", 4: "면접관(B반 1번 면접실)", 5: "x (대기)"},
    2: {1: "면접자(구상실)", 2: "면접자(A반 2번 면접실)", 3: "면접관(B반 3번 면접실)", 4: "면접관(B반 1번 면접실)", 5: "x (대기)"},
    3: {1: "면접자(구상실)", 2: "면접자(A반 3번 면접실)", 3: "면접관(B반 4번 면접실)", 4: "면접관(B반 2번 면접실)", 5: "x (대기)"},
    4: {1: "면접자(구상실)", 2: "면접자(A반 4번 면접실)", 3: "면접관(B반 4번 면접실)", 4: "면접관(B반 2번 면접실)", 5: "x (대기)"},
    5: {1: "x (대기)", 2: "면접자(구상실)", 3: "면접자(A반 1번 면접실)", 4: "면접관(B반 3번 면접실)", 5: "면접관(B반 1번 면접실)"},
    6: {1: "x (대기)", 2: "면접자(구상실)", 3: "면접자(A반 2번 면접실)", 4: "면접관(B반 3번 면접실)", 5: "면접관(B반 1번 면접실)"},
    7: {1: "x (대기)", 2: "면접자(구상실)", 3: "면접자(A반 3번 면접실)", 4: "면접관(B반 4번 면접실)", 5: "면접관(B반 2번 면접실)"},
    8: {1: "x (대기)", 2: "면접자(구상실)", 3: "면접자(A반 4번 면접실)", 4: "면접관(B반 4번 면접실)", 5: "면접관(B반 2번 면접실)"},
    9: {1: "x (대기)", 2: "면접관(B반 1번 면접실)", 3: "면접자(구상실)", 4: "면접자(A반 1번 면접실)", 5: "면접관(B반 3번 면접실)"},
    10: {1: "x (대기)", 2: "면접관(B반 1번 면접실)", 3: "면접자(구상실)", 4: "면접자(A반 2번 면접실)", 5: "면접관(B반 3번 면접실)"},
    11: {1: "x (대기)", 2: "면접관(B반 2번 면접실)", 3: "면접자(구상실)", 4: "면접자(A반 3번 면접실)", 5: "면접관(B반 1번 면접실)"},
    12: {1: "x (대기)", 2: "면접관(B반 2번 면접실)", 3: "면접자(구상실)", 4: "면접자(A반 4번 면접실)", 5: "면접관(B반 2번 면접실)"},
    13: {1: "x (대기)", 2: "면접관(B반 3번 면접실)", 3: "면접관(B반 1번 면접실)", 4: "면접자(구상실)", 5: "면접자(A반 1번 면접실)"},
    14: {1: "x (대기)", 2: "면접관(B반 3번 면접실)", 3: "면접관(B반 1번 면접실)", 4: "면접자(구상실)", 5: "면접자(A반 2번 면접실)"},
    15: {1: "x (대기)", 2: "면접관(B반 4번 면접실)", 3: "면접관(B반 2번 면접실)", 4: "면접자(구상실)", 5: "면접자(A반 3번 면접실)"},
    16: {1: "x (대기)", 2: "면접관(B반 4번 면접실)", 3: "면접관(B반 2번 면접실)", 4: "면접자(구상실)", 5: "면접자(A반 4번 면접실)"},
    17: {1: "면접자(구상실)", 2: "면접자(B반 1번 면접실)", 3: "면접관(A반 3번 면접실)", 4: "면접관(A반 1번 면접실)", 5: "x (대기)"},
    18: {1: "면접자(구상실)", 2: "면접자(B반 2번 면접실)", 3: "면접관(A반 3번 면접실)", 4: "면접관(A반 1번 면접실)", 5: "x (대기)"},
    19: {1: "면접자(구상실)", 2: "면접자(B반 3번 면접실)", 3: "면접관(A반 4번 면접실)", 4: "면접관(A반 2번 면접실)", 5: "x (대기)"},
    20: {1: "면접자(구상실)", 2: "면접자(B반 4번 면접실)", 3: "면접관(A반 4번 면접실)", 4: "면접관(A반 2번 면접실)", 5: "x (대기)"},
    21: {1: "x (대기)", 2: "면접자(구상실)", 3: "면접자(B반 1번 면접실)", 4: "면접관(A반 3번 면접실)", 5: "면접관(A반 1번 면접실)"},
    22: {1: "x (대기)", 2: "면접자(구상실)", 3: "면접자(B반 2번 면접실)", 4: "면접관(A반 3번 면접실)", 5: "면접관(A반 1번 면접실)"},
    23: {1: "x (대기)", 2: "면접자(구상실)", 3: "면접자(B반 3번 면접실)", 4: "면접관(A반 4번 면접실)", 5: "면접관(A반 2번 면접실)"},
    24: {1: "x (대기)", 2: "면접자(구상실)", 3: "면접자(B반 4번 면접실)", 4: "면접관(A반 4번 면접실)", 5: "면접관(A반 2번 면접실)"},
    25: {1: "x (대기)", 2: "면접관(A반 1번 면접실)", 3: "면접자(구상실)", 4: "면접자(B반 1번 면접실)", 5: "면접관(A반 3번 면접실)"},
    26: {1: "x (대기)", 2: "면접관(A반 1번 면접실)", 3: "면접자(구상실)", 4: "면접자(B반 2번 면접실)", 5: "면접관(A반 3번 면접실)"},
    27: {1: "x (대기)", 2: "면접관(A반 2번 면접실)", 3: "면접자(구상실)", 4: "면접자(B반 3번 면접실)", 5: "면접관(A반 4번 면접실)"},
    28: {1: "x (대기)", 2: "면접관(A반 2번 면접실)", 3: "면접자(구상실)", 4: "면접자(B반 4번 면접실)", 5: "면접관(A반 4번 면접실)"},
    29: {1: "x (대기)", 2: "면접관(A반 3번 면접실)", 3: "면접관(A반 1번 면접실)", 4: "면접자(구상실)", 5: "면접자(B반 1번 면접실)"},
    30: {1: "x (대기)", 2: "면접관(A반 3번 면접실)", 3: "면접관(A반 1번 면접실)", 4: "면접자(구상실)", 5: "면접자(B반 2번 면접실)"},
    31: {1: "x (대기)", 2: "면접관(A반 4번 면접실)", 3: "면접관(A반 2번 면접실)", 4: "면접자(구상실)", 5: "면접자(B반 3번 면접실)"}
}

# ==========================================
# 3. HTML 타임테이블 생성 함수
# ==========================================
def get_html_table(highlight_num=None):
    raw_table = [
        ["00:05~00:25", "1, 2<br>3, 4", "", "", "17, 18<br>19, 20", "", ""],
        ["00:25~00:45", "5, 6<br>7, 8", "1 / 2<br>3 / 4", "(25,26) / (27,28)<br>(29,30) / (31)", "21, 22<br>23, 24", "17 / 18<br>19 / 20", "(9,10) / (11,12)<br>(13,14) / (15,16)"],
        ["00:45~01:05", "9, 10<br>11, 12", "5 / 6<br>7 / 8", "(29,30) / (31)<br>(17,18) / (19,20)", "25, 26<br>27, 28", "21 / 22<br>23 / 24", "(13,14) / (15,16)<br>(1,2) / (3,4)"],
        ["01:05~01:25", "13, 14<br>15, 16", "9 / 10<br>11 / 12", "(17,18) / (19,20)<br>(21,22) / (23,24)", "29, 30<br>31", "25 / 26<br>27 / 28", "(1,2) / (3,4)<br>(5,6) / (7,8)"],
        ["01:25~01:45", "", "13 / 14<br>15 / 16", "(21,22) / (23,24)<br>(25,26) / (27,28)", "", "29 / 30<br>31", "(5,6,11) / (7,8,12)<br>(9,10)"]
    ]

    html = """
    <style>
        .timetable { width: 100%; border-collapse: collapse; text-align: center; font-family: 'Malgun Gothic', sans-serif; margin-top: 15px; }
        .timetable th { background-color: #2b3a55; color: white; border: 1px solid #d3d3d3; padding: 10px; font-size: 14px; }
        .timetable td { border: 1px solid #d3d3d3; padding: 12px 5px; vertical-align: middle; font-size: 14px; color: #333; }
        .timetable tr:nth-child(even) { background-color: #f9f9f9; }
        .highlight { background-color: #ffeb3b; font-weight: 900; color: #d32f2f; padding: 3px 6px; border-radius: 4px; box-shadow: 0 0 5px rgba(255,235,59,0.8); font-size: 1.1em; }
    </style>
    <table class="timetable">
        <tr>
            <th>수업시작후</th>
            <th>A반 구상</th>
            <th>A반 면접</th>
            <th>B반 면접관</th>
            <th>B반 구상</th>
            <th>B반 면접</th>
            <th>A반 면접관</th>
        </tr>
    """
    for row in raw_table:
        html += "<tr>"
        for i, cell in enumerate(row):
            if highlight_num and i > 0 and cell:
                cell = re.sub(rf'\b({highlight_num})\b', r'<span class="highlight">\1</span>', cell)
            html += f"<td>{cell}</td>"
        html += "</tr>"
    html += "</table>"
    return html


# ==========================================
# 4. 화면 렌더링 (오직 학생 조회 화면만 존재)
# ==========================================
st.title("🕒 나의 로테이션 시간표 조회")

# 시트 데이터 불러오기
df = load_data_from_sheet(SHEET_CSV_URL)

if df is None:
    st.error("오류: 구글 스프레드시트 링크를 다시 확인해 주십시오. '웹에 게시'가 정상적으로 이루어지지 않았습니다.")
elif df.empty:
    st.warning("아직 선생님께서 명단과 번호를 입력하지 않으셨습니다. 잠시 후 다시 확인해 주십시오.")
else:
    # 학생 이름 목록 추출 (오름차순 정렬)
    student_list = sorted(df["학생 이름"].astype(str).tolist())
    selected_name = st.selectbox("자신의 이름을 선택해 주십시오.", ["-- 선택 --"] + student_list)
    
    if selected_name != "-- 선택 --":
        # 선택한 학생의 정보 추출
        student_info = df[df["학생 이름"] == selected_name].iloc[0]
        try:
            my_num = int(student_info["부여된 번호"])
            my_class = str(student_info["소속"]).strip()
        except ValueError:
            st.error("선생님께서 입력하신 번호에 문자가 포함되어 있습니다. 구글 시트를 확인해 주십시오.")
            st.stop()
            
        st.success(f"반갑습니다, **{selected_name}**님! 부여받은 번호는 **{my_class} {my_num}번** 입니다.")
        
        # 타임별 역할 카드 뷰
        st.subheader("📋 타임별 역할 안내")
        roles = TIMETABLE_DICT.get(my_num, {})
        
        if not roles:
            st.error("입력된 번호가 1~31번 사이가 아닙니다. 선생님께 확인을 요청하십시오.")
        else:
            cols = st.columns(5)
            for time_idx in range(1, 6):
                role = roles.get(time_idx, "오류")
                with cols[time_idx-1]:
                    st.markdown(
                        f"""
                        <div style="background-color: {'#e8f5e9' if '면접' in role or '구상' in role else '#f5f5f5'}; 
                                    padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #ddd; height: 100px; display: flex; flex-direction: column; justify-content: center;">
                            <div style="font-size: 13px; color: #666; font-weight: bold; margin-bottom: 5px;">{time_idx}타임</div>
                            <div style="font-size: 15px; color: {'#2e7d32' if '면접' in role or '구상' in role else '#999'}; font-weight: bold;">{role}</div>
                        </div>
                        """, unsafe_allow_html=True
                    )
            
            # 전체 시간표 내 위치 강조 표시
            st.markdown("---")
            st.subheader("📍 전체 시간표 내 동선 확인")
            st.markdown("전체 일정표에서 본인의 번호가 **노란색**으로 강조되어 표시됩니다.")
            highlighted_table = get_html_table(highlight_num=my_num)
            st.markdown(highlighted_table, unsafe_allow_html=True)