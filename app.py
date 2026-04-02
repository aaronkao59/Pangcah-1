import streamlit as st
import pandas as pd
import random
import os

# --- [元數據與效能設定] ---
st.set_page_config(page_title="Amis-Pro 族語認證衝刺", page_icon="🌊", layout="wide")

# --- [模組 A] 極速資料載入引擎 (內建單音節過濾與防呆機制) ---
@st.cache_data
def load_static_data():
    # 1. 載入單詞庫並處理潛在的讀取錯誤
    try:
        vocab_df = pd.read_csv("data/vocab.csv")
        if 'word' not in vocab_df.columns:
            vocab_df = pd.DataFrame([{"word": "rengos"}, {"word": "lotong"}, {"word": "enem"}])
        vocab_df = vocab_df.dropna(subset=['word']) # 清除空值
    except (FileNotFoundError, pd.errors.EmptyDataError):
        vocab_df = pd.DataFrame([
            {"word": "rengos"}, {"word": "lotong"}, {"word": "enem"}, 
            {"word": "mali"}, {"word": "dafak"}, {"word": "mami'"}, {"word": "posi"}
        ])

    # 2. 【核心條件追加】單音節過濾器
    def is_multi_syllable(word):
        # 定義阿美語母音
        vowels = set("aeiouAEIOU")
        # 計算單字中的母音數量 (代表音節數)
        vowel_count = sum(1 for char in str(word) if char in vowels)
        # 嚴禁單音節：母音數量必須大於 1
        return vowel_count > 1

    # 套用過濾器，剔除單音節字
    vocab_df['is_valid'] = vocab_df['word'].apply(is_multi_syllable)
    valid_vocab_df = vocab_df[vocab_df['is_valid'] == True]

    # 防呆：如果過濾後題庫被清空了，強行注入合法預設值
    if valid_vocab_df.empty:
        valid_vocab_df = pd.DataFrame([
            {"word": "rengos"}, {"word": "lotong"}, {"word": "enem"}, 
            {"word": "mali"}, {"word": "dafak"}
        ])
    
    # 3. 內建 [提示詞-圖片] 關聯矩陣
    prompts_dict = {
        "我喜歡的活動": ["activity_01.png", "activity_02.png", "activity_03.png", "activity_04.png"],
        "拜訪爺爺的一天": ["grandpa_01.png", "grandpa_02.png", "grandpa_03.png", "grandpa_04.png"],
        "我和朋友玩耍": ["friends_01.png", "friends_02.png", "friends_03.png", "friends_04.png"],
        "我的生活作息": ["routine_01.png", "routine_02.png", "routine_03.png", "routine_04.png"],
        "我喜歡的天氣": ["weather_01.png", "weather_02.png", "weather_03.png", "weather_04.png"],
        "我喜歡吃的東西": ["food_01.png", "food_02.png", "food_03.png", "food_04.png"],
        "伴我讀書的用品": ["study_01.png", "study_02.png", "study_03.png", "study_04.png"],
        "我喜歡的職業": ["job_01.png", "job_02.png", "job_03.png", "job_04.png"],
        "我喜歡的活動2": ["activity2_01.png", "activity2_02.png", "activity2_03.png", "activity2_04.png"],
        "我的生活作息2": ["routine2_01.png", "routine2_02.png", "routine2_03.png", "routine2_04.png"],
        "我喜歡的動物": ["animal_01.png", "animal_02.png", "animal_03.png", "animal_04.png"]
    }
        
    return valid_vocab_df, prompts_dict

# --- [模組 B] 介面視覺規範 ---
st.markdown("""
    <style>
    .exam-banner { background-color: #f0f7ff; border-left: 10px solid #1e40af; padding: 20px; border-radius: 5px; margin-bottom: 25px; }
    .word-card { font-family: 'Courier New', monospace; font-size: 32px; font-weight: bold; color: #1e3a8a; text-align: center; 
                 padding: 30px; border: 2px solid #e2e8f0; border-radius: 15px; background: white; transition: 0.3s; }
    .q-number { color: #64748b; font-size: 14px; margin-bottom: 5px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

def main():
    vocab_df, oral_prompts = load_static_data()

    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Emblem_of_Council_of_Indigenous_Peoples.svg/200px-Emblem_of_Council_of_Indigenous_Peoples.svg.png", width=150)
    st.sidebar.title("🌊 阿美語初級認證")
    app_mode = st.sidebar.radio("測驗單元切換", ["📝 考試說明與指南", "第一部分：單詞朗讀", "第二部分：簡答題", "第三部分：看圖說話"])

    if app_mode == "📝 考試說明與指南":
        st.markdown('<div class="exam-banner"><h3>📝 初級認證測驗指南</h3><p>考前必讀：測驗項目、配分與合格標準</p></div>', unsafe_allow_html=True)
        exam_info = {
            "項目 (Category)": ["測驗項目與配分", "測驗時間", "範圍與參考教材", "合格標準", "測驗方式"],
            "內容說明 (Details)": [
                "1. 口說測驗 (佔 40 分)：單詞朗讀 (10%)、簡答題 (20%)、看圖說話 (10%)\n2. 聽力測驗 (佔 60 分)：是非題、選擇題、配合題",
                "口說測驗：約 5 分鐘\n聽力測驗：約 20 分鐘",
                "1. 九階教材（第 1 至 3 階）\n2. 國中版句型篇\n3. 初級教材 — 生活會話篇\n4. 原住民族語言學習詞表",
                "總分須達 60 分（含）以上，且必須「同時」符合：聽力達 45 分，口說達 15 分",
                "電腦數位化測驗：看螢幕聽語音後點選答案或對麥克風回答。"
            ]
        }
        df_info = pd.DataFrame(exam_info)
        df_info.index = [""] * len(df_info) 
        st.table(df_info)

    elif app_mode == "第一部分：單詞朗讀":
        st.markdown('<div class="exam-banner"><h3>第一部分：單詞朗讀 (每題 2 分，共 10 分)</h3></div>', unsafe_allow_html=True)
        if st.button("🔄 刷新考卷"): st.rerun()
            
        # 安全抽樣：最多抽 5 題，題庫不夠就全拿
        sample_size = min(5, len(vocab_df))
        test_words = vocab_df.sample(n=sample_size)['word'].tolist()
        
        # 畫面渲染防呆：萬一抽出來不到 5 題，用 "---" 補齊 5 個空格，避免 UI 錯位報錯
        while len(test_words) < 5:
            test_words.append("---")

        cols = st.columns(5)
        for i, word in enumerate(test_words):
            with cols[i]:
                st.markdown(f'<div class="q-number">1-{i+1}.</div><div class="word-card">{word}</div>', unsafe_allow_html=True)

    elif app_mode == "第二部分：簡答題":
        st.markdown('<div class="exam-banner"><h3>第二部分：簡答題 (每題 4 分，共 20 分)</h3></div>', unsafe_allow_html=True)
        q_idx = st.select_slider("請選擇當前播放題號：", options=["2-1", "2-2", "2-3", "2-4", "2-5"])
        st.write(f"#### 🔊 {q_idx} (聽...)")
        st.progress(100, text="作答倒數：15 秒")

    elif app_mode == "第三部分：看圖說話":
        st.markdown('<div class="exam-banner"><h3>第三部分：看圖說話 (10 分)</h3></div>', unsafe_allow_html=True)
        
        prompt_text = random.choice(list(oral_prompts.keys()))
        st.markdown(f"#### 📌 中文提示：{prompt_text}")
        
        target_images = oral_prompts[prompt_text]
        display_imgs = []
        for img_name in target_images:
            img_path = os.path.join("images", img_name)
            display_imgs.append(img_path if os.path.exists(img_path) else None)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="q-number">圖片 A</div>', unsafe_allow_html=True)
            if display_imgs[0]: st.image(display_imgs[0], use_container_width=True)
            else: st.info(f"無圖片檔案: {target_images[0]}")
            
            st.markdown('<div class="q-number">圖片 C</div>', unsafe_allow_html=True)
            if display_imgs[2]: st.image(display_imgs[2], use_container_width=True)
            else: st.info(f"無圖片檔案: {target_images[2]}")
            
        with col2:
            st.markdown('<div class="q-number">圖片 B</div>', unsafe_allow_html=True)
            if display_imgs[1]: st.image(display_imgs[1], use_container_width=True)
            else: st.info(f"無圖片檔案: {target_images[1]}")
            
            st.markdown('<div class="q-number">圖片 D</div>', unsafe_allow_html=True)
            if display_imgs[3]: st.image(display_imgs[3], use_container_width=True)
            else: st.info(f"無圖片檔案: {target_images[3]}")

        st.divider()
        st.text_area("✍️ 草稿：", height=100)

if __name__ == "__main__":
    main()
