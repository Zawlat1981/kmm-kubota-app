import streamlit as st
import pandas as pd

# ၁။ Page Config
st.set_page_config(page_title="KMM Kubota Price List", page_icon="🚜", layout="centered")

# Google Sheet ID
SHEET_ID = "1QqQvPKH7G0hqqhd_0V6cP40Htl8qdFEZ6nHBVe_53_g"

# --- Sidebar Menu ---
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

# --- ဒေတာ Load လုပ်သည့် Function ---
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

# ==========================================
# ၁။ BRAND SELECTION MENU
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
# ၂။ COMPETITOR NEWS UPDATES MENU (Perfect Grouping Version)
# ==========================================
elif menu_choice == "Competitor News Updates":
    st.markdown("<h1 style='text-align: center; color: #0066cc;'>📊 Competitor News Updates & News Myanmar</h1>", unsafe_allow_html=True)
    st.write("---")
    
    import time
    timestamp = int(time.time())
    comp_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Competitor%20News%20Updates&cache_bust={timestamp}"
    
    try:
        df_comp = pd.read_csv(comp_url).fillna('')
        df_comp.columns = [str(c).strip().lower() for c in df_comp.columns]
        
        grouped_data = {}  # Format: {'2026-05-18': [news1, news2]}
        current_date = "No Date"
        current_company = "Unknown Company"
        
        for _, row in df_comp.iterrows():
            r_date = str(row.get('date', '')).strip()
            r_company = str(row.get('company', '')).strip()
            r_content = str(row.get('content', '')).strip()
            
            # အကယ်၍ အရေးကြီးသော ကော်လံအားလုံး လွတ်နေပါက ကျော်သွားမည်
            if r_date == '' and r_company == '' and r_content == '':
                continue
                
            # Date အသစ်တွေ့လျှင် မှတ်သားမည်
            if r_date != '':
                current_date = r_date
            
            # Company အသစ်တွေ့လျှင် မှတ်သားမည်၊ အလွတ်ဖြစ်နေပါက အပေါ်က Company နာမည်ကို ဆက်သုံးမည်
            if r_company != '':
                current_company = r_company
                
            # သတင်းအချက်အလက်များကို စုစည်းမှုတစ်ခု ပြုလုပ်ခြင်း
            news_item = {
                'company': current_company,
                'content': r_content,
                'promo': str(row.get('promo', '')).strip(),
                'facebook': str(row.get('facebook', '')).strip(),
                'tiktok': str(row.get('tiktok', '')).strip()
            }
            
            # တကယ်လို့ သတင်းစာသား (Content) ပါလာရင် သက်ဆိုင်ရာ Date အုပ်စုထဲ ထည့်မည်
            if r_content != '':
                if current_date not in grouped_data:
                    grouped_data[current_date] = []
                grouped_data[current_date].append(news_item)
            
        if grouped_data:
            # ရက်စွဲအလိုက် အသစ်ဆုံး Date ကို ထိပ်ဆုံးတွင် ထားရန် Sort လုပ်မည်
            sorted_dates = sorted(grouped_data.keys(), reverse=True)
            
            for date_key in sorted_dates:
                # နေ့ရက်အလိုက် ခေါင်းစဉ်ကြီး
                st.markdown(f"<h2 style='color: #ff6600; background-color: #f0f7ff; padding: 10px; border-radius: 5px;'>📅 Date: {date_key}</h2>", unsafe_allow_html=True)
                
                for news in grouped_data[date_key]:
                    with st.container(border=True):
                        st.subheader(f"🏢 {news['company']}")
                        st.write("**Description:**")
                        st.write(news['content'])
                        
                        promo = news['promo']
                        if promo not in ['', '0']:
                            st.info(f"💡 {promo}")
                        
                        # ခလုတ်များ ပြသခြင်း
                        fb_link = news['facebook']
                        tt_link = news['tiktok']
                        if fb_link.startswith("http") or tt_link.startswith("http"):
                            st.write("---")
                            btn_col1, btn_col2 = st.columns(2)
                            if fb_link.startswith("http"):
                                with btn_col1:
                                    st.link_button("🔵 Facebook", fb_link, use_container_width=True)
                            if tt_link.startswith("http"):
                                with btn_col2:
                                    st.link_button("⚫ TikTok", tt_link, use_container_width=True)
                st.write("<br>", unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"Error loading data: {e}")

st.markdown("<br><hr><center><small>© 2026 KMM Service Co., Ltd.</small></center>", unsafe_allow_html=True)
















