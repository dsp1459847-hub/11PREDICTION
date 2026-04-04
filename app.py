import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from collections import Counter

# --- नए एनालिसिस मेथड्स ---

# 1. Frequency Analysis (सबसे ज्यादा आने वाले नंबर)
def get_freq_analysis(nums):
    counts = Counter(nums)
    top_3 = [n for n, c in counts.most_common(3)]
    return top_3

# 2. Markov Chain (अगली संख्या की संभावना)
def markov_prediction(nums):
    last_num = nums[-1]
    transitions = []
    for i in range(len(nums)-1):
        if nums[i] == last_num:
            transitions.append(nums[i+1])
    if transitions:
        return Counter(transitions).most_common(1)[0][0]
    return None

# --- मुख्य ऐप ---
st.set_page_config(page_title="Ultimate AI Predictor", layout="wide")
st.title("🎯 Advanced Hybrid Prediction Engine")

uploaded_file = st.file_uploader("अपनी Excel फाइल अपलोड करें", type=['xlsx'])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        shift_cols = df.columns[2:9] # C1 to I1
        target_shift = st.selectbox("शिफ्ट चुनें:", shift_cols)

        if st.button("🔮 Deep Analysis शुरू करें"):
            # डेटा क्लीनिंग
            temp_list = []
            for _, row in df.iterrows():
                val = str(row[target_shift]).strip()
                if val.isdigit():
                    temp_list.append(int(val))
            
            nums = np.array(temp_list)

            if len(nums) < 15:
                st.error("डेटा बहुत कम है! कम से कम 15-20 नंबर्स चाहिए।")
            else:
                # 1. Machine Learning (Random Forest)
                X, y = [], []
                for i in range(5, len(nums)):
                    X.append(nums[i-5:i])
                    y.append(nums[i])
                
                rf = RandomForestClassifier(n_estimators=200)
                rf.fit(X, y)
                last_5 = nums[-5:].reshape(1, -1)
                rf_res = rf.predict(last_5)[0]

                # 2. Frequency Method
                freq_res = get_freq_analysis(nums)

                # 3. Markov Method
                markov_res = markov_prediction(nums)

                # --- डिस्प्ले रिजल्ट्स ---
                st.divider()
                st.subheader("📊 विभिन्न तरीकों से प्राप्त परिणाम:")
                
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    st.info("🤖 AI (Machine Learning)")
                    st.header(f"{rf_res:02d}")
                    st.write("पैटर्न के आधार पर")

                with c2:
                    st.success("📈 Frequency (Top)")
                    st.header(f"{freq_res[0]:02d}")
                    st.write("सबसे ज्यादा आने वाला")

                with c3:
                    st.warning("🔗 Markov Chain")
                    st.header(f"{markov_res:02d}" if markov_res is not None else "--")
                    st.write("समीपता के आधार पर")

                st.balloons()
                st.write("---")
                st.markdown("### 💡 एक्सपर्ट टिप: अगर दो या तीन मेथड्स में एक ही नंबर दिखाई दे, तो उस नंबर के आने की संभावना सबसे अधिक होती है।")

    except Exception as e:
        st.error(f"Error: {e}")
