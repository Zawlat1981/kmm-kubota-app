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
            
            # ခေါင်းစဉ် (Header) ကို ရှာဖွေခြင်း (Row 1 သို့မဟုတ် Row 4 အတွက်)
            # Row 4 မှာ "DH225E_Price" ရှိနေတာကို ဖမ်းယူဖို့
            if "Model" in model_cell or any("_Price" in str(cell) for cell in row):
                current_headers = {}
                for col_idx, cell_val in enumerate(row):
                    val = str(cell_val).strip()
                    if val and val != "nan" and col_idx > 1:
                        # "_Price" သို့မဟုတ် "Price" ကို ဖယ်ထုတ်ပြီး Attachment နာမည်ယူခြင်း
                        header_name = val.replace("_Price", "").replace("Price", "").strip()
                        current_headers[col_idx] = header_name
                continue
            
            # Model အမည် ရှိမရှိ စစ်ဆေးခြင်း
            if model_cell and model_cell not in ["nan", "0", "0.0", "", "Model"]:
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
                                # ဈေးနှုန်း 0 ထက်ကြီးမှ Attachment စာရင်းထဲ ထည့်မယ်
                                if att_price > 0:
                                    header_name = current_headers[col_idx]
                                    temp_products[model_cell]["Attachments"][header_name] = att_price
                            except: continue
        return temp_products
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return {}  

# --- UI ---
st.markdown("<h1 style='text-align: center; color: #333;'>🚜 KMM Kubota Price List</h1>", unsafe_allow_html=True)

data = load_data()

if data:
    model_list = list(data.keys())
    selected_model = st.selectbox("Product Model ကိုရွေးပါ -", model_list)

    if selected_model:
        prod = data[selected_model]
        # Base Price ပြသခြင်း
        st.markdown(f"### 💰 Base Price: **{prod['Base_Price']:,.0f}** MMK")
        
        st.write("---")
        att_dict = prod['Attachments']
        selected_atts_prices = []
        
        if att_dict:
            st.markdown("🔗 **Attachments (ဈေးနှုန်းကိုနှိပ်၍ ပေါင်းထည့်ပါ):**")
            for att, price in att_dict.items():
                # Checkbox ကို သုံးသော်လည်း စာသားအရောင်ကို ခွဲခြားရန် Logic
                # Checkbox state ကို စစ်ဆေးခြင်း
                is_selected = st.checkbox(f"➕ {att}", key=f"final_{selected_model}_{att}")
                
                if is_selected:
                    # ရွေးချယ်ပြီးပါက ဈေးနှုန်းကို အစိမ်းရောင် (Bold) ဖြင့်ပြရန်
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp; 💹 {att} Price: <span style='color: #28a745; font-weight: bold;'>+{price:,.0f} MMK</span> (Added)", unsafe_allow_html=True)
                    selected_atts_prices.append(price)
                else:
                    # မရွေးရသေးပါက ဈေးနှုန်းကို မီးခိုးရောင် သို့မဟုတ် အဖြူရောင်ဘောင်ထဲတွင်ပြရန်
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp; 🏷️ {att} Price: <span style='color: #666;'>+{price:,.0f} MMK</span>", unsafe_allow_html=True)
        
        total = prod['Base_Price'] + sum(selected_atts_prices)
        st.write("---")
        
        # Grand Total အကွက် (လူကြီးမင်းပို့ထားသည့်ပုံစံအတိုင်း အစိမ်းရောင် Highlight)
        st.success(f"## 📄 Grand Total: {total:,.0f} Kyats")

st.markdown("<br><hr><center><small>© 2024 KMM Kubota</small></center>", unsafe_allow_html=True)
















