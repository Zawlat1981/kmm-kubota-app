import streamlit as st
import pandas as pd

st.set_page_config(page_title="KMM Kubota Official Catalog", page_icon="🚜", layout="wide")

SHEET_ID = "1QqQvPKH7G0hqqhd_0V6cP40Htl8qdFEZ6nHBVe_53_g"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=300)
def load_data():
    try:
        # Header မပါဘဲ ဖတ်ပြီး Dynamic Header Logic သုံးပါမည်
        df = pd.read_csv(SHEET_URL, header=None)
        temp_products = {}
        current_headers = {}
        image_mapping = {} # ပုံ Link များသိမ်းရန်

        for index, row in df.iterrows():
            model_cell = str(row[0]).strip()
            
            # Header Row ရှာဖွေခြင်း
            if "Model" in model_cell or any("_Price" in str(cell) for cell in row):
                for col_idx, cell_val in enumerate(row):
                    val = str(cell_val).strip()
                    if val and val != "nan":
                        current_headers[col_idx] = val.replace("_Price", "").replace("Price", "").strip()
                continue

            # Data Row ဖတ်ခြင်း
            if model_cell and model_cell not in ["nan", "0", "0.0", ""]:
                try:
                    price_val = str(row[1]).replace(',', '').strip()
                    base_p = float(price_val) if price_val != "" else 0
                except: base_p = 0
                
                if base_p > 0:
                    temp_products[model_cell] = {"Base_Price": base_p, "Attachments": {}}
                    for col_idx, cell_val in enumerate(row):
                        if col_idx <= 1: continue
                        
                        # Image URL ရှာဖွေခြင်း (Column နာမည် Image_URL ဖြစ်ရပါမည်)
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

# --- UI ပိုင်း ---
st.markdown("<h1 style='text-align: center; color: #FF6600;'>🚜 KMM Kubota Product Catalog</h1>", unsafe_allow_html=True)
data, images = load_data()

if data:
    model_list = list(data.keys())
    # Sidebar တွင် Model ရွေးရန် ထားပါမည်
    st.sidebar.header("🔍 Search & Filter")
    selected_model = st.sidebar.selectbox("Product Model ကိုရွေးပါ -", model_list)

    if selected_model:
        prod = data[selected_model]
        img_url = images.get(selected_model, "")

        # Layout နှစ်ခြမ်းခွဲခြင်း
        col1, col2 = st.columns([1.2, 1])

        with col1:
            if img_url and img_url != "nan":
                st.image(img_url, caption=f"Kubota {selected_model}", use_container_width=True)
            else:
                st.info("📷 ပုံထည့်သွင်းရန် ပြင်ဆင်နေဆဲ...")
            
            # ဆက်သွယ်ရန် ခလုတ်များ
            st.write("---")
            st.write("📞 **ဆက်သွယ်ရန်:**")
            st.link_button("☎️ Call Now: 09-xxxxxxxxx", "tel:09xxxxxxxxx")
            st.link_button("💬 Chat on Messenger", "https://m.me/yourpage")

        with col2:
            st.header(f"Kubota {selected_model}")
            st.markdown(f"### 💰 Base Price: **{prod['Base_Price']:,.0f}** Ks")
            
            att_dict = prod['Attachments']
            selected_atts_prices = []
            
            if att_dict:
                st.write("---")
                st.write("🔧 **Attachments ပေါင်းထည့်ရန်:**")
                for att, price in att_dict.items():
                    if st.checkbox(f"{att} (+{price:,.0f} Ks)", key=f"v2_{selected_model}_{att}"):
                        selected_atts_prices.append(price)
            
            total = prod['Base_Price'] + sum(selected_atts_prices)
            st.write("---")
            st.success(f"## 📑 Grand Total: {total:,.0f} Kyats")

# Footer
st.markdown("<br><hr><center><small>© 2024 KMM Kubota | All Rights Reserved</small></center>", unsafe_allow_html=True)








