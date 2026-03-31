import streamlit as st
import pandas as pd

st.set_page_config(page_title="Multi-Brand Tractor Price List", page_icon="🚜", layout="centered")

# Google Sheet ID
SHEET_ID = "1QqQvPKH7G0hqqhd_0V6cP40Htl8qdFEZ6nHBVe_53_g"

# --- Sidebar အတွက် ကုမ္ပဏီရွေးချယ်မှု ---
st.sidebar.header("🚜 Brand Selection")
selected_brand = st.sidebar.selectbox(
    "အမှတ်တံဆိပ် ရွေးချယ်ပါ -", 
    ["Kubota", "Yanmar", "Win-Shwe-Wah(2nd)", "John-Deere", "New-Holland", "YTO", "Dongfeng", "Mahindra", "Yamabisi", "Sonalika"]
)

sheet_name = selected_brand

@st.cache_data(ttl=60)
def load_data(tab_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={tab_name}"
    try:
        df = pd.read_csv(url, header=None)
        temp_products = {}
        current_headers = {}
        image_col_idx = -1 

        for index, row in df.iterrows():
            # Header ရှာဖွေခြင်း (Model သို့မဟုတ် Image_Link ပါဝင်သော row ကို header အဖြစ်ယူမည်)
            row_values = [str(cell).strip() for cell in row]
            if "Model" in row_values or "Image_Link" in row_values:
                for col_idx, cell_val in enumerate(row):
                    val = str(cell_val).strip()
                    if "Image_Link" in val:
                        image_col_idx = col_idx
                    # _Price ပါတာရော၊ သာမန် Attachment ဈေးနှုန်းပါတာရောကို သိမ်းမယ်
                    if val and val != "nan" and col_idx > 1:
                        current_headers[col_idx] = val.replace("_Price", "").replace("Price", "").strip()
                continue 

            model_cell = str(row[0]).strip()
            if model_cell and model_cell not in ["nan", "0", "0.0", "", "Model"]:
                try:
                    price_val = str(row[1]).replace(',', '').strip()
                    base_p = float(price_val) if price_val != "" else 0
                except: base_p = 0
                
                # ပုံ Link ကို Column ကနေ ဆွဲယူမယ်
                img_url = str(row[image_col_idx]).strip() if image_col_idx != -1 else ""

                if base_p > 0:
                    # 'Image' key ထဲမှာ ပုံ link ကို သိမ်းမယ်
                    temp_products[model_cell] = {"Base_Price": base_p, "Image": img_url, "Attachments": {}}
                    for col_idx, cell_val in enumerate(row):
                        if col_idx in current_headers:
                            try:
                                clean_val = str(cell_val).replace(',', '').strip()
                                att_price = float(clean_val)
                                if att_price > 0:
                                    temp_products[model_cell]["Attachments"][current_headers[col_idx]] = att_price
                            except: continue
        return temp_products
    except: return {}

# --- 👇 ဒီနေရာမှာ load_data ကို ခေါ်ပေးဖို့ လိုပါတယ် 👇 ---
data = load_data(sheet_name)

# --- UI Display ---
if data:
    # ခေါင်းစဉ်ကို အလယ်မှာပြမယ်
    st.markdown(f"<h1 style='text-align: center; color: #333;'>🚜 {selected_brand} Price List</h1>", unsafe_allow_html=True)
    
    model_list = list(data.keys())
    selected_model = st.selectbox(f"{selected_brand} မော်ဒယ်ကို ရွေးပါ -", model_list)

    if selected_model:
        prod = data[selected_model]
        
        # မော်ဒယ်ပုံကို အရင်ပြမယ်
        if prod['Image'] and prod['Image'] != "nan" and prod['Image'] != "":
            st.image(prod['Image'], caption=f"{selected_brand} {selected_model}", use_container_width=True)
        
        st.markdown(f"### 💰 Base Price: **{prod['Base_Price']:,.0f}** MMK")
        st.write("---")
        
        att_dict = prod['Attachments']
        selected_atts_prices = []
        
        if att_dict:
            st.markdown("🔗 **Attachments (ဈေးနှုန်းကိုနှိပ်၍ ပေါင်းထည့်ပါ):**")
            for att, price in att_dict.items():
                is_selected = st.checkbox(f"➕ {att}", key=f"{selected_brand}_{selected_model}_{att}")
                if is_selected:
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp; 💹 {att}: <span style='color: #28a745; font-weight: bold;'>+{price:,.0f} MMK</span>", unsafe_allow_html=True)
                    selected_atts_prices.append(price)
                else:
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp; 🏷️ {att}: <span style='color: #666;'>+{price:,.0f} MMK</span>", unsafe_allow_html=True)
        
        total = prod['Base_Price'] + sum(selected_atts_prices)
        st.write("---")
        st.success(f"## 📄 Grand Total: {total:,.0f} Kyats")
else:
    st.warning(f"Google Sheet ထဲမှာ '{sheet_name}' ဆိုတဲ့ Tab ကို မတွေ့သေးပါဘူး။ Tab အသစ်ဆောက်ပြီး အချက်အလက်ဖြည့်ပေးပါခင်ဗျာ။")

st.markdown(f"<br><hr><center><small>© 2026 KMM {selected_brand}</small></center>", unsafe_allow_html=True)

















