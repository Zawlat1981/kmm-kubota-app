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
            # စာသားများကို သန့်စင်ရန်
            row_values = [str(cell).strip() for cell in row]
            
            # ၁။ Header (ခေါင်းစဉ်) ရှာဖွေခြင်း
            if "Model" in row_values or "Image_Link" in row_values:
                for col_idx, cell_val in enumerate(row):
                    val = str(cell_val).strip()
                    if "Image_Link" in val:
                        image_col_idx = col_idx
                    # Attachment ခေါင်းစဉ်များကို သိမ်းဆည်းခြင်း
                    if val and val != "nan" and col_idx > 1 and "Image_Link" not in val:
                        current_headers[col_idx] = val.replace("_Price", "").replace("Price", "").strip()
                continue 

            # ၂။ ဒေတာဖတ်ခြင်း (Model အမည်ကို စစ်ဆေးခြင်း)
            model_cell = str(row[0]).strip()
            
            # Model နေရာမှာ 0 ဖြစ်နေရင် ဒါမှမဟုတ် အလွတ်ဖြစ်နေရင် ကျော်သွားမယ်
            if model_cell in ["nan", "0", "0.0", "", "Model"]:
                continue 

            # ၃။ Base Price ဖတ်ခြင်း
            try:
                price_val = str(row[1]).replace(',', '').strip()
                base_p = float(price_val) if price_val != "" else 0
            except:
                base_p = 0
            
            # ၄။ ပုံ Link ကို ဆွဲယူခြင်း
            img_url = ""
            if image_col_idx != -1:
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
                                temp_products[model_cell]["Attachments"][current_headers[col_idx]] = att_price
                        except:
                            continue
        return temp_products
    except Exception as e:
        return {}

# ဒေတာများကို စတင် Load လုပ်ခြင်း
data = load_data(sheet_name)

# --- UI Display အပိုင်း ---
if data:
    st.markdown(f"<h1 style='text-align: center; color: #333;'>🚜 {selected_brand} Price List</h1>", unsafe_allow_html=True)
    
    model_list = list(data.keys())
    selected_model = st.selectbox(f"{selected_brand} မော်ဒယ်ကို ရွေးပါ -", model_list)

    if selected_model:
        prod = data[selected_model]
        
        # မော်ဒယ်ပုံကို ပြသခြင်း
        img_url = prod['Image']
        if img_url and img_url != "nan" and img_url != "0" and img_url.startswith("http"):
            st.image(img_url, caption=f"{selected_brand} {selected_model}", use_container_width=True)
        
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
    st.warning(f"Google Sheet ထဲမှာ '{sheet_name}' ဆိုတဲ့ Tab ကို မတွေ့သေးပါဘူး (သို့မဟုတ်) ဒေတာဖတ်လို့ မရဖြစ်နေပါတယ်။ Tab အသစ်ဆောက်ပြီး အချက်အလက်ဖြည့်ပေးပါခင်ဗျာ။")

st.markdown(f"<br><hr><center><small>© 2026 KMM {selected_brand}</small></center>", unsafe_allow_html=True)

















