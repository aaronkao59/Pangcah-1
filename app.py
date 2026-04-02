import streamlit as st
import pandas as pd
import random
import PyPDF2
import os
import glob
import re
from PIL import Image

# --- [元數據與憲法設定] ---
st.set_page_config(page_title="Amis-Pro 族語認證衝刺", page_icon="🌊", layout="wide")

# --- [模組 A] 深度題庫解析引擎 (Integ-CRF v9.0) ---
@st.cache_data
def get_exam_bank():
    """精準掃描目錄下的 PDF，提取初級認證的單詞與句型"""
    vocab_pool = []
    oral_bank = []
    
    files = glob.glob('*.pdf')
    
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
                
                # 2. 判斷是否有看圖說話提示
                if "提示:" in full_text or "提示：" in full_text:
                    prompts = re.findall(r'提示[:：](.*?)\)', full_text)
                    oral_bank.extend(prompts)
        except:
            continue

    if not vocab_pool:
        vocab_pool = [{"word": "rengos", "source": "系統預設"}, {"word": "lotong", "source": "系統預設"}, 
                      {"word": "enem", "source": "系統預設"}, {"word": "mali", "source": "系統預設"},
                      {"word": "dafak", "source": "系統預設"}]
                      
    if not oral_bank:
        oral_bank = ["我喜歡的活動", "拜訪爺爺的一天", "我和朋友玩耍", "我的生活作息"]
    
    return pd.DataFrame(vocab_pool).drop_duplicates(), list(set(oral_bank))

# --- [模組 B] 介面視覺規範 (UIUX-CRF v10-3) ---
st.markdown("""
    <style>
    .exam-banner { background-color: #f0f7ff; border-left: 10px solid #1e40af; padding: 20px; border-radius: 5px; margin-bottom: 25px; }
    .word-card { font-family: 'Courier New', monospace; font-size: 32px; font-weight: bold; color: #1e3a8a; text-align: center; 
                 padding: 30px; border: 2px solid #e2e8f0; border-radius: 15px; background: white; transition: 0.3s; }
    .q-number { color: #64748b; font-size: 14px; margin-bottom: 5px; font-weight: bold; }
    .img-container { border: 2px dashed #cbd5e1; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

def main():
    vocab_df, oral_prompts = get_exam_bank()

    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Emblem_of_Council_of_Indigenous_Peoples.svg/200px-Emblem_of_Council_of_Indigenous_Peoples.svg.png", width=150)
    st.sidebar.title("🌊 阿美語初級認證")
    st.sidebar.markdown("---")
    app_mode = st.sidebar.radio("測驗單元切換", ["第一部分：單詞朗讀", "第二部分：簡答題", "第三部分：看圖說話"])
    
    st.sidebar.info("💡 系統已自動載入目錄下所有 PDF 與截圖題庫。")

    if app_mode == "第一部分：單詞朗讀":
        st.markdown('<div class="exam-banner"><h3>第一部分：單詞朗讀 (每題 2 分，共 10 分)</h3><p>【說明】 試卷上有 5 個族語單詞，請在準備時間 2 分鐘後，聽到「請開始回答」時，依序將單詞唸出，回答時間 1 分半鐘。</p></div>', unsafe_allow_html=True)
        
        if st.button("🔄 刷新考卷"):
            st.rerun()
            
        test_words = vocab_df.sample(n=min(5, len(vocab_df)))['word'].tolist()
        
        cols = st.columns(5)
        for i, word in enumerate(test_words):
            with cols[i]:
                st.markdown(f'<div class="q-number">1-{i+1}.</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="word-card">{word}</div>', unsafe_allow_html=True)

    elif app_mode == "第二部分：簡答題":
        st.markdown('<div class="exam-banner"><h3>第二部分：簡答題 (每題 4 分，共 20 分)</h3><p>【說明】 以下請聆聽電腦播出問題，每題播出兩遍，聽完後，再以報考方言別簡短回答。每題作答時間 15 秒。</p></div>', unsafe_allow_html=True)
        
        q_idx = st.select_slider("請選擇當前播放題號：", options=["2-1", "2-2", "2-3", "2-4", "2-5"])
        
        st.write(f"#### 🔊 {q_idx} (聽...)")
        st.progress(100, text="作答倒數：15 秒")
        
        with st.expander("👁️ 顯示參考題目與中文提示 (複習專用)"):
            st.write("**模擬題音檔內容：** Papina ko malikakaay namo? (你們有幾個兄弟姊妹？)")
            st.write("**建議句型：** `Tolo ko malikakaay niyam.` (我們有三個兄弟姊妹。)")

    elif app_mode == "第三部分：看圖說話":
        st.markdown('<div class="exam-banner"><h3>第三部分：看圖說話 (10 分)</h3><p>【說明】 請根據下面四個圖片及中文提示，選擇一個、兩個、三個或全部的圖片，以族語簡短地說說你的想法。作答時間 2 分鐘。</p></div>', unsafe_allow_html=True)
        
        # 動態抓取目錄下的圖片，模擬 2x2 考卷排版
        images = glob.glob('*.png') + glob.glob('*.jpg') + glob.glob('*.jpeg')
        
        # 若圖片不足 4 張，使用佔位符補齊
        display_imgs = images[:4] if len(images) >= 4 else images + [None] * (4 - len(images))
        
        prompt_text = random.choice(oral_prompts) if oral_prompts else "我喜歡的活動"
        st.markdown(f"#### 📌 中文提示：{prompt_text}")
        
        # 繪製 2x2 圖片矩陣 (完全仿造考卷)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="q-number">圖片 A</div>', unsafe_allow_html=True)
            if display_imgs[0]: st.image(display_imgs[0], use_column_width=True)
            else: st.info("無圖片檔案 A")
            
            st.markdown('<div class="q-number">圖片 C</div>', unsafe_allow_html=True)
            if display_imgs[2]: st.image(display_imgs[2], use_column_width=True)
            else: st.info("無圖片檔案 C")
            
        with col2:
            st.markdown('<div class="q-number">圖片 B</div>', unsafe_allow_html=True)
            if display_imgs[1]: st.image(display_imgs[1], use_column_width=True)
            else: st.info("無圖片檔案 B")
            
            st.markdown('<div class="q-number">圖片 D</div>', unsafe_allow_html=True)
            if display_imgs[3]: st.image(display_imgs[3], use_column_width=True)
            else: st.info("無圖片檔案 D")

        st.divider()
        st.text_area("✍️ 試著寫下你的族語草稿 (正式考試為口說)：", height=150, placeholder="例如：Itini i coka A, maolah kako mimali...")
        if st.button("💾 儲存練習"):
            st.success("練習已記錄！")

# --- [啟動] ---
if __name__ == "__main__":
    main()
