import streamlit as st
import pandas as pd

# ၁။ Page Config နှင့် ခေါင်းစဉ်ကို ပြောင်းလဲခြင်း
st.set_page_config(page_title="KMM Kubota Price List", page_icon="🚜", layout="centered")

# Google Sheet ID
SHEET_ID = "1QqQvPKH7G0hqqhd_0V6cP40Htl8qdFEZ6nHBVe_53_g"

# --- Sidebar အတွက် ကုမ္ပဏီရွေးချယ်မှု ---
st.sidebar.header("🚜 Brand Selection")
selected_brand = st.sidebar.selectbox(
    "အမှတ်တံဆိပ် ရွေးချယ်ပါ -", 
    ["Kubota", "Yanmar", "Win-Shwe-Wah(2nd)", "John-Deere", "New-Holland", "YTO", "Mahindra", "Sonalika", "Yamabisi", "DongFeng"]
)

# နောက်တွဲများအတွက် သီးသန့် Tab နာမည်
ATTACHMENT_SHEET = "Attachments_List"

@st.cache_data(ttl=60)
def load_data(tab_name):
    base_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet="
    try:
        # ရွေးထားတဲ့ Brand ရဲ့ စက်ပစ္စည်းစာရင်းကို ဖတ်မယ်
        df_tractor = pd.read_csv(base_url + tab_name).fillna(0)
        # နောက်တွဲစာရင်းကို ဖတ်မယ်
        df_attach = pd.read_csv(base_url + ATTACHMENT_SHEET).fillna(0)
        return df_tractor, df_attach
    except Exception as e:
        st.error(f"Data Load Error: {e}")
        return pd.DataFrame(), pd.DataFrame()

# ဒေတာများကို Load လုပ်ခြင်း
df_tractor, df_attach = load_data(selected_brand)

if not df_tractor.empty:
    # ၁။ ခေါင်းစဉ်
    st.markdown("<h1 style='text-align: center; color: #ff6600;'>🚜 KMM Kubota Price List</h1>", unsafe_allow_html=True)

    # ၂။ နိုင်ငံအမည် သတ်မှတ်ခြင်း (တစ်ကြိမ်ပဲ ရေးဖို့ လိုပါတယ်)
    if selected_brand in ["John-Deere", "New-Holland", "Mahindra", "Sonalika"]:
        origin = "Indian"
    elif selected_brand in ["YTO", "Yamabisi", "DongFeng"]:
        origin = "China"
    elif selected_brand == "Kubota":
        origin = "Japan/Thailand"
    elif selected_brand == "Yanmar":
        origin = "Japan"
    else:
        origin = ""

    # ၃။ စာသားကို ပြသခြင်း (Brand အမည် နှင့် နိုင်ငံ)
    display_text = f"({selected_brand} Brand - {origin})" if origin else f"({selected_brand} Brand)"
    st.markdown(f"<p style='text-align: center; color: #555; font-weight: bold;'>{display_text}</p>", unsafe_allow_html=True)
    
    st.write("---") # မျဉ်းတားလေးတစ်ခု ထည့်လိုက်ရင် ပိုကြည့်ကောင်းပါတယ်

    # ၄။ စက်မော်ဒယ် ရွေးချယ်ခြင်း
    model_list = df_tractor.iloc[:, 0].astype(str).tolist()
    model_list = [m for m in model_list if m not in ["0", "0.0", "nan", "Model"]]
    
    selected_model = st.selectbox(f"{selected_brand} မော်ဒယ်ကို ရွေးပါ -", model_list)
    
    # ... (ကျန်တဲ့ code အပိုင်းတွေ ဆက်သွားပါမယ်) ...
    
    t_info = df_tractor[df_tractor.iloc[:, 0] == selected_model].iloc[0]
    
    # ဈေးနှုန်းနှင့် ပုံ
    try:
        raw_p = str(t_info.iloc[1]).replace(',', '').strip()
        base_price = float(raw_p) if raw_p != "" else 0
    except:
        base_price = 0
    img_url = str(t_info.iloc[2])

    if img_url and img_url.startswith("http"):
        st.image(img_url, use_container_width=True)

    st.markdown(f"### 💰 စက်ဈေးနှုန်း: **{base_price:,.0f}** MMK")
    st.write("---")

    # ၄။ နောက်တွဲများ ရွေးချယ်ရန်
    st.subheader("🛠 နောက်တွဲများ ရွေးချယ်ရန်")
    filtered_att = df_attach[df_attach.iloc[:, 0].astype(str) == selected_model]
    
    selected_att_total = 0
    
    def add_att_ui(label, m_col, p_col):
        if m_col in df_attach.columns:
            items = filtered_att[[m_col, p_col]].drop_duplicates()
            options = []
            for _, row in items.iterrows():
                if str(row[m_col]) not in ["0", "0.0", "nan"]:
                    options.append({"label": f"{row[m_col]} (+{float(row[p_col]):,.0f} MMK)", "price": float(row[p_col])})
            if options:
                c = st.selectbox(f"{label}:", ["မယူပါ"] + [o["label"] for o in options])
                if c != "မယူပါ":
                    return next(item["price"] for item in options if item["label"] == c)
        return 0

    col1, col2 = st.columns(2)
    with col1:
        st.caption("🚜 Tractor Implements")
        selected_att_total += add_att_ui("Rotary", "Rotary_Model1", "Rotary_Price")
        selected_att_total += add_att_ui("Disc Harrow", "Harrow_Model1", "Harrow_Price")
        selected_att_total += add_att_ui("Disc Plow", "Plow_Model1", "Plow_Price")
        selected_att_total += add_att_ui("Combine Harvester Attach", "Combine_Model1", "Combine_Price")

    with col2:
        st.caption("🏗 Excavator & Others")
        selected_att_total += add_att_ui("Hydraulic Breaker", "Breaker_Model1", "Breaker_Price")
        selected_att_total += add_att_ui("Sowing/Transplanter", "Transplanter_Model1", "Transplanter_Price")

    # ၅။ စုစုပေါင်း
    grand_total = base_price + selected_att_total
    st.write("---")
    st.success(f"## 📄 စုစုပေါင်းကျသင့်ငွေ: {grand_total:,.0f} MMK")
    st.info(f"စက်ဈေး: {base_price:,.0f} + နောက်တွဲ: {selected_att_total:,.0f}")
else:
    st.warning(f"Google Sheet ထဲမှာ '{selected_brand}' ဆိုတဲ့ Tab ကို မတွေ့ပါဘူး။ Tab အမည်ကို ပြန်စစ်ပေးပါ။")

st.markdown("<br><hr><center><small>© 2026 KMM Service Co., Ltd.</small></center>", unsafe_allow_html=True)
















