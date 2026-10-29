import streamlit as st
import pandas as pd
import random
import os
import json
import base64
import streamlit.components.v1 as components  # <--- 沙盒魔法的關鍵

# --- [元數據與效能設定] ---
st.set_page_config(page_title="Amis-Pro 族語認證衝刺", page_icon="🌊", layout="wide")

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

    st.sidebar.markdown("### <span style='color: #94a3b8;'>❖ sawm<span style='color: #ff4b4b;'>A</span>h 族語學院</span>", unsafe_allow_html=True)
    st.sidebar.title("🌊 阿美語初級認證")
    app_mode = st.sidebar.radio("練習單元切換", ["📝 考試說明", "🗣️ 單詞朗讀", "💬 簡單問答", "🖼️ 看圖說話"])

    if app_mode == "📝 考試說明":
        st.markdown('<div class="exam-banner"><h3>📝 測驗指南</h3><p>考前必讀：[測驗項目]-[配分]-[合格標準]</p></div>', unsafe_allow_html=True)
        exam_info = {
            "項目": ["測驗項目與配分", "測驗時間", "範圍與參考教材", "合格標準", "測驗方式"],
            "內容說明": [
                "1. 口說測驗 (佔40分)：單詞朗讀 (10%)、簡單問答 (20%)、看圖說話 (10%)\n2. 聽力測驗 (佔60分)：是非題、選擇題、配合題",
                "口說測驗：約 5分鐘 / 聽力測驗：約 20分鐘",
                "1. 九階教材（第 1 至 3 階）\n2. 國中版句型篇\n3. 初級教材 — 生活會話篇\n4. 海岸阿美族語學習詞表",
                "1. 總分須達 60分(含)以上，\n2. 且必須「同時」符合：聽力達 45分，口說達 15分",
                "電腦數位化：聆聽語音、螢幕點選答案、對麥克風回答"
            ]
        }
        df_info = pd.DataFrame(exam_info)
        df_info.index = [""] * len(df_info) 
        st.table(df_info)

    elif app_mode == "🗣️ 單詞朗讀":
        st.markdown('<div class="exam-banner"><h3>單詞朗讀 </h3></div>', unsafe_allow_html=True)
        if st.button("🔄 題目刷新"): st.rerun()
        
        test_words = vocab_df.sample(n=min(5, len(vocab_df)))['word'].tolist()
        cols = st.columns(5)
        
        for i, word in enumerate(test_words + ["---"]*(5-len(test_words))):
            with cols[i]:
                w_str = str(word)
                if len(w_str) <= 6:
                    f_size = "1.6rem"
                elif len(w_str) <= 10:
                    f_size = "1.1rem"
                else:
                    f_size = "0.9rem"
                
                if w_str != "---":
                    audio_path = os.path.join("audio", "words", f"{w_str}.mp3")
                    
                    if os.path.exists(audio_path):
                        with open(audio_path, "rb") as f:
                            audio_bytes = f.read()
                        audio_base64 = base64.b64encode(audio_bytes).decode()
                        
                        # --- 🔊 終極解法：使用 Html 沙盒組件保護 JavaScript ---
                        html_code = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                        <style>
                            body {{ margin: 0; padding: 5px; font-family: sans-serif; }}
                            .vocab-card {{
                                text-align: center;
                                padding: 20px 5px;
                                border: 2px solid #e2e8f0;
                                border-radius: 12px;
                                background: white;
                                cursor: pointer;
                                transition: all 0.2s ease-in-out;
                            }}
                            .vocab-card:hover {{
                                border-color: #ff4b4b;
                                box-shadow: 0 4px 12px rgba(255, 75, 75, 0.15);
                                transform: translateY(-3px);
                            }}
                            .q-number {{ color: #64748b; font-size: 14px; margin-bottom: 5px; font-weight: bold; }}
                            .vocab-word {{ color: #1e3a8a; font-weight: bold; font-family: 'Courier New', monospace; font-size: {f_size}; white-space: nowrap; }}
                        </style>
                        </head>
                        <body>
                            <audio id="audio_player" src="data:audio/mp3;base64,{audio_base64}"></audio>
                            <div class="vocab-card" onclick="document.getElementById('audio_player').play()">
                                <div class="q-number">1-{i+1}.</div>
                                <div class="vocab-word">{w_str}</div>
                            </div>
                        </body>
                        </html>
                        """
                        components.html(html_code, height=130, scrolling=False)
                    else:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 20px 5px; border: 2px solid #e2e8f0; border-radius: 12px; background: white; height: 100%;">
                            <div class="q-number">1-{i+1}.</div>
                            <div style="color: #1e3a8a; font-weight: bold; font-family: 'Courier New', monospace; font-size: {f_size}; white-space: nowrap;">{w_str}</div>
                            <div style="color: #ccc; font-size: 12px; margin-top: 8px;">🔇 尚無音檔</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 20px 5px; border: 2px solid #e2e8f0; border-radius: 12px; background: white; height: 100%;">
                        <div class="q-number">1-{i+1}.</div>
                        <div style="color: #1e3a8a; font-weight: bold; font-family: 'Courier New', monospace; font-size: {f_size}; white-space: nowrap;">---</div>
                    </div>
                    """, unsafe_allow_html=True)

    elif app_mode == "💬 簡單問答":
        st.markdown('<div class="exam-banner"><h3>簡單問答 </h3></div>', unsafe_allow_html=True)
        
        qa_sets = [f"題組 {i}" for i in range(1, 8)]
        
        if 'current_qa_set' not in st.session_state:
            st.session_state.current_qa_set = qa_sets[0]

        selected_set_ui = st.selectbox("🎯 請選擇練習題組：", ["🎲 隨機抽題組"] + qa_sets)
        
        if selected_set_ui == "🎲 隨機抽題組":
            if st.button("🎲 重新隨機抽題組"):
                st.session_state.current_qa_set = random.choice(qa_sets)
            current_set = st.session_state.current_qa_set
        else:
            current_set = selected_set_ui

        st.markdown(f"#### 當前練習：{current_set}")
        set_num = current_set.split(" ")[1]
        st.divider()
        
        st.markdown("<p style='font-size:14px; color:#64748b; font-weight:bold; margin-bottom:10px;'>請選擇當前播放題號：</p>", unsafe_allow_html=True)
        
        if 'current_q_idx' not in st.session_state:
            st.session_state.current_q_idx = 1

        btn_cols = st.columns(5)
        for i in range(1, 6):
            btn_type = "primary" if st.session_state.current_q_idx == i else "secondary"
            if btn_cols[i-1].button(f"第 {i} 題", key=f"q_btn_{i}", type=btn_type, use_container_width=True):
                st.session_state.current_q_idx = i
                st.rerun()

        q_idx = st.session_state.current_q_idx
        st.markdown(f'#### 🔊 {current_set} - <span style="font-size: 16px; font-weight: normal; color: red;">第 {q_idx} 題</span>', unsafe_allow_html=True)
        
        audio_filename = f"{set_num}-{q_idx}.mp3"
        audio_path = os.path.join("audio", "qa", audio_filename)
        
        if os.path.exists(audio_path):
            st.audio(audio_path, format="audio/mp3")
        else:
            st.warning(f"⚠️ 找不到音檔：{audio_filename}，請確認是否已放入 audio/qa/ 資料夾中。")

    elif app_mode == "🖼️ 看圖說話":
        st.markdown('<div class="exam-banner"><h3>看圖說話 <span style="font-size: 16px; color: #64748b; font-weight: normal;">(附參考答案)</span></h3></div>', unsafe_allow_html=True)
        
        # --- [新增：萬用前言與結語展開區塊] ---
        with st.expander("🗣️ （前言）"):
            st.markdown("""
            1. **(預留前言族語短語 1)**
            2. **(預留前言族語短語 2)**
            3. **(預留前言族語短語 3)**
            """)
            intro_audio = os.path.join("audio", "reference", "intro.mp3")
            if os.path.exists(intro_audio):
                st.audio(intro_audio, format="audio/mp3")
            else:
                st.caption("🔇 尚未配置前言音檔 (預期路徑: audio/reference/intro.mp3)")

        with st.expander("🗣️ （結語）"):
            st.markdown("""
            1. **(預留結語族語短語 1)**
            2. **(預留結語族語短語 2)**
            3. **(預留結語族語短語 3)**
            """)
            outro_audio = os.path.join("audio", "reference", "outro.mp3")
            if os.path.exists(outro_audio):
                st.audio(outro_audio, format="audio/mp3")
            else:
                st.caption("🔇 尚未配置結語音檔 (預期路徑: audio/reference/outro.mp3)")
        
        st.write("") # 增加微小間距區隔
        
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

        st.markdown(f"####  當前主題：{prompt_text}")
        
        audio_mapping = {
            "我喜歡的活動": "activity.mp3", "拜訪爺爺的一天": "grandpa.mp3",
            "我和朋友玩耍": "friends.mp3", "我的生活作息": "routine.mp3",
            "我喜歡的天氣": "weather.mp3", "我喜歡吃的東西": "food.mp3",
            "伴我讀書的用品": "study.mp3", "我喜歡的職業": "job.mp3",
            "我喜歡的活動2": "activity2.mp3", "我的生活作息2": "routine2.mp3",
            "我喜歡的動物": "animal.mp3"
        }
        
        target_audio = audio_mapping.get(prompt_text)
        if target_audio:
            audio_path = os.path.join("audio", "prompts", target_audio)
            if os.path.exists(audio_path):
                st.audio(audio_path, format="audio/mp3")
            else:
                st.caption(f"🔇 此題尚無語音提示 ({target_audio})")

        target_images = oral_prompts[prompt_text]
        cols = st.columns(2)
        for i, label in enumerate(['A','B','C','D']):
            with cols[i % 2]:
                st.markdown(f'<div class="q-number">圖片 {label}</div>', unsafe_allow_html=True)
                img_path = os.path.join("images", target_images[i])
                if os.path.exists(img_path): st.image(img_path, use_container_width=True)
                else: st.info(f"遺失: {target_images[i]}")

        st.divider()
        
        # --- [資料層] 11題看圖說話的固定參考答案與音檔對應表 ---
        # 建議將音檔統一放置於 audio/reference/ 資料夾中
        reference_data = {
            "我喜歡的活動": {"text": "（請在此填入標準阿美語參考文字）", "audio": "ref_activity.mp3"},
            "拜訪爺爺的一天": {"text": "（請在此填入標準阿美語參考文字）", "audio": "ref_grandpa.mp3"},
            "我和朋友玩耍": {"text": "（請在此填入標準阿美語參考文字）", "audio": "ref_friends.mp3"},
            "我的生活作息": {"text": "（請在此填入標準阿美語參考文字）", "audio": "ref_routine.mp3"},
            "我喜歡的天氣": {"text": "（請在此填入標準阿美語參考文字）", "audio": "ref_weather.mp3"},
            "我喜歡吃的東西": {"text": "（請在此填入標準阿美語參考文字）", "audio": "ref_food.mp3"},
            "伴我讀書的用品": {"text": "（請在此填入標準阿美語參考文字）", "audio": "ref_study.mp3"},
            "我喜歡的職業": {"text": "（請在此填入標準阿美語參考文字）", "audio": "ref_job.mp3"},
            "我喜歡的活動2": {"text": "（請在此填入標準阿美語參考文字）", "audio": "ref_activity2.mp3"},
            "我的生活作息2": {"text": "（請在此填入標準阿美語參考文字）", "audio": "ref_routine2.mp3"},
            "我喜歡的動物": {"text": "（請在此填入標準阿美語參考文字）", "audio": "ref_animal.mp3"}
        }

        # --- [UIUX層] 顯示標準參考答案與語音示範 ---
        st.markdown('<div class="exam-banner" style="background-color: #f0fdf4; border-left-color: #16a34a;"><h3>💡 參考答案</h3></div>', unsafe_allow_html=True)
        
        ref_info = reference_data.get(prompt_text)
        if ref_info:
            # 顯示阿美語標準文字 (可根據 10-5 詞彙規範進行精確校準)
            st.info(f"**📖 參考句型：**\n\n{ref_info['text']}")
            
            # 載入並顯示標準參考音檔
            ref_audio_path = os.path.join("audio", "reference", ref_info["audio"])
            if os.path.exists(ref_audio_path):
                st.audio(ref_audio_path, format="audio/mp3")
            else:
                st.caption(f"🔇 尚未配置參考音檔 (預期路徑: {ref_audio_path})")
        else:
            st.warning("⚠️ 系統尚未建檔此題的參考資料")

if __name__ == "__main__":
    main()

# ==========================================
# 頁尾資訊
# ==========================================
st.sidebar.markdown("---")
st.sidebar.caption("© 2026 sawmAh singsi. All Rights Reserved.")
st.sidebar.caption("v1.3 (Fixed Reference Integration)")
