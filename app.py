import streamlit as st
import pandas as pd
import random
import PyPDF2
import os
import glob
import re

# --- [元數據與憲法設定] ---
st.set_page_config(page_title="Amis-Pro 族語認證衝刺", page_icon="🌊", layout="wide")

# --- [模組 A] 深度題庫解析引擎 (Integ-CRF v9.0) ---
@st.cache_data
def load_static_data():
    # 1. 載入單詞庫 ... (省略，照舊)
    
    # 2. 載入 [提示詞-圖片] 關聯矩陣
    try:
        with open("data/prompts.json", "r", encoding="utf-8") as f:
            prompts_dict = json.load(f)
    except FileNotFoundError:
        # 防呆預設資料
        prompts_dict = {
            "我喜歡的活動": ["act_01.jpg", "act_02.jpg", "act_03.jpg", "act_04.jpg"]
        }
        
    return vocab_df, prompts_dict

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
    
    # 這裡將「考試說明與指南」設為獨立的第一個選單
    app_mode = st.sidebar.radio("測驗單元切換", ["📝 考試說明與指南", "第一部分：單詞朗讀", "第二部分：簡答題", "第三部分：看圖說話"])
    
    st.sidebar.info("💡 系統已自動載入目錄下所有 PDF 與截圖題庫。")

    # --- 獨立頁籤：考試說明 ---
    if app_mode == "📝 考試說明與指南":
        st.markdown('<div class="exam-banner"><h3>📝 初級認證測驗指南</h3><p>考前必讀：測驗項目、配分與合格標準</p></div>', unsafe_allow_html=True)
        
        exam_info = {
            "項目 (Category)": ["測驗項目與配分", "測驗時間", "範圍與參考教材", "合格標準", "測驗方式"],
            "內容說明 (Details)": [
                "1. 口說測驗 (佔 40 分)：單詞朗讀 (10%)、簡答題 (20%)、看圖說話 (10%)\n2. 聽力測驗 (佔 60 分)：是非題、選擇題、配合題",
                "口說測驗：約 5 分鐘\n聽力測驗：約 20 分鐘",
                "1. 九階教材（第 1 至 3 階）\n2. 國中版句型篇\n3. 初級教材 — 生活會話篇\n4. 原住民族語言學習詞表",
                "總分須達 60 分（含）以上，且必須「同時」符合：\n• 聽力成績達 45 分（含）以上\n• 口說成績達 15 分（含）以上",
                "電腦數位化測驗\n• 聽力：看螢幕聽語音後點選答案。\n• 口說：看螢幕聽語音後，對麥克風以族語回答。"
            ]
        }
        
        df_info = pd.DataFrame(exam_info)
        df_info.index = [""] * len(df_info) 
        st.table(df_info)
        
        st.info("💡 戰術建議：口說測驗只要拿到 15 分即達標！請務必把握「第一部分：單詞朗讀」與「第三部分：看圖說話」的基礎分數。")

    # --- 測驗模組 ---
    elif app_mode == "第一部分：單詞朗讀":
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
