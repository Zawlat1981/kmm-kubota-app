import streamlit as st # ဒီစာကြောင်းက အပေါ်ဆုံးမှာ ရှိရပါမယ်
import pandas as pd

st.set_page_config(page_title="Multi-Brand Tractor Price List", page_icon="🚜", layout="centered")

# Google Sheet ID
SHEET_ID = "1QqQvPKH7G0hqqhd_0V6cP40Htl8qdFEZ6nHBVe_53_g"

# ... (ကျန်တဲ့ sidebar code တွေ) ...

@st.cache_data(ttl=60)
def load_data(tab_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={tab_name}"
    try:
        df = pd.read_csv(url, header=None)
        temp_products = {}
        current_headers = {} 
        image_col_idx = -1 

        for index, row in df.iterrows():
            row_values = [str(cell).strip() for cell in row]
            
            # ၁။ Header (ခေါင်းစဉ်) အသစ်တွေ့ရင် Reset လုပ်မယ်
            if "Model" in row_values or "Image_Link" in row_values:
                current_headers = {} 
                for col_idx, cell_val in enumerate(row):
                    val = str(cell_val).strip()
                    if "Image_Link" in val:
                        image_col_idx = col_idx
                    if val and val != "nan" and col_idx > 1 and "Image_Link" not in val and "Base Price" not in val:
                        current_headers[col_idx] = val.replace("_Price", "").replace("Price", "").strip()
                continue 

            # ၂။ ဒေတာဖတ်ခြင်း
            model_cell = str(row[0]).strip()
            if model_cell in ["nan", "0", "0.0", "", "Model", "None"]:
                continue 

            # ၃။ Base Price ဖတ်ခြင်း
            try:
                price_val = str(row[1]).replace(',', '').strip()
                base_p = float(price_val) if price_val != "" else 0
            except:
                base_p = 0
            
            # ၄။ ပုံ Link ကို ဆွဲယူခြင်း
            img_url = ""
            if image_col_idx != -1 and image_col_idx < len(row):
                img_url = str(row[image_col_idx]).strip()

            # ဒေတာများကို Dictionary ထဲသို့ ထည့်သွင်းခြင်း
            if base_p > 0:
                temp_products[model_cell] = {"Base_Price": base_p, "Image": img_url, "Attachments": {}}
                for col_idx, cell_val in enumerate(row):
                    if col_idx in current_headers:
                        try:
                            clean_val = str(cell_val).replace(',', '').strip()
                            att_price = float(clean_val)
                            if att_price > 0:
                                header_name = current_headers[col_idx]
                                temp_products[model_cell]["Attachments"][header_name] = att_price
                        except:
                            continue
        return temp_products
    except Exception as e:
        return {}

# ... (အောက်က UI code တွေ ပုံမှန်အတိုင်း ပြန်ထည့်ပါ) ...

















