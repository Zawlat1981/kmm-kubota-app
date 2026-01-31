import streamlit as st
import pandas as pd

st.set_page_config(page_title="KMM Kubota Official Catalog", page_icon="🚜", layout="wide")

# --- CONFIG ---
CORRECT_PASSWORD = "kmm111" 
SHEET_ID = "1QqQvPKH7G0hqqhd_0V6cP40Htl8qdFEZ6nHBVe_53_g"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=300)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL, header=None)
        temp_products = {}
        current_headers = {}
        image_mapping = {}
        for index, row in df.iterrows():
            model_cell = str(row[0]).strip()
            if "Model" in model_cell or any("_Price" in str(cell) for cell in row):
                for col_idx, cell_val in enumerate(row):
                    val = str(cell_val).strip()
                    if val and val != "nan":
                        current_headers[col_idx] = val.replace("_Price", "").replace("Price", "").strip()
                continue
            if model_cell and model_cell not in ["nan", "0", "0.0", ""]:
                try:
                    price_val = str(row[1]).replace(',', '').strip()
                    base_p = float(price_val) if price_val != "" else 0
                except: base_p = 0
                temp_products[model_cell] = {"Base_Price": base_p, "Attachments": {}}
                for col_idx, cell_val in enumerate(row):
                    if col_idx <= 1: continue
                    header_name = current_headers.get(col_idx, "")
                    if "Image" in header_name:
                        image_mapping[model_cell] = str(cell_val).strip()
                        continue
                    try:
                        clean_val = str(cell_val).replace(',', '').strip()
                        if clean_val and clean_val not in ["nan", "0", "0.0"]:
                            att_price = float(clean_val)
                            temp_products[model_cell]["Attachments"][header_name] = att_price
                    except: continue
        return temp_products, image_mapping
    except: return {}, {}

# --- UI START ---
st.markdown("<h1 style='text-align: center; color: #FF6600;'>🚜 KMM Kubota Product Catalog</h1>", unsafe_allow_html=True)

# --- SIDEBAR: CONTACT INFO (PASSWORD မလိုပါ) ---
st.sidebar.header("📞 Contact Centers")
with st.sidebar.expander("🏢 Sale Offices"):
    st.write("**Hpa-An:** 09755499997")
    st.write("**Mawlamyine:** 09788880890")
    st.write("**Tharyarwaddy:** 09789998484")
    st.write("**Nattalin:** 09751666604")

with st.sidebar.expander("⚙️ Spare Part Centers"):
    st.write("**Hpa-An:** 09780866048")
    st.write("**Mawlamyine:** 09768170065")
    st.write("**Tharyarwaddy:** 09795126031")

with st.sidebar.expander("🛠️ Service Centers"):
    st.write("**Hpa-An:** 09767646506")
    st.write("**Mawlamyine:** 09769772629, 09760460349")
    st.write("**Tharyarwaddy:** 09775298175")

st.sidebar.write("---")

data, images = load_data()

if data:
    model_list = list(data.keys())
    st.sidebar.subheader("🔍 Search & Filter")
    selected_model = st.sidebar.selectbox("Product Model ကိုရွေးပါ -", model_list)

    st.sidebar.write("---")
    show_price_mode = st.sidebar.checkbox("💰 Show Prices & Calculate (Staff Only)")

    if selected_model:
        prod = data[selected_model]
        img_url = images.get(selected_model, "")
        col1, col2 = st.columns([1.2, 1])

        with col1:
            if img_url and img_url != "nan":
                st.image(img_url, caption=f"Kubota {selected_model}", use_container_width=True)
            else:
                st.info("📷 ပုံထည့်သွင်းရန် ပြင်ဆင်နေဆဲ...")

        with col2:
            st.header(f"Kubota {selected_model}")
            
            if show_price_mode:
                if "authenticated" not in st.session_state:
                    st.session_state["authenticated"] = False
                
                if not st.session_state["authenticated"]:
                    pwd_input = st.text_input("ဈေးနှုန်းကြည့်ရန် Password ရိုက်ထည့်ပါ -", type="password")
                    if st.button("Unlock Prices"):
                        if pwd_input == CORRECT_PASSWORD:
                            st.session_state["authenticated"] = True
                            st.rerun()
                        else:
                            st.error("❌ Password မှားယွင်းနေပါသည်။")
                else:
                    st.markdown(f"### 💰 Base Price: **{prod['Base_Price']:,.0f}** Ks")
                    att_dict = prod['Attachments']
                    selected_atts_prices = []
                    if att_dict:
                        st.write("---")
                        st.write("🔧 **Attachments ပေါင်းထည့်ရန်:**")
                        for att, price in att_dict.items():
                            if st.checkbox(f"{att} (+{price:,.0f} Ks)", key=f"p_{selected_model}_{att}"):
                                selected_atts_prices.append(price)
                    total = prod['Base_Price'] + sum(selected_atts_prices)
                    st.write("---")
                    st.success(f"## 📑 Grand Total: {total:,.0f} Kyats")
                    if st.button("Lock Prices 🔒"):
                        st.session_state["authenticated"] = False
                        st.rerun()
            else:
                st.info("ℹ️ ဈေးနှုန်းနှင့် တွက်ချက်မှုများ သိရှိလိုပါက Sidebar ရှိ 'Show Prices' ကို နှိပ်ပါ။")
                st.write("---")
                st.write(f"**Selected Model:** {selected_model}")
                st.write("ကျွန်ုပ်တို့၏ အရောင်းပြခန်းများတွင် စမ်းသပ်မောင်းနှင်ကြည့်ရှုနိုင်ပါသည်။")

st.markdown("<br><hr><center><small>© 2024 KMM Kubota | All Rights Reserved</small></center>", unsafe_allow_html=True)


