import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from collections import Counter
import datetime
import io

# --- 1. एनालिसिस इंजन (मल्टी-डे प्रेडिक्शन के लिए) ---

def get_predictions(nums, days=11):
    if len(nums) < 15:
        return ["--"] * days, ["--"] * days, ["--"] * days
    
    ai_preds = []
    freq_preds = []
    markov_preds = []
    
    current_nums = list(nums)
    
    for _ in range(days):
        # AI Prediction (Random Forest)
        X, y = [], []
        for i in range(5, len(current_nums)):
            X.append(current_nums[i-5:i])
            y.append(current_nums[i])
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X, y)
        last_5 = np.array(current_nums[-5:]).reshape(1, -1)
        pred = rf.predict(last_5)[0]
        ai_preds.append(f"{pred:02d}")
        
        # Frequency (Top)
        counts = Counter(current_nums)
        freq_preds.append(f"{counts.most_common(1)[0][0]:02d}")
        
        # Markov Chain
        last_num = current_nums[-1]
        transitions = [current_nums[i+1] for i in range(len(current_nums)-1) if current_nums[i] == last_num]
        if transitions:
            markov_preds.append(f"{Counter(transitions).most_common(1)[0][0]:02d}")
        else:
            markov_preds.append("--")
            
        current_nums.append(pred) # अगले दिन के लूप के लिए

    return ai_preds, freq_preds, markov_preds

# --- 2. मुख्य ऐप सेटअप (Zoom Support के साथ) ---
st.set_page_config(page_title="MAYA AI: 10-Day Hybrid", layout="wide")

# CSS for Zoom and Mobile Table view
st.markdown("""
    <style>
    .reportview-container .main .block-container { max-width: 100%; padding: 1rem; }
    table { width: 100% !important; font-size: 16px !important; }
    .stTable { overflow-x: auto !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 10-Days Hybrid Prediction Sheets")

uploaded_file = st.file_uploader("📂 अपनी Excel फाइल अपलोड करें", type=['xlsx'], key="refresher")

if uploaded_file:
    try:
        # डेटा पढ़ना
        file_bytes = uploaded_file.getvalue()
        df = pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        date_col = df.columns[1] # Column B
        shift_cols = list(df.columns[2:9]) # Column C to I (7 Shifts)

        st.write("---")
        target_date = st.date_input("📅 प्रेडिक्शन शुरू करने की तारीख:", datetime.date.today())

        if st.button("🔮 सभी 10 सेट्स तैयार करें"):
            df[date_col] = pd.to_datetime(df[date_col]).dt.date
            
            # अगले 10 दिनों के लिए लूप (0 = Today, 1-10 = Next Days)
            for day_offset in range(11):
                current_target = target_date + datetime.timedelta(days=day_offset)
                st.write(f"---")
                st.subheader(f"📅 प्रेडिक्शन शीट: {current_target.strftime('%d-%b-%Y')}")
                
                sheet_data = []
                
                # चुनी हुई तारीख के हिसाब से इतिहास (History)
                history_df = df[df[date_col] < target_date]
                current_day_data = df[df[date_col] == current_target]

                for s_name in shift_cols:
                    s_nums = history_df[s_name].dropna().astype(str).str.strip()
                    clean_nums = [int(float(n)) for n in s_nums if n.replace('.0','').isdigit()]
                    
                    # Same Day (📍) - अगर उस दिन का डेटा एक्सेल में है
                    today_val = current_day_data[s_name].dropna().values
                    same_day = f"{int(float(today_val[0])):02d}" if len(today_val) > 0 else "--"
                    
                    # प्रेडिक्शन प्राप्त करें
                    ai_list, freq_list, markov_list = get_predictions(clean_nums)
                    
                    sheet_data.append({
                        "Shift": s_name,
                        "📍 SAME DAY": same_day,
                        "🤖 AI (ML)": ai_list[day_offset],
                        "📈 FREQUENCY": freq_list[day_offset],
                        "🔗 MARKOV": markov_list[day_offset]
                    })

                # टेबल डिस्प्ले
                st.table(pd.DataFrame(sheet_data))

            st.success("✅ अगले 10 दिनों की हाइब्रिड सीटें तैयार हैं।")
            st.info("💡 **Zoom Tip:** मोबाइल पर आप स्क्रीन को पिंच करके (Pinch Zoom) अंकों को बड़ा या छोटा देख सकते हैं।")
            st.balloons()

    except Exception as e:
        st.error(f"❌ गड़बड़ हुई: {e}")
else:
    st.info("शुरू करने के लिए एक्सेल फाइल अपलोड करें।")
    
