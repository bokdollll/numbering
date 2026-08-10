import streamlit as st
import pandas as pd
import re

# ==========================================
# 1. 구글 스프레드시트 연동 설정
# ==========================================
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQvHn3sGjNkCyLuvBYcC_z8qshngxNAWmqfKieDarv_3TOyzxlmrSY7B5WHwhASoTi5AA_dKAXZ5Atb/pub?output=csv"

st.set_page_config(page_title="로테이션 면접 타임테이블 및 배치도", page_icon="🏫", layout="wide")

@st.cache_data(ttl=60)
def load_data_from_sheet(url):
    try:
        df = pd.read_csv(url)
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
# 3. HTML 타임테이블 & 면접실 배치도 생성 함수
# ==========================================
def get_html_table(highlight_num=None):
    raw_table = [
        ["1타임<br>(13:40~14:00)", "1, 2<br>3, 4", "", "", "17, 18<br>19, 20", "", ""],
        ["2타임<br>(14:00~14:20)", "5, 6<br>7, 8", "1 / 2<br>3 / 4", "(25,26) / (27,28)<br>(29,30) / (31)", "21, 22<br>23, 24", "17 / 18<br>19 / 20", "(9,10) / (11,12)<br>(13,14) / (15,16)"],
        ["3타임<br>(14:20~14:40)", "9, 10<br>11, 12", "5 / 6<br>7 / 8", "(29,30) / (31)<br>(17,18) / (19,20)", "25, 26<br>27, 28", "21 / 22<br>23 / 24", "(13,14) / (15,16)<br>(1,2) / (3,4)"],
        ["4타임<br>(14:40~15:00)", "13, 14<br>15, 16", "9 / 10<br>11 / 12", "(17,18) / (19,20)<br>(21,22) / (23,24)", "29, 30<br>31", "25 / 26<br>27 / 28", "(1,2) / (3,4)<br>(5,6) / (7,8)"],
        ["5타임<br>(15:00~15:20)", "", "13 / 14<br>15 / 16", "(21,22) / (23,24)<br>(25,26) / (27,28)", "", "29 / 30<br>31", "(5,6,11) / (7,8,12)<br>(9,10)"]
    ]

    html = """
    <style>
        .timetable { width: 100%; border-collapse: collapse; text-align: center; font-family: 'Malgun Gothic', sans-serif; margin-top: 15px; }
        .timetable th { background-color: #2b3a55; color: white; border: 1px solid #d3d3d3; padding: 10px; font-size: 14px; }
        .timetable td { border: 1px solid #d3d3d3; padding: 12px 5px; vertical-align: middle; font-size: 14px; color: #333; }
        .timetable tr:nth-child(even) { background-color: #f9f9f9; }
        .hl { background-color: #ffeb3b; font-weight: 900; color: #d32f2f; padding: 2px 5px; border-radius: 4px; border: 1px solid #f57f17; }
    </style>
    <table class="timetable">
        <tr><th>타임 (시간)</th><th>A반 구상</th><th>A반 면접</th><th>B반 면접관</th><th>B반 구상</th><th>B반 면접</th><th>A반 면접관</th></tr>
    """
    for row in raw_table:
        html += "<tr>"
        for i, cell in enumerate(row):
            if highlight_num and i > 0 and cell:
                cell = re.sub(rf'\b({highlight_num})\b', r'<span class="hl">\1</span>', cell)
            html += f"<td>{cell}</td>"
        html += "</tr>"
    html += "</table>"
    return html

def get_room_map_html(highlight_num=None, time_filter="전체"):
    # 1) 전체 타임통합 데이터
    rooms_all = {
        "A반 1번": [("25,29<br>17,21", "top-left"), ("26,30<br>18,22", "top-right"), ("1,5,<br>9,13", "bottom-mid")],
        "A반 2번": [("27,31<br>19,23", "top-left"), ("28,()<br>20,24", "top-right"), ("2,6,<br>10,14", "bottom-mid")],
        "A반 3번": [("3,7,<br>11,15", "top-mid"), ("29,17,<br>21,25", "bottom-left"), ("30,18,<br>22,26", "bottom-right")],
        "A반 4번": [("4,8,<br>12,16", "top-mid"), ("31,19,<br>23,27", "bottom-left"), ("(),20,<br>24,28", "bottom-right")],
        "B반 1번": [("9,13,<br>1,(5,11)", "top-left"), ("10,14,<br>2,6", "top-right"), ("17,21,<br>25,29", "bottom-mid")],
        "B반 2번": [("11,15,<br>3,(7,12)", "top-left"), ("12,16,<br>4,8", "top-right"), ("18,22,<br>26,30", "bottom-mid")],
        "B반 3번": [("19,23,<br>27,31", "top-mid"), ("13,1,<br>5,9", "bottom-left"), ("14,2,<br>6,10", "bottom-right")],
        "B반 4번": [("20,24,<br>28", "top-mid"), ("15,3,<br>7", "bottom-left"), ("16,4,<br>8", "bottom-right")]
    }

    # 2) 각 타임별 전용 데이터 (2~5타임)
    rooms_by_time = {
        "2타임": {
            "A반 1번": [("25", "top-left"), ("26", "top-right"), ("1", "bottom-mid")],
            "A반 2번": [("27", "top-left"), ("28", "top-right"), ("2", "bottom-mid")],
            "A반 3번": [("3", "top-mid"), ("29", "bottom-left"), ("30", "bottom-right")],
            "A반 4번": [("4", "top-mid"), ("31", "bottom-left"), ("-", "bottom-right")],
            "B반 1번": [("9", "top-left"), ("10", "top-right"), ("17", "bottom-mid")],
            "B반 2번": [("11", "top-left"), ("12", "top-right"), ("18", "bottom-mid")],
            "B반 3번": [("19", "top-mid"), ("13", "bottom-left"), ("14", "bottom-right")],
            "B반 4번": [("20", "top-mid"), ("15", "bottom-left"), ("16", "bottom-right")]
        },
        "3타임": {
            "A반 1번": [("29", "top-left"), ("30", "top-right"), ("5", "bottom-mid")],
            "A반 2번": [("31", "top-left"), ("-", "top-right"), ("6", "bottom-mid")],
            "A반 3번": [("7", "top-mid"), ("17", "bottom-left"), ("18", "bottom-right")],
            "A반 4번": [("8", "top-mid"), ("19", "bottom-left"), ("20", "bottom-right")],
            "B반 1번": [("13", "top-left"), ("14", "top-right"), ("21", "bottom-mid")],
            "B반 2번": [("15", "top-left"), ("16", "top-right"), ("22", "bottom-mid")],
            "B반 3번": [("23", "top-mid"), ("1", "bottom-left"), ("2", "bottom-right")],
            "B반 4번": [("24", "top-mid"), ("3", "bottom-left"), ("4", "bottom-right")]
        },
        "4타임": {
            "A반 1번": [("17", "top-left"), ("18", "top-right"), ("9", "bottom-mid")],
            "A반 2번": [("19", "top-left"), ("20", "top-right"), ("10", "bottom-mid")],
            "A반 3번": [("11", "top-mid"), ("21", "bottom-left"), ("22", "bottom-right")],
            "A반 4번": [("12", "top-mid"), ("23", "bottom-left"), ("24", "bottom-right")],
            "B반 1번": [("1", "top-left"), ("2", "top-right"), ("25", "bottom-mid")],
            "B반 2번": [("3", "top-left"), ("4", "top-right"), ("26", "bottom-mid")],
            "B반 3번": [("27", "top-mid"), ("5", "bottom-left"), ("6", "bottom-right")],
            "B반 4번": [("28", "top-mid"), ("7", "bottom-left"), ("8", "bottom-right")]
        },
        "5타임": {
            "A반 1번": [("21", "top-left"), ("22", "top-right"), ("13", "bottom-mid")],
            "A반 2번": [("23", "top-left"), ("24", "top-right"), ("14", "bottom-mid")],
            "A반 3번": [("15", "top-mid"), ("25", "bottom-left"), ("26", "bottom-right")],
            "A반 4번": [("16", "top-mid"), ("27", "bottom-left"), ("28", "bottom-right")],
            "B반 1번": [("5, 11", "top-left"), ("6", "top-right"), ("29", "bottom-mid")],
            "B반 2번": [("7, 12", "top-left"), ("8", "top-right"), ("30", "bottom-mid")],
            "B반 3번": [("31", "top-mid"), ("9", "bottom-left"), ("10", "bottom-right")],
            "B반 4번": [("-", "top-mid"), ("-", "bottom-left"), ("-", "bottom-right")]
        }
    }

    rooms_data = rooms_by_time.get(time_filter, rooms_all)

    def render_block(text):
        if highlight_num and text and text != "-":
            text = re.sub(rf'\b({highlight_num})\b', r'<span class="hl">\1</span>', text)
        return text

    html = """
    <style>
        .map-container { display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; margin-top: 15px; }
        .room-section { flex: 1; min-width: 340px; background: #fafafa; padding: 15px; border-radius: 10px; border: 1px solid #ccc; padding-bottom: 50px; }
        .section-title { text-align: center; font-weight: bold; font-size: 16px; margin-bottom: 20px; color: #1a237e; }
        .grid-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 20px 15px; }
        .room-box { border: 2px solid #333; height: 160px; position: relative; background: #fff; border-radius: 6px; }
        .room-left { transform: translateY(0px); }
        .room-right { transform: translateY(35px); }
        .room-label { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-weight: bold; font-size: 16px; color: #555; }
        .seat { position: absolute; border: 1px solid #999; padding: 4px; font-size: 13px; text-align: center; background: #f0f0f0; border-radius: 4px; min-width: 60px; }
        .pos-top-left { top: 6px; left: 6px; }
        .pos-top-right { top: 6px; right: 6px; }
        .pos-top-mid { top: 6px; left: 50%; transform: translateX(-50%); }
        .pos-bottom-mid { bottom: 6px; left: 50%; transform: translateX(-50%); }
        .pos-bottom-left { bottom: 6px; left: 6px; }
        .pos-bottom-right { bottom: 6px; right: 6px; }
    </style>
    <div class="map-container">
        <!-- 1. B반 면접실 배치도 (좌측 배치) -->
        <div class="room-section">
            <div class="section-title">🅱️ B반 면접실 배치도 (2학년)</div>
            <div class="grid-layout">
    """
    
    b_rooms = ["B반 1번", "B반 2번", "B반 3번", "B반 4번"]
    for idx, name in enumerate(b_rooms):
        seats = rooms_data[name]
        pos_class = "room-left" if idx % 2 == 0 else "room-right"
        html += f'<div class="room-box {pos_class}"><div class="room-label">{name[3:]}</div>'
        for text, pos in seats:
            html += f'<div class="seat pos-{pos}">{render_block(text)}</div>'
        html += '</div>'
        
    html += """
            </div>
        </div>
        <!-- 2. A반 면접실 배치도 (우측 배치) -->
        <div class="room-section">
            <div class="section-title">🅰️ A반 면접실 배치도 (1학년)</div>
            <div class="grid-layout">
    """
    
    a_rooms = ["A반 1번", "A반 2번", "A반 3번", "A반 4번"]
    for idx, name in enumerate(a_rooms):
        seats = rooms_data[name]
        pos_class = "room-left" if idx % 2 == 0 else "room-right"
        html += f'<div class="room-box {pos_class}"><div class="room-label">{name[3:]}</div>'
        for text, pos in seats:
            html += f'<div class="seat pos-{pos}">{render_block(text)}</div>'
        html += '</div>'
        
    html += '</div></div></div>'
    return html

# ==========================================
# 4. 화면 렌더링
# ==========================================
st.title("🕒 나의 로테이션 시간표 및 면접실 배치도")

df = load_data_from_sheet(SHEET_CSV_URL)

if df is None:
    st.error("오류: 구글 스프레드시트 링크를 다시 확인해 주십시오.")
elif df.empty:
    st.warning("아직 선생님께서 명단과 번호를 입력하지 않으셨습니다.")
else:
    student_list = sorted(df["학생 이름"].astype(str).tolist())
    selected_name = st.selectbox("자신의 이름을 선택해 주십시오.", ["-- 선택 --"] + student_list)
    
    if selected_name != "-- 선택 --":
        student_info = df[df["학생 이름"] == selected_name].iloc[0]
        try:
            my_num = int(student_info["부여된 번호"])
            my_class = str(student_info["소속"]).strip()
        except ValueError:
            st.error("숫자 번호 오류가 발생했습니다. 구글 시트를 확인해 주십시오.")
            st.stop()
            
        st.success(f"반갑습니다, **{selected_name}**님! 부여받은 번호는 **{my_class} {my_num}번** 입니다.")
        
        # 1) 타임별 역할
        st.subheader("📋 타임별 역할 안내")
        roles = TIMETABLE_DICT.get(my_num, {})
        
        if roles:
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
            
            # 2) 타임테이블 위치
            st.markdown("---")
            st.subheader("📍 1. 전체 시간표 내 동선 확인")
            st.markdown(get_html_table(highlight_num=my_num), unsafe_allow_html=True)
            
            # 3) 면접실 배치도 위치 (타임 필터 추가)
            st.markdown("---")
            st.subheader("🗺️ 2. 면접실 내 좌석 위치 확인")
            
            time_filter = st.radio(
                "조회할 타임을 선택하십시오:",
                ["전체", "2타임", "3타임", "4타임", "5타임"],
                horizontal=True
            )
            
            st.markdown("아래 면접실 배치도에서 본인의 번호가 **노란색**으로 표시됩니다.")
            st.markdown(get_room_map_html(highlight_num=my_num, time_filter=time_filter), unsafe_allow_html=True)
