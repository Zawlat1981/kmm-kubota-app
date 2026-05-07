import streamlit as st
import pandas as pd

st.set_page_config(page_title="KMM Equipment Calculator", page_icon="🚜", layout="centered")

# Google Sheet အချက်အလက်
SHEET_ID = "1QqQvPKH7G0hqqhd_0V6cP40Htl8qdFEZ6nHBVe_53_g"
# သင် အခု အသစ်ပြင်ထားတဲ့ Tab နာမည်ကို ဒီမှာ ထည့်ပေးပါ (ဥပမာ - Sheet1 သို့မဟုတ် Attachments)
ATTACHMENT_SHEET = "Sheet1" 

@st.cache_data(ttl=60)
def get_data():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={ATTACHMENT_SHEET}"
    try:
        df = pd.read_csv(url, header=0)
        df = df.fillna(0)
        return df
    except Exception as e:
        st.error(f"Google Sheet ဖတ်လို့မရပါ: {e}")
        return pd.DataFrame()

df = get_data()

if not df.empty:
    st.markdown("<h2 style='text-align: center; color: #333;'>🚜 Equipment & Attachments Calculator</h2>", unsafe_allow_html=True)
    
    # ၁။ မော်ဒယ် ရွေးချယ်ခြင်း
    model_col = 'Model1' # Excel ထဲက Column ခေါင်းစဉ်အတိုင်း
    models = sorted(df[model_col].unique().astype(str).tolist())
    models = [m for m in models if m not in ["0", "0.0", "nan", "Model1"]]
    
    selected_model = st.selectbox("စက်မော်ဒယ် ရွေးချယ်ပါ (Tractor/Excavator/Combine) -", models)
    filtered_df = df[df[model_col] == selected_model]

    selected_prices = []
    st.write("---")
    st.subheader(f"🛠 {selected_model} အတွက် နောက်တွဲများ")

    # Dropdown Function
    def create_select(label, m_col, p_col):
        if m_col in filtered_df.columns and p_col in filtered_df.columns:
            items = filtered_df[[m_col, p_col]].drop_duplicates()
            options = []
            for _, row in items.iterrows():
                name = str(row[m_col]).strip()
                price = row[p_col]
                if name not in ["0", "0.0", "nan"]:
                    options.append({"label": f"{name} (+{price:,.0f} MMK)", "price": float(price)})
            
            if options:
                choice = st.selectbox(f"{label} ရွေးချယ်ရန် -", ["မယူပါ"] + [o["label"] for o in options])
                if choice != "မယူပါ":
                    return next(item["price"] for item in options if item["label"] == choice)
        return 0

    # ၂။ အမျိုးအစားအလိုက် Column ခွဲပြသခြင်း
    col1, col2 = st.columns(2)

    with col1:
        st.info("🚜 Tractor & Harvester")
        selected_prices.append(create_select("Rotary", "Rotary_Model1", "Rotary_Price"))
        selected_prices.append(create_select("Harrow", "Harrow_Model1", "Harrow_Price"))
        selected_prices.append(create_select("Plow", "Plow_Model1", "Plow_Price"))
        selected_prices.append(create_select("Bean Kit", "BEANKIT_Model1", "BEANKIT_Price"))
        selected_prices.append(create_select("Corn Kit", "CORNKIT_Model1", "CORNKIT_Price"))

    with col2:
        st.info("🏗 Excavator & Others")
        selected_prices.append(create_select("EHB01 Breaker", "EHB01_Model1", "EHB01_Price"))
        selected_prices.append(create_select("EHB03 Breaker", "EHB03_Model1", "EHB03_Price"))
        selected_prices.append(create_select("EHB05 Breaker", "EHB05_Model1", "EHB05_Price"))
        selected_prices.append(create_select("Sowing Machine", "SOWINGMACHINE_Model1", "SOWINGMACHINE_Price"))
        selected_prices.append(create_select("Semi-Auto Sowing", "SEMI-AUTOSOWINGMAACHINE_Model1", "SEMI-AUTOSOWINGMAACHINE_Price"))
        selected_prices.append(create_select("MATV2", "MATV2_Model1", "MATV2_Price"))

    # ၃။ စုစုပေါင်းတွက်ချက်ခြင်း
    grand_total_att = sum(selected_prices)
    st.write("---")
    if grand_total_att > 0:
        st.success(f"### 📄 ရွေးချယ်ထားသော နောက်တွဲစုစုပေါင်း: {grand_total_att:,.0f} MMK")
    else:
        st.write("နောက်တွဲများကို ရွေးချယ်တွက်ချက်နိုင်ပါသည်။")

else:
    st.warning("Data load လုပ်၍မရဖြစ်နေပါသည်။ Google Sheet ကို စစ်ဆေးပေးပါ။")

st.markdown("<br><hr><center><small>© 2026 KMM Equipment Calculator</small></center>", unsafe_allow_html=True)
















