import streamlit as st
import pandas as pd
import random
import os
import json

# --- [元數據與效能設定] ---
st.set_page_config(page_title="Amis-Pro 族語認證衝刺", page_icon="🌊", layout="wide")

# --- [新增：草稿永久化管理模組] ---
DRAFTS_FILE = "data/user_drafts.json"

def load_all_drafts():
    """從硬碟讀取所有已存草稿"""
    if os.path.exists(DRAFTS_FILE):
        try:
            with open(DRAFTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_single_draft(topic, content):
    """將單一題目的草稿寫入硬碟"""
    drafts = load_all_drafts()
    drafts[topic] = content
    os.makedirs("data", exist_ok=True)
    with open(DRAFTS_FILE, "w", encoding="utf-8") as f:
        json.dump(drafts, f, ensure_ascii=False, indent=2)

# --- [模組 A] 極速資料載入引擎 ---
@st.cache_data
def load_static_data():
    try:
        vocab_df = pd.read_csv("data/vocab.csv")
        vocab_df = vocab_df.dropna(subset=['word']) 
    except:
        vocab_df = pd.DataFrame([{"word": "rengos"}, {"word": "lotong"}, {"word": "enem"}])

    def is_multi_syllable(word):
        vowels = set("aeiouAEIOU")
        return sum(1 for char in str(word) if char in vowels) > 1

    vocab_df = vocab_df[vocab_df['word'].apply(is_multi_syllable)]
    
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
    return vocab_df, prompts_dict

# --- [介面視覺規範] ---
st.markdown("""
    <style>
    .exam-banner { background-color: #f0f7ff; border-left: 10px solid #1e40af; padding: 20px; border-radius: 5px; margin-bottom: 25px; }
    .q-number { color: #64748b; font-size: 14px; margin-bottom: 5px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

def main():
    vocab_df, oral_prompts = load_static_data()
    all_drafts = load_all_drafts() # 載入所有歷史草稿

    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Emblem_of_Council_of_Indigenous_Peoples.svg/200px-Emblem_of_Council_of_Indigenous_Peoples.svg.png", width=150)
    st.sidebar.title("🌊 阿美語初級認證")
    app_mode = st.sidebar.radio("測驗單元切換", ["📝 考試說明", "第一部分：單詞朗讀", "第二部分：簡答題", "第三部分：看圖說話"])

    if app_mode == "📝 考試說明":
        # 恢復完整的考試說明表格
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
        
        test_words = vocab_df.sample(n=min(5, len(vocab_df)))['word'].tolist()
        cols = st.columns(5)
        
        # 維持動態字體縮放，確保單字不會被折行
        for i, word in enumerate(test_words + ["---"]*(5-len(test_words))):
            with cols[i]:
                w_str = str(word)
                if len(w_str) <= 6:
                    f_size = "1.6rem"
                elif len(w_str) <= 10:
                    f_size = "1.1rem"
                else:
                    f_size = "0.9rem"
                    
                st.markdown(f"""<div style="text-align: center; padding: 20px 5px; border: 2px solid #e2e8f0; border-radius: 12px; background: white; height: 100%;">
                    <div class="q-number">1-{i+1}.</div>
                    <div style="color: #1e3a8a; font-weight: bold; font-family: 'Courier New', monospace; font-size: {f_size}; white-space: nowrap;">{w_str}</div>
                </div>""", unsafe_allow_html=True)

    elif app_mode == "第二部分：簡答題":
        st.markdown('<div class="exam-banner"><h3>第二部分：簡答題 (每題 4 分，共 20 分)</h3></div>', unsafe_allow_html=True)
        q_idx = st.select_slider("請選擇當前播放題號：", options=["2-1", "2-2", "2-3", "2-4", "2-5"])
        st.write(f"#### 🔊 {q_idx} (聽...)")
        st.progress(100, text="作答倒數：15 秒")

    elif app_mode == "第三部分：看圖說話":
        st.markdown('<div class="exam-banner"><h3>第三部分：看圖說話 (草稿已自動同步儲存)</h3></div>', unsafe_allow_html=True)
        
        topic_list = list(oral_prompts.keys())
        
        if 'current_topic' not in st.session_state:
            st.session_state.current_topic = topic_list[0]

        selected_ui = st.selectbox("🎯 請選擇練習主題：", ["🎲 隨機抽題"] + topic_list)
        
        if selected_ui == "🎲 隨機抽題":
            if st.button("🎲 重新隨機抽題"):
                st.session_state.current_topic = random.choice(topic_list)
            prompt_text = st.session_state.current_topic
        else:
            prompt_text = selected_ui

        st.markdown(f"#### 📌 當前主題：{prompt_text}")
        
        target_images = oral_prompts[prompt_text]
        cols = st.columns(2)
        for i, label in enumerate(['A','B','C','D']):
            with cols[i % 2]:
                st.markdown(f'<div class="q-number">圖片 {label}</div>', unsafe_allow_html=True)
                img_path = os.path.join("images", target_images[i])
                if os.path.exists(img_path): st.image(img_path, use_container_width=True)
                else: st.info(f"遺失: {target_images[i]}")

        st.divider()
        
        # 永久化草稿區
        existing_draft = all_drafts.get(prompt_text, "")
        
        draft_input = st.text_area(
            f"✍️ 【{prompt_text}】的專屬草稿（系統會自動儲存）：",
            value=existing_draft,
            height=200,
            key=f"draft_{prompt_text}",
            help="此處輸入的內容會自動存檔，下次選到同一題時會自動載入。"
        )

        if draft_input != existing_draft:
            save_single_draft(prompt_text, draft_input)
            st.toast(f"✅ {prompt_text} 草稿已更新", icon='💾')

if __name__ == "__main__":
    main()
