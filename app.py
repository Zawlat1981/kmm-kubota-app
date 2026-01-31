import streamlit as st
import pandas as pd

st.set_page_config(page_title="KMM Kubota Price List", page_icon="🚜", layout="centered")

# Google Sheet ID
SHEET_ID = "1QqQvPKH7G0hqqhd_0V6cP40Htl8qdFEZ6nHBVe_53_g"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL, header=None)
        temp_products = {}
        current_headers = {}

        for index, row in df.iterrows():
            model_cell = str(row[0]).strip()
            
            # Header Row ကို ခွဲခြားခြင်း
            if "Model" in model_cell or "_Price" in str(row[2]):
                current_headers = {} # Header အဟောင်းကို ဖျက်ပြီး အသစ်ပြန်မှတ်ပါ
                for col_idx, cell_val in enumerate(row):
                    val = str(cell_val).strip()
                    if val and val != "nan" and col_idx > 1:
                        current_headers[col_idx] = val.replace("_Price", "").replace("Price", "").strip()
                continue

            # Data Row (Model အမည်ပါသော Row)
            if model_cell and model_cell not in ["nan", "0", "0.0", ""]:
                try:
                    price_val = str(row[1]).replace(',', '').strip()
                    base_p = float(price_val) if price_val != "" else 0
                except: base_p = 0
                
                if base_p > 0:
                    temp_products[model_cell] = {"Base_Price": base_p, "Attachments": {}}
                    for col_idx, cell_val in enumerate(row):
                        if col_idx in current_headers:
                            try:
                                clean_val = str(cell_val).replace(',', '').strip()
                                att_price = float(clean_val)
                                # ဈေးနှုန်း 0 ထက်ကြီးသော Attachment ကိုသာ ထည့်ပါ
                                if att_price > 0:
                                    header_name = current_headers[col_idx]
                                    temp_products[model_cell]["Attachments"][header_name] = att_price
                            except: continue
        return temp_products
    except: return {}

# --- UI ပိုင်း ---
st.markdown("<h1 style='text-align: center;'>🚜 KMM Kubota Price List</h1>", unsafe_allow_html=True)

data = load_data()

if data:
    model_list = list(data.keys())
    selected_model = st.selectbox("Product Model ကိုရွေးပါ -", model_list)

    if selected_model:
        prod = data[selected_model]
        st.markdown(f"## 💰 Base Price: {prod['Base_Price']:,.0f} Ks")
        
        st.write("---")
        att_dict = prod['Attachments']
        selected_atts_prices = []
        
        if att_dict:
            st.write("🔗 **Attachments ပေါင်းထည့်ရန်:**")
            for att, price in att_dict.items():
                # တစ်ခုချင်းစီအတွက် Checkbox ပြခြင်း
                if st.checkbox(f"{att} (+{price:,.0f} Ks)", key=f"calc_{selected_model}_{att}"):
                    selected_atts_prices.append(price)
        else:
            st.info("ဤ Model အတွက် ထပ်တိုး Attachment များ မရှိပါ။")
            
        total = prod['Base_Price'] + sum(selected_atts_prices)
        st.write("---")
        st.success(f"### 📑 Grand Total: {total:,.0f} Kyats")

st.markdown("<br><hr><center><small>© 2024 KMM Kubota</small></center>", unsafe_allow_html=True)












