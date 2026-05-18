import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime

# ==========================================
# ၁။ PAGE CONFIG & CONSTANTS
# ==========================================
st.set_page_config(page_title="KMM Kubota Price List", page_icon="🚜", layout="centered")

# Google Sheet ID (ထွန်စက်ဈေးနှုန်းအတွက်)
SHEET_ID = "1QqQvPKH7G0hqqhd_0V6cP40Htl8qdFEZ6nHBVe_53_g"

# Notion Configuration
NOTION_TOKEN = "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"
DATABASE_ID = "2e19e825888681b38bd4cc8fc5233ceb"

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# ==========================================
# ၂။ SIDEBAR MENU
# ==========================================
with st.sidebar:
    st.markdown("## 🚜 KMM Service")
    menu_choice = st.radio("သွားလိုရာကို ရွေးချယ်ပါ (กรุณาเลือกเมนู) -", ["Brand Selection", "Competitor News Updates"])
    st.write("---")
    
    if menu_choice == "Brand Selection":
        st.header("🔍 Filter")
        selected_brand = st.selectbox(
            "အမှတ်တံဆိပ် ရွေးချယ်ပါ (กรุณาเลือกยี่ห้อ) -", 
            ["Kubota", "Yanmar", "Win-Shwe-Wah(2nd)", "John-Deere", "New-Holland", "YTO", "Mahindra", "Sonalika", "Yamabisi", "DongFeng"]
        )

# ==========================================
# ၃။ FUNCTIONS (DATA LOAD & FETCH NOTION NEWS DIRECTLY)
# ==========================================
@st.cache_data(ttl=60)
def load_data(tab_name):
    base_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet="
    try:
        df_tractor = pd.read_csv(base_url + tab_name).fillna(0)
    except:
        df_tractor = pd.DataFrame()
    
    df_attach = pd.DataFrame()
    if tab_name in ["Kubota", "Yanmar"]:
        attachment_tab = f"Attachments_{tab_name}"
        try:
            df_attach = pd.read_csv(base_url + attachment_tab).fillna(0)
        except:
            pass
    return df_tractor, df_attach

def fetch_notion_news_with_images():
    """ Notion ထဲ တိုက်ရိုက်တင်ထားတဲ့ ပုံတွေရော၊ စာတွေကိုပါ တိုက်ရိုက်ဆွဲထုတ်ပေးမည့် Function """
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    # ရက်စွဲအလိုက် အသစ်ဆုံးကို ထိပ်ဆုံးကပြရန်
    payload = {
        "sorts": [
            {"property": "Date", "direction": "descending"}
        ]
    }
    
    try:
        res = requests.post(url, headers=NOTION_HEADERS, json=payload).json()
        notion_items = []
        
        for page in res.get("results", []):
            page_id = page["id"]
            props = page.get("properties", {})
            
            # ၁။ ရက်စွဲယူခြင်း
            date_val = props.get("Date", {}).get("date")
            item_date = date_val.get("start", "No Date") if date_val else "No Date"
            
            # ၂။ ခေါင်းစဉ် (ဗမာလို) ယူခြင်း
            title_list = props.get("Name", {}).get("title", [])
            item_title = title_list[0].get("text", {}).get("content", "No Title") if title_list else "No Title"
            
            # ၃။ စာမျက်နှာအထဲက 'စာသား' နှင့် 'တိုက်ရိုက်တင်ထားသောပုံ' ကို ဝင်ဖတ်ခြင်း
            blocks_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
            blocks_res = requests.get(blocks_url, headers=NOTION_HEADERS).json()
            
            item_content_th = ""
            item_img_url = ""
            
            for block in blocks_res.get("results", []):
                # Notion ထဲ တိုက်ရိုက် Upload တင်ထားသောပုံများကို ဖတ်ခြင်း
                if block["type"] == "image":
                    img_data = block["image"]
                    if img_data["type"] == "file":  # တိုက်ရိုက် Upload တင်ထားသောပုံဖြစ်လျှင်
                        item_img_url = img_data["file"]["url"]
                    elif img_data["type"] == "external": # အကယ်၍ လင့်ခ်နဲ့ချိတ်ထားရင်လည်း ဖတ်ပေးမည်
                        item_img_url = img_data["external"]["url"]
                
                # စာသားများကို ဖတ်ခြင်း
                elif block["type"] == "paragraph":
                    text_list = block["paragraph"]["rich_text"]
                    if text_list:
                        item_content_th += text_list[0]["text"]["content"] + "\n"
            
            notion_items.append({
                "date": item_date,
                "title": item_title,
                "content_th": item_content_th.strip(),
                "image": item_img_url
            })
        return notion_items
    except Exception as e:
        return []

# ==========================================
# ၄။ BRAND SELECTION MENU (မူရင်းအတိုင်း မပြောင်းလဲပါ)
# ==========================================
if menu_choice == "Brand Selection":
    df_tractor, df_attach = load_data(selected_brand)
    if not df_tractor.empty:
        st.markdown("<h1 style='text-align: center; color: #ff6600;'>🚜 KMM Kubota Price List</h1>", unsafe_allow_html=True)
        
        if selected_brand in ["John-Deere", "New-Holland", "Mahindra", "Sonalika"]: origin = "Indian"
        elif selected_brand in ["YTO", "Yamabisi", "DongFeng"]: origin = "China"
        elif selected_brand == "Kubota": origin = "Japan/Thailand"
        elif selected_brand == "Yanmar": origin = "Japan"
        else: origin = ""
        
        display_text = f"({selected_brand} Brand - {origin})" if origin else f"({selected_brand} Brand)"
        st.markdown(f"<p style='text-align: center; color: #555; font-weight: bold;'>{display_text}</p>", unsafe_allow_html=True)
        st.write("---") 

        model_list = df_tractor.iloc[:, 0].astype(str).tolist()
        model_list = [m for m in model_list if m not in ["0", "0.0", "nan", "Model"]]
        selected_model = st.selectbox(f"{selected_brand} မော်ဒယ်ကို ရွေးပါ -", model_list)
        t_info = df_tractor[df_tractor.iloc[:, 0].astype(str) == selected_model].iloc[0]
        
        try:
            raw_p = str(t_info.iloc[1]).replace(',', '').strip()
            base_price = float(raw_p) if raw_p != "" else 0
        except: base_price = 0
        img_url = str(t_info.iloc[2])
        if img_url and img_url.startswith("http"):
            st.image(img_url, use_container_width=True)
        st.markdown(f"### 💰 စက်ဈေးနှုန်း: **{base_price:,.0f}** MMK")
        st.write("---")
        
        st.subheader("🛠 နောက်တွဲများ ရွေးချယ်ရန်")
        selected_att_total = 0
        if not df_attach.empty:
            filtered_att = df_attach[df_attach.iloc[:, 0].astype(str) == selected_model]
            def add_att_ui(label, m_col, p_col):
                if m_col in df_attach.columns:
                    items = filtered_att[[m_col, p_col]].drop_duplicates()
                    options = []
                    for _, row in items.iterrows():
                        if str(row[m_col]) not in ["0", "0.0", "nan"]:
                            try:
                                p_val = str(row[p_col]).replace(',', '').strip()
                                p = float(p_val)
                                options.append({"label": f"{row[m_col]} (+{p:,.0f} MMK)", "price": p})
                            except: continue
                    if options:
                        c = st.selectbox(f"{label}:", ["မယူပါ"] + [o["label"] for o in options], key=f"{label}_{selected_model}")
                        if c != "မယူပါ":
                            return next(item["price"] for item in options if item["label"] == c)
                return 0
            c1, c2 = st.columns(2)
            with c1:
                selected_att_total += add_att_ui("Rotary", "Rotary_Model1", "Rotary_Price")
                selected_att_total += add_att_ui("Disc Harrow", "Harrow_Model1", "Harrow_Price")
                selected_att_total += add_att_ui("Disc Plow", "Plow_Model1", "Plow_Price")
            with c2:
                selected_att_total += add_att_ui("Combine", "Combine_Model1", "Combine_Price")
                selected_att_total += add_att_ui("Breaker", "Breaker_Model1", "Breaker_Price")
                selected_att_total += add_att_ui("Sowing", "Transplanter_Model1", "Transplanter_Price")
        
        grand_total = base_price + selected_att_total
        st.success(f"## 📄 စုစုပေါင်း: {grand_total:,.0f} MMK")
    else:
        st.warning("Sheet Not Found")

# ==========================================
# ၅။ COMPETITOR NEWS UPDATES MENU (NOTION DIRECT IMAGE SHOW)
# ==========================================
elif menu_choice == "Competitor News Updates":
    st.markdown("<h1 style='text-align: center; color: #0066cc;'>📊 Competitor News Updates & News Myanmar</h1>", unsafe_allow_html=True)
    st.write("---")
    
    st.info("💡 အကြံပြုချက် - သတင်းအသစ်နှင့် ပုံများကို ကိုယ်တိုင် Notion App/Web ထဲမှာပဲ စိတ်ကြိုက် သွားရောက်ထည့်သွင်းပေးပါ။ အောက်တွင် အော်တို ပုံနှင့်တကွ ထွက်ပေါ်လာပါလိမ့်မည်။")
    st.write("<br>", unsafe_allow_html=True)
    
    # Notion Database ထဲက သတင်းများကို ပုံများနှင့်တကွ လှမ်းဆွဲထုတ်ခြင်း
    with st.spinner("Notion ပြက္ခဒိန်ထဲမှ ပုံများနှင့် သတင်းများကို တိုက်ရိုက်ဆွဲထုတ်နေပါသည်..."):
        notion_news_list = fetch_notion_news_with_images()
        
    if notion_news_list:
        for news in notion_news_list:
            # ရက်စွဲပြသခြင်း
            st.markdown(f"<h4 style='color: #ff6600; background-color: #f0f7ff; padding: 8px; border-radius: 5px;'>📅 Date: {news['date']}</h4>", unsafe_allow_html=True)
            
            with st.container(border=True):
                # ခေါင်းစဉ်ကြီး (ဗမာလို)
                st.subheader(f"🏢 {news['title']}")
                
                # အစ်ကို Notion ထဲမှာ တိုက်ရိုက်တင်ထားခဲ့တဲ့ ဓာတ်ပုံကို တိုက်ရိုက်ဆွဲပြခြင်း
                if news['image']:
                    st.image(news['image'], use_container_width=True)
                    
                # ထိုင်းလို သတင်းအကျဉ်းချုပ်
                st.write("**รายละเอียด (ထိုင်းလို အကျဉ်းချုပ်):**")
                st.write(news['content_th'])
                
            st.write("<br>", unsafe_allow_html=True)
    else:
        st.info("Notion ပြက္ခဒိန်ထဲမှာ ပြစရာ သတင်းမရှိသေးပါဘူးဗျာ။")

st.markdown("<br><hr><center><small>© 2026 KMM Service Co., Ltd.</small></center>", unsafe_allow_html=True)
















