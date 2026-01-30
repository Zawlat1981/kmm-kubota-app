import streamlit as st
import pandas as pd

st.set_page_config(page_title="KMM Kubota Price List", page_icon="🚜", layout="centered")

SHEET_ID = "1QqQvPKH7G0hqqhd_0V6cP40Htl8qdFEZ6nHBVe_53_g"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=300)
def load_data():
    try:
        # Header မပါဘဲ အရင်ဖတ်ပြီး Data Clean လုပ်ပါမည်
        df = pd.read_csv(SHEET_URL, header=None)
        
        temp_products = {}
        # လက်ရှိ Row တစ်ခုချင်းစီအတွက် အသုံးပြုမယ့် Dynamic Column Names (Attachment နာမည်များ)
        current_headers = {}

        for index, row in df.iterrows():
            model_cell = str(row[0]).strip()
            
            # ၁။ အကယ်၍ Row ထဲမှာ "Model" သို့မဟုတ် "Price" ဆိုတဲ့ စာသားပါနေရင် Header အသစ်လို့ သတ်မှတ်မယ်
            if "Model" in model_cell or any("_Price" in str(cell) for cell in row):
                for col_idx, cell_val in enumerate(row):
                    val = str(cell_val).strip()
                    if val and val != "nan":
                        current_headers[col_idx] = val.replace("_Price", "").replace("Price", "").strip()
                continue

            # ၂။ Model အမည်ရှိပြီး Base Price ရှိသော Row ကို ရှာမယ်
            if model_cell and model_cell not in ["nan", "0", "0.0", ""]:
                try:
                    price_val = str(row[1]).replace(',', '').strip()
                    base_p = float(price_val) if price_val != "" else 0
                except: base_p = 0
                
                if base_p > 0:
                    temp_products[model_cell] = {"Base_Price": base_p, "Attachments": {}}
                    
                    # ၃။ ကျန်တဲ့ Column တွေထဲက Attachment တန်ဖိုးတွေကို Header နာမည်နဲ့ သိမ်းမယ်
                    for col_idx, cell_val in enumerate(row):
                        if col_idx <= 1: continue # Model နဲ့ Base Price ကို ကျော်မယ်
                        
                        try:
                            clean_val = str(cell_val).replace(',', '').strip()
                            if clean_val and clean_val not in ["nan", "0", "0.0"]:
                                att_price = float(clean_val)
                                att_name = current_headers.get(col_idx, f"Attachment {col_idx}")
                                temp_products[model_cell]["Attachments"][att_name] = att_price
                        except:
                            continue
        return temp_products
    except Exception as e:
        st.error(f"Error: {e}")
        return {}

# --- UI ပိုင်း ---
st.title("🚜 KMM Kubota Price List")
data = load_data()

if not data:
    st.warning("Data ဖတ်မရဖြစ်နေပါသည်။ Sheet ထဲတွင် Model ဇယားများ ရှိမရှိ စစ်ဆေးပါ။")
else:
    model_list = list(data.keys())
    selected_model = st.selectbox("Product Model ကိုရွေးပါ -", ["-- ရွေးချယ်ရန် --"] + model_list)

    if selected_model != "-- ရွေးချယ်ရန် --":
        prod = data[selected_model]
        st.markdown(f"### 💰 Base Price: **{prod['Base_Price']:,.0f}** MMK")
        
        att_dict = prod['Attachments']
        selected_atts_prices = []
        
        if att_dict:
            st.write("---")
            st.write("🔧 **Attachments ပေါင်းထည့်ရန်:**")
            for att, price in att_dict.items():
                if st.checkbox(f"{att} (+{price:,.0f} MMK)", key=f"{selected_model}_{att}"):
                    selected_atts_prices.append(price)
        
        total = prod['Base_Price'] + sum(selected_atts_prices)
        st.write("---")
        st.success(f"### 📑 Grand Total: {total:,.0f} MMK")

