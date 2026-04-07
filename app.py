import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from collections import Counter
import datetime
import io

# --- 1. एनालिसिस मेथड्स ---

# Frequency Analysis
def get_freq_analysis(nums):
    if len(nums) == 0: return "--"
    counts = Counter(nums)
    return f"{counts.most_common(1)[0][0]:02d}"

# Markov Chain Prediction
def markov_prediction(nums):
    if len(nums) < 2: return "--"
    last_num = nums[-1]
    transitions = []
    for i in range(len(nums)-1):
        if nums[i] == last_num:
            transitions.append(nums[i+1])
    if transitions:
        res = Counter(transitions).most_common(1)[0][0]
        return f"{res:02d}"
    return "--"

# Machine Learning (Random Forest)
def rf_prediction(nums):
    if len(nums) < 15: return "--"
    X, y = [], []
    for i in range(5, len(nums)):
        X.append(nums[i-5:i])
        y.append(nums[i])
    
    try:
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X, y)
        last_5 = np.array(nums[-5:]).reshape(1, -1)
        res = rf.predict(last_5)[0]
        return f"{res:02d}"
    except:
        return "--"

# --- 2. मुख्य ऐप सेटअप ---
st.set_page_config(page_title="Ultimate AI Predictor", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1a73e8;'>🎯 Hybrid AI Prediction Engine (All Shifts)</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 अपनी Excel फाइल अपलोड करें", type=['xlsx'])

if uploaded_file:
    try:
        # डेटा पढ़ना और कॉलम साफ़ करना
        df = pd.read_excel(io.BytesIO(uploaded_file.getvalue()), engine='openpyxl')
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # तारीख और शिफ्ट्स पहचानना
        date_col = df.columns[1] # Column B
        shift_cols = list(df.columns[2:9]) # Column C to I (7 Shifts)

        st.write("---")
        # तारीख चुनने का विकल्प
        target_date = st.date_input("📅 प्रेडिक्शन के लिए तारीख चुनें:", datetime.date.today())

        if st.button("🔮 Deep Analysis शुरू करें"):
            # डेटा को तारीख के हिसाब से फिल्टर करना
            df[date_col] = pd.to_datetime(df[date_col]).dt.date
            history_df = df[df[date_col] < target_date]
            current_day_df = df[df[date_col] == target_date]

            results = []

            for s_name in shift_cols:
                # उस शिफ्ट का पिछला डेटा निकालना
                s_nums = history_df[s_name].dropna().astype(str).str.strip()
                clean_nums = [int(float(n)) for n in s_nums if n.replace('.0','').isdigit()]
                
                # Same Day Result (अगर शीट में पहले से है)
                today_val = current_day_df[s_name].dropna().values
                same_day = f"{int(float(today_val[0])):02d}" if len(today_val) > 0 else "--"

                if len(clean_nums) >= 15:
                    results.append({
                        "Shift": s_name,
                        "📍 SAME DAY": same_day,
                        "🤖 AI (ML)": rf_prediction(clean_nums),
                        "📈 FREQUENCY": get_freq_analysis(clean_nums),
                        "🔗 MARKOV": markov_prediction(clean_nums)
                    })
                else:
                    results.append({
                        "Shift": s_name, "📍 SAME DAY": same_day,
                        "🤖 AI (ML)": "Low Data", "📈 FREQUENCY": "Low Data", "🔗 MARKOV": "Low Data"
                    })

            # --- डिस्प्ले रिजल्ट्स ---
            st.subheader(f"📊 सभी शिफ्ट्स का हाइब्रिड प्रेडिक्शन ({target_date})")
            st.table(pd.DataFrame(results))

            st.info("💡 **हाइब्रिड टिप:** यदि किसी एक ही शिफ्ट में AI, Frequency और Markov तीनों एक ही नंबर दिखा रहे हैं, तो वह 'Strong' नंबर है।")
            st.balloons()

    except Exception as e:
        st.error(f"❌ गड़बड़ हुई: {e}")
else:
    st.info("शुरू करने के लिए एक्सेल फाइल अपलोड करें।")
    
