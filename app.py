import streamlit as st
import pandas as pd

st.set_page_config(page_title="KMM Equipment Calculator", page_icon="🚜", layout="centered")

# Google Sheet ID
SHEET_ID = "1QqQvPKH7G0hqqhd_0V6cP40Htl8qdFEZ6nHBVe_53_g"

# Tab အမည်များ
TRACTOR_SHEET = "Kubota"
ATTACHMENT_SHEET = "Attachments_List"

@st.cache_data(ttl=60)
def load_all_data():
    base_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet="
    try:
        df_tractor = pd.read_csv(base_url + TRACTOR_SHEET).fillna(0)
        df_attach = pd.read_csv(base_url + ATTACHMENT_SHEET).fillna(0)
        return df_tractor, df_attach
    except Exception as e:
        st.error(f"Data Load Error: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_tractor, df_attach = load_all_data()

if not df_tractor.empty:
    st.markdown("<h2 style='text-align: center; color: #ff6600;'>🚜 KMM Equipment & Attachments</h2>", unsafe_allow_html=True)
    
    # ၁။ စက်မော်ဒယ် ရွေးချယ်ခြင်း
    tractor_models = df_tractor.iloc[:, 0].astype(str).tolist()
    tractor_models = [m for m in tractor_models if m not in ["0", "0.0", "nan", "Model"]]
    
    selected_model = st.selectbox("စက်မော်ဒယ် ရွေးချယ်ပါ -", tractor_models)
    
    t_info = df_tractor[df_tractor.iloc[:, 0] == selected_model].iloc[0]
    
    try:
        raw_price = str(t_info.iloc[1]).replace(',', '').strip()
        base_price = float(raw_price) if raw_price != "" else 0
    except:
        base_price = 0
        
    img_url = str(t_info.iloc[2])

    if img_url and img_url.startswith("http"):
        st.image(img_url, caption=f"Model: {selected_model}", use_container_width=True)

    st.markdown(f"### 💰 စက်ဈေးနှုန်း: **{base_price:,.0f}** MMK")
    st.write("---")

    # ၂။ နောက်တွဲများ ရွေးချယ်ခြင်း
    st.subheader("🛠 ရရှိနိုင်သော နောက်တွဲများ")
    
    filtered_att = df_attach[df_attach.iloc[:, 0].astype(str) == selected_model]
    selected_att_total = 0
    
    def add_attachment_ui(label, m_col_name, p_col_name):
        if m_col_name in df_attach.columns and p_col_name in df_attach.columns:
            items = filtered_att[[m_col_name, p_col_name]].drop_duplicates()
            options = []
            for _, row in items.iterrows():
                m_name = str(row[m_col_name]).strip()
                m_price = row[p_col_name]
                if m_name not in ["0", "0.0", "nan"]:
                    options.append({"label": f"{m_name} (+{float(m_price):,.0f} MMK)", "price": float(m_price)})
            
            if options:
                choice = st.selectbox(f"{label} ရွေးရန်:", ["မယူပါ"] + [o["label"] for o in options])
                if choice != "မယူပါ":
                    return next(item["price"] for item in options if item["label"] == choice)
        return 0

    col1, col2 = st.columns(2)
    with col1:
        st.caption("🚜 Tractor Implements")
        selected_att_total += add_attachment_ui("Rotary", "Rotary_Model1", "Rotary_Price")
        selected_att_total += add_attachment_ui("Disc Harrow", "Harrow_Model1", "Harrow_Price")
        selected_att_total += add_attachment_ui("Disc Plow", "Plow_Model1", "Plow_Price")
        selected_att_total += add_attachment_ui("Combine Attach", "Combine_Model1", "Combine_Price")

    with col2:
        st.caption("🏗 Excavator & Others")
        selected_att_total += add_attachment_ui("Transplanter Attach", "Transplanter_Model1", "Transplanter_Price")
        selected_att_total += add_attachment_ui("Hydraulic Breaker", "Breaker_Model1", "Breaker_Price")

    # ၃။ စုစုပေါင်းတွက်ချက်ခြင်း
    grand_total = base_price + selected_att_total
    st.write("---")
    st.success(f"## 📄 စုစုပေါင်းကျသင့်ငွေ: {grand_total:,.0f} MMK")
    st.info(f"စက်ဈေး: {base_price:,.0f} | နောက်တွဲစုစုပေါင်း: {selected_att_total:,.0f}")

else:
    st.warning("Google Sheet မှ data ဖတ်မရဖြစ်နေပါသည်။")

st.markdown("<br><hr><center><small>© 2026 KMM Service Co., Ltd.</small></center>", unsafe_allow_html=True)
















