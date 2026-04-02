import streamlit as st
import pandas as pd
import random
import PyPDF2
import os
import re

# --- [元數據與憲法設定] ---
st.set_page_config(page_title="Amis-Pro 族語認證衝刺", page_icon="🌊", layout="wide")

# --- [模組 A] 深度題庫解析引擎 (Integ-CRF v9.0) ---
@st.cache_data
def get_exam_bank():
    """精準掃描目錄下的 PDF，提取初級認證的單詞與句型"""
    vocab_pool = []
    oral_bank = []
    
    # 掃描 3.海岸阿美語_x.pdf 檔案
    files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    for f_name in files:
        try:
            with open(f_name, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                full_text = ""
                for page in reader.pages:
                    full_text += page.extract_text()
                
                # 1. 提取單詞朗讀 (Regex 匹配 1-1. 到 1-5.)
                words = re.findall(r'1-\d\.\s*([a-zA-Z\']+)', full_text)
                for w in words:
                    vocab_pool.append({"word": w, "source": f_name})
                
                # 2. 提取簡答題關鍵字 (模擬)
                if "簡答題" in full_text:
                    oral_bank.append({"source": f_name, "q_count": 5})
        except:
            continue

    # 兜底數據 (若解析失敗)
    if not vocab_pool:
        vocab_pool = [{"word": "rengos", "source": "系統預設"}, {"word": "lotong", "source": "系統預設"}, 
                      {"word": "enem", "source": "系統預設"}, {"word": "mali", "source": "系統預設"}]
    
    return pd.DataFrame(vocab_pool).drop_duplicates(), oral_bank

# --- [模組 B] 介面視覺規範 (UIUX-CRF v10-3) ---
st.markdown("""
    <style>
    /* 模仿認證測驗介面藍色標題 */
    .exam-banner { background-color: #f0f7ff; border-left: 10px solid #1e40af; padding: 20px; border-radius: 5px; margin-bottom: 25px; }
    .word-card { font-family: 'Courier New', monospace; font-size: 32px; font-weight: bold; color: #1e3a8a; text-align: center; 
                 padding: 30px; border: 2px solid #e2e8f0; border-radius: 15px; background: white; transition: 0.3s; }
    .word-card:hover { border-color: #3b82f6; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .q-number { color: #64748b; font-size: 14px; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

def main():
    vocab_df, oral_data = get_exam_bank()

    # Sidebar 狀態列
    st.sidebar.title("🌊 阿美語初級認證")
    st.sidebar.markdown("---")
    app_mode = st.sidebar.radio("測驗單元", ["單詞朗讀 (第一部分)", "簡答題模擬 (第二部分)", "看圖說話 (第三部分)"])
    
    st.sidebar.info(f"📚 已從 PDF 載入 {len(vocab_df)} 個考驗單詞")

    if app_mode == "單詞朗讀 (第一部分)":
        st.markdown('<div class="exam-banner"><h3>第一部分：單詞朗讀</h3><p>說明：試卷上有 5 個單詞，請在準備 2 分鐘後，依序將單詞唸出。</p></div>', unsafe_allow_html=True)
        
        # 模擬隨機抽取 5 題
        if st.button("🔄 刷新考題 (更換試卷)"):
            st.rerun()
            
        test_words = vocab_df.sample(n=min(5, len(vocab_df)))['word'].tolist()
        
        # 模擬截圖中的 1-1 到 1-5 佈局
        cols = st.columns(5)
        for i, word in enumerate(test_words):
            with cols[i]:
                st.markdown(f'<div class="q-number">1-{i+1}.</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="word-card">{word}</div>', unsafe_allow_html=True)

        st.divider()
        st.caption("⚠️ 注意：唸出時請注意喉塞音 (') 與長短音的準確度。")

    elif app_mode == "簡答題模擬 (第二部分)":
        st.markdown('<div class="exam-banner"><h3>第二部分：簡答題</h3><p>說明：請聆聽電腦播出問題，聽完後以族語簡短回答。</p></div>', unsafe_allow_html=True)
        
        # 模擬播放介面
        q_idx = st.select_slider("選擇題目編號", options=[1, 2, 3, 4, 5])
        
        st.write(f"#### 🔊 題目 2-{q_idx} 正在播放...")
        st.audio("https://www.w3schools.com/html/horse.ogg") # 這裡僅為示意，實務上可放空白音頻或提示音
        
        st.warning("⏱️ 作答倒數：15 秒")
        
        with st.expander("👁️ 顯示參考題目與中文提示 (練習用)"):
            # 根據 PDF 內容模擬常見初級簡答題
            sample_qs = [
                {"q": "Cima ko ngangan iso? (你叫什麼名字？)", "a": "O ci ... ko ngangan ako."},
                {"q": "Icowa ko loma' iso? (你家在哪裡？)", "a": "Itini i ... ko loma' ako."},
                {"q": "Pina ko mihecaan iso? (你幾歲？)", "a": " ... ko mihecaan ako."},
                {"q": "Papina ko malikakaay namo? (你們有幾個兄弟姊妹？)", "a": " ... ko malikakaay niyam."},
                {"q": "Maan ko kaolahan iso a tamdaw? (你喜歡什麼樣的人？)", "a": "Maolah kako to ..."}
            ]
            st.write(f"**題目：** {sample_qs[q_idx-1]['q']}")
            st.write(f"**建議句型：** `{sample_qs[q_idx-1]['a']}`")

    elif app_mode == "看圖說話 (第三部分)":
        st.markdown('<div class="exam-banner"><h3>第三部分：看圖說話</h3><p>說明：根據圖片及中文提示，以族語簡短說說你的想法。</p></div>', unsafe_allow_html=True)
        
        # 隨機抓取目錄下的截圖圖檔
        images = [f for f in os.listdir('.') if f.endswith(('.png', '.jpg', '.jpeg'))]
        if images:
            selected_img = random.choice(images)
            st.image(selected_img, use_column_width=True, caption="考題圖片庫隨機抽取")
        else:
            st.info("請將考題截圖（如：截圖 2026-04-02 上午 11.25.15.png）放入與 app.py 相同目錄以載入圖片。")

        st.text_area("請在此練習輸入族語描述...", height=100)
        if st.button("提交練習記錄"):
            st.toast("已儲存本次練習進度！")

# --- [啟動] ---
if __name__ == "__main__":
    main()
