import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from collections import Counter
import datetime
import io

# --- 1. एनालिसिस इंजन ---

def rf_prediction(nums, days=10):
    if len(nums) < 15: return ["--"] * days
    try:
        predictions = []
        current_nums = list(nums)
        for _ in range(days):
            X, y = [], []
            for i in range(5, len(current_nums)):
                X.append(current_nums[i-5:i])
                y.append(current_nums[i])
            
            rf = RandomForestClassifier(n_estimators=100, random_state=42)
            rf.fit(X, y)
            
            last_5 = np.array(current_nums[-5:]).reshape(1, -1)
            pred = rf.predict(last_5)[0]
            predictions.append(f"{pred:02d}")
            current_nums.append(pred) # अगले दिन के लिए इसे जोड़ें
        return predictions
    except:
        return ["--"] * days

# --- 2. मुख्य ऐप ---
st.set_page_config(page_title="Ultimate AI Predictor", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1a73e8;'>🎯 Hybrid AI: Same Day & 10-Days Forecast</h1>", unsafe_allow_html=True)

# 'key' पैरामीटर डालने से एक्सेल अपडेट होने पर एरर नहीं आएगा
uploaded_file = st.file_uploader("📂 अपनी Excel फाइल अपलोड करें", type=['xlsx'], key="file_refresher")

if uploaded_file:
    try:
        # फ़ाइल को सीधे बाइट्स से पढ़ना (एरर रोकने के लिए)
        file_bytes = uploaded_file.getvalue()
        df = pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
        
        # कॉलम साफ़ करना
        df.columns = [str(c).strip().upper() for c in df.columns]
        date_col = df.columns[1] # Column B
        shift_cols = list(df.columns[2:9]) # C to I

        st.write("---")
        target_date = st.date_input("📅 प्रेडिक्शन शुरू करने की तारीख चुनें:", datetime.date.today())

        if st.button("🔮 Deep Analysis शुरू करें"):
            # तारीख कन्वर्जन
            df[date_col] = pd.to_datetime(df[date_col]).dt.date
            
            # चुनी हुई तारीख का और उसके पहले का डेटा
            history_df = df[df[date_col] < target_date]
            current_day_df = df[df[date_col] == target_date]

            # प्रेडिक्शन के लिए तारीखों की लिस्ट (Next 10 Days)
            future_dates = [(target_date + datetime.timedelta(days=i)).strftime('%d-%b') for i in range(11)] # Same day + 10 days

            all_results = []

            for s_name in shift_cols:
                s_nums = history_df[s_name].dropna().astype(str).str.strip()
                clean_nums = [int(float(n)) for n in s_nums if n.replace('.0','').isdigit()]
                
                # Same Day Result (📍 Today)
                today_val = current_day_df[s_name].dropna().values
                same_day_actual = f"{int(float(today_val[0])):02d}" if len(today_val) > 0 else "--"

                # अगले 10 दिन का प्रेडिक्शन
                forecast = rf_prediction(clean_nums, days=11) # 0 index is today's prediction
                
                res_row = {"Shift": s_name, "📍 SAME DAY": same_day_actual}
                for idx, d_label in enumerate(future_dates):
                    res_row[d_label] = forecast[idx]
                
                all_results.append(res_row)

            # डिस्प्ले टेबल
            st.subheader(f"📊 10-Days Prediction Table (Starting {target_date})")
            st.table(pd.DataFrame(all_results))
            
            st.info("💡 **Note:** 'SAME DAY' कॉलम आपकी एक्सेल शीट का असली नंबर दिखाता है। बाकी कॉलम AI द्वारा अगले 10 दिनों के प्रेडिक्शन हैं।")
            st.balloons()

    except Exception as e:
        st.error(f"❌ गड़बड़ हुई: {e}")
        st.info("कृपया चेक करें कि एक्सेल में तारीखें 'B' कॉलम में और नंबर 'C से I' कॉलम में सही हैं।")
else:
    st.info("एक्सेल फाइल अपलोड करें।")
    
