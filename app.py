import streamlit as st
import pandas as pd

# Browser Layout သတ်မှတ်ခြင်း
st.set_page_config(page_title="KMM Kubota Price List", page_icon="🚜", layout="centered")

# Google Sheet Link
SHEET_ID = "1QqQvPKH7G0hqqhd_0V6cP40Htl8qdFEZ6nHBVe_53_g"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=300)
def load_data():
    try:
        # Header မပါဘဲ အရင်ဖတ်ကြည့်မည်
        df = pd.read_csv(SHEET_URL, header=None)
        
        # 'Model' နှင့် 'Base Price' ပါသော Row ကို ရှာဖွေခြင်း
        header_row_index = 0
        for i, row in df.iterrows():
            if "Model" in str(row[0]) and "Base Price" in str(row[1]):
                header_row_index = i
                break
        
        # ရှာတွေ့သော Row ကို Header အဖြစ် သတ်မှတ်၍ Data ပြန်ဖတ်ခြင်း
        df = pd.read_csv(SHEET_URL, skiprows=header_row_index)
        
        temp_products = {}
        last_model_name = None 
        
        for index, row in df.iterrows():
            model_val = str(row['Model']).strip()
            # Model အမည်အသစ်တွေ့လျှင် မှတ်ထားမည်
            if pd.notna(row['Model']) and model_val not in ["", "0", "nan", "0.0"]:
                last_model_name = model_val
            
            if last_model_name:
                try:
                    # Base Price ကို ဂဏန်းအဖြစ် ပြောင်းလဲခြင်း
                    price_str = str(row['Base Price']).replace(',', '').strip()
                    base_p = float(price_str) if price_str not in ["", "nan"] else 0
                except: base_p = 0
                
                if base_p > 0:
                    if last_model_name not in temp_products:
                        temp_products[last_model_name] = {"Base_Price": base_p, "Attachments": {}}
                    
                    # Attachment များကို ရှာဖွေခြင်း
                    for col in df.columns:
                        if col in ['Base Price', 'Model']: continue
                        try:
                            p_val = row[col]
                            if pd.notna(p_val) and str(p_val).strip() not in ["", "0", "0.0", "nan"]:
                                price = float(str(p_val).replace(',', '').strip())
                                # အပေါ်ကို တက်ရှာသော Logic
                                clean_n = str(col).strip()
                                if "Price" not in clean_n:
                                    for r_idx in range(index, -1, -1):
                                        cell_text = str(df.iloc[r_idx][col]).strip()
                                        if "Price" in cell_text:
                                            clean_n = cell_text
                                            break
                                final_name = clean_n.replace('_Price','').replace('Price','').strip()
                                temp_products[last_model_name]["Attachments"][final_name] = price
                        except: continue
        return temp_products
    except Exception as e:
        st.error(f"Error: {e}")
        return {}

# UI ပိုင်း
st.title("🚜 KMM Kubota Price List")

data = load_data()
if not data:
    st.warning("Data မရှိသေးပါ။ Google Sheet တွင် 'Model' နှင့် 'Base Price' Column Header များ ရှိမရှိ စစ်ဆေးပါဗျာ။")
else:
    model_list = list(data.keys())
    selected_model = st.selectbox("Product Model ကိုရွေးပါ -", ["-- ရွေးချယ်ရန် --"] + model_list)

    if selected_model != "-- ရွေးချယ်ရန် --":
        prod = data[selected_model]
        st.markdown(f"### 💰 Base Price: **{prod['Base_Price']:,.0f}** Ks")
        
        att_dict = prod['Attachments']
        selected_atts = []
        
        if att_dict:
            st.write("---")
            st.write("🔧 **Attachments ပေါင်းထည့်ရန်:**")
            for att, price in att_dict.items():
                if st.checkbox(f"{att} (+{price:,.0f} Ks)"):
                    selected_atts.append((att, price))
        
        total = prod['Base_Price'] + sum(p for n, p in selected_atts)
        st.write("---")
        st.success(f"### 📑 Grand Total: {total:,.0f} Kyats")