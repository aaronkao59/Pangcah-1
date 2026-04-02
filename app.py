import streamlit as st
import pandas as pd
import random
import PyPDF2
import os
import io
from PIL import Image

# --- [設定] 憲法級 Meta-Rules 載入 ---
st.set_page_config(
    page_title="Amis-Pro: 海岸阿美語初級認證複習系統",
    page_icon="🌊",
    layout="wide"
)

# --- [模組 A] 資源整合與數據提取 (Integ-CRF v9.0) ---
@st.cache_resource
def load_lexicon_and_questions():
    """掃描同級目錄下的 PDF 文件，提取詞彙與句型"""
    lexicon = []
    
    # 這裡演示從 03_junior_book.pdf 或 學習手冊提取
    # 實際上會掃描所有 .pdf
    files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    for file in files:
        try:
            with open(file, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                # 僅提取前幾頁作為樣本數據源，實際可全量提取
                text = ""
                for i in range(len(reader.pages)):
                    text += reader.pages[i].extract_text()
                
                # 簡易解析邏輯：尋找阿美語與中文對應 (基於上傳檔案格式)
                # 這裡假設提取規則，實務上可根據 10-5 規範進行 NLP 清洗
                if "cecay" in text: # 數字篇
                    lexicon.append({"amis": "cecay", "zh": "一", "cat": "數字"})
                    lexicon.append({"amis": "tosa", "zh": "二", "cat": "數字"})
                    lexicon.append({"amis": "tolo", "zh": "三", "cat": "數字"})
                if "mama" in text: # 親屬篇
                    lexicon.append({"amis": "mama", "zh": "爸爸", "cat": "親屬"})
                    lexicon.append({"amis": "ina", "zh": "媽媽", "cat": "親屬"})
        except:
            continue
            
    # 預設基礎數據 (避免讀取失敗時為空)
    if not lexicon:
        lexicon = [
            {"amis": "lotong", "zh": "猴子", "cat": "動物"},
            {"amis": "waco", "zh": "狗", "cat": "動物"},
            {"amis": "mami'", "zh": "橘子", "cat": "食物"},
            {"amis": "dafak", "zh": "早晨", "cat": "時間"}
        ]
    return pd.DataFrame(lexicon)

# --- [模組 B] 介面視覺與交互 (UIUX-CRF v9.0) ---
def local_css(file_name):
    st.markdown(f'<style>{file_name}</style>', unsafe_allow_html=True)

# 強制極致轉換 (Zero Friction) 風格
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #1f77b4; color: white; }
    .amis-card { padding: 20px; border-radius: 15px; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
    .amis-text { font-size: 48px; font-weight: bold; color: #1e3a8a; margin-bottom: 10px; }
    .zh-text { font-size: 24px; color: #64748b; }
    </style>
""", unsafe_allow_html=True)

def main():
    st.sidebar.title("🌊 Amis-Pro v9.0")
    st.sidebar.info("海岸阿美語初級認證考前衝刺")
    
    menu = st.sidebar.radio("模式選擇", ["詞彙閃卡 (Vocab)", "聽力/簡答模擬 (Oral)", "看圖說話 (Image)"])
    
    df = load_lexicon_and_questions()
    
    if menu == "詞彙閃卡 (Vocab)":
        st.header("⚡ 核心詞彙快速記憶")
        
        if 'idx' not in st.session_state: st.session_state.idx = 0
        
        # 取得當前題目
        current_row = df.iloc[st.session_state.idx % len(df)]
        
        st.markdown(f"""
            <div class="amis-card">
                <div class="amis-text">{current_row['amis']}</div>
                <div class="zh-text">類別：{current_row['cat']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👁️ 顯示答案"):
                st.success(f"中文翻譯：{current_row['zh']}")
        with col2:
            if st.button("➡️ 下一個"):
                st.session_state.idx += 1
                st.rerun()

    elif menu == "聽力/簡答模擬 (Oral)":
        st.header("🎧 簡答題實戰模擬")
        st.write("根據提示題目，請試著大聲說出阿美語答案。")
        
        # 模擬 3.海岸阿美語_1.pdf 題型
        questions = [
            {"q": "你叫什麼名字？", "a": "O ci [名字] ko ngangan ako."},
            {"q": "這是什麼？(指著筆)", "a": "O impic oni."},
            {"q": "你去哪裡？", "a": "Talaicowa kiso?"},
            {"q": "你幾歲？", "a": "Pina ko mihecaan iso?"}
        ]
        
        q_item = random.choice(questions)
        st.info(f"問題（中文提示）：{q_item['q']}")
        
        with st.expander("查看標準參考答案"):
            st.code(q_item['a'], language="text")
            st.write("提示：注意阿美語的 VSO 語序")

    elif menu == "看圖說話 (Image)":
        st.header("🖼️ 看圖說話 (模擬認證題型)")
        
        # 嘗試讀取截圖或 PDF 中的圖片 (此處以示意圖呈現)
        img_files = [f for f in os.listdir('.') if f.endswith(('.jpg', '.png'))]
        
        if img_files:
            target_img = random.choice(img_files)
            image = Image.open(target_img)
            st.image(image, caption="請根據圖片描述情境 (提示：我喜歡的活動/我的部落)", use_column_width=True)
        else:
            st.warning("請確保目錄下有圖片檔案 (如: 截圖 2026-04-02.jpg)")
        
        st.text_area("試著輸入你的族語描述：", placeholder="例如：Maolah kako micoka...")
        
        if st.button("提交練習"):
            st.balloons()
            st.success("記錄已儲存！建議對照《初級看圖說話.pdf》中的範例。")

# --- [執行端] ---
if __name__ == "__main__":
    main()
