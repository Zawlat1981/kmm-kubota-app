import streamlit as st
import pandas as pd
import time
import datetime

# ၁။ Page Config
st.set_page_config(page_title="KMM Kubota Price List", page_icon="🚜", layout="centered")

# Google Sheet ID
SHEET_ID = "1QqQvPKH7G0hqqhd_0V6cP40Htl8qdFEZ6nHBVe_53_g" 

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
            # Brand Selection အောက်က ပုံအတွက်လည်း ဇူးမ်ချဲ့လင့်ခ် ထည့်ပေးထားပါတယ်
            st.markdown(f"[🔍 ပုံကို အကြီးချဲ့ကြည့်ရန် (သို့မဟုတ်) ဒေါင်းလုด်ซွဲရန် နှိပ်ပါ]({img_url})")
            
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
# ၂။ COMPETITOR NEWS UPDATES MENU (ရှာဖွေရေးနှင့် ပုံချဲ့စနစ် ပေါင်းစပ်ထားသောအပိုင်း)
# ==========================================
elif menu_choice == "Competitor News Updates":
    st.markdown("<h1 style='text-align: center; color: #0066cc;'>📊 Competitor News Updates & News Myanmar</h1>", unsafe_allow_html=True)
    st.write("---")
    
    timestamp = int(time.time())
    comp_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Competitor%20News%20Updates&cache_bust={timestamp}"
    
    try:
        df_comp = pd.read_csv(comp_url).fillna('')
        df_comp.columns = [str(c).strip().lower() for c in df_comp.columns]
        
        # --- [သစ်] ခေါင်းစဉ်ထိပ်မှာ ရှာဖွေရေး UI ထည့်သွင်းခြင်း ---
        st.markdown("### 🔍 သတင်းများ ပြန်လည်ရှာဖွေရန်/ค้นหาข่าวย้อนหลัง")
        search_col1, search_col2 = st.columns(2)
        
        with search_col1:
            search_query = st.text_input("📝 သတင်းခေါင်းစဉ်/ကုမ္ပဏီ/အကြောင်းအရာဖြင့် ရှာရန်/ค้นหาด้วยหัวข้อข่าว/บริษัท/เนื้อหา", "")
        with search_col2:
            search_date = st.date_input("📅 ရက်စွဲဖြင့် ရွေးချယ်ရန်/เลือกตามวันที่", value=None, format="YYYY-MM-DD")
        st.write("---")
        
        grouped_data = {}  
        current_date = "No Date"
        last_news_item = None 
        
        for _, row in df_comp.iterrows():
            r_date = str(row.get('date', '')).strip()
            r_company = str(row.get('company', '')).strip()
            r_content_th = str(row.get('content_th', '')).strip()
            r_content_mm = str(row.get('content_mm', '')).strip()
            
            if r_date == '' and r_company == '' and r_content_th == '' and r_content_mm == '':
                continue
                
            if r_date != '' or r_company != '':
                if r_date != '':
                    current_date = r_date
                
                if last_news_item is not None:
                    if last_news_item['date_key'] not in grouped_data:
                        grouped_data[last_news_item['date_key']] = []
                    grouped_data[last_news_item['date_key']].append(last_news_item)
                
                last_news_item = {
                    'date_key': current_date,
                    'company': r_company if r_company != '' else '💵 Exchange Rate / News',
                    'content_th': r_content_th,
                    'content_mm': r_content_mm,
                    'promo': str(row.get('promo', '')).strip(),
                    'facebook': str(row.get('facebook', '')).strip(),
                    'tiktok': str(row.get('tiktok', '')).strip(),
                    'telegram': str(row.get('telegram', '')).strip(),
                    'image_url': str(row.get('image_url', '')).strip() 
                }
            else:
                if last_news_item is not None:
                    if r_content_th != '':
                        last_news_item['content_th'] = (last_news_item['content_th'] + "\n" + r_content_th).strip()
                    if r_content_mm != '':
                        last_news_item['content_mm'] = (last_news_item['content_mm'] + "\n" + r_content_mm).strip()
                        
                    if str(row.get('image_url', '')).strip() != '':
                        last_news_item['image_url'] = str(row.get('image_url', '')).strip()
                    if str(row.get('promo', '')).strip() != '':
                        last_news_item['promo'] = str(row.get('promo', '')).strip()
                    if str(row.get('facebook', '')).strip() != '':
                        last_news_item['facebook'] = str(row.get('facebook', '')).strip()
                    if str(row.get('tiktok', '')).strip() != '':
                        last_news_item['tiktok'] = str(row.get('tiktok', '')).strip()
                    if str(row.get('telegram', '')).strip() != '':
                        last_news_item['telegram'] = str(row.get('telegram', '')).strip()
                else:
                    last_news_item = {
                        'date_key': current_date,
                        'company': '💵 Exchange Rate / News',
                        'content_th': r_content_th,
                        'content_mm': r_content_mm,
                        'promo': str(row.get('promo', '')).strip(),
                        'facebook': str(row.get('facebook', '')).strip(),
                        'tiktok': str(row.get('tiktok', '')).strip(),
                        'telegram': str(row.get('telegram', '')).strip(),
                        'image_url': str(row.get('image_url', '')).strip() 
                    }
        
        if last_news_item is not None:
            if last_news_item['date_key'] not in grouped_data:
                grouped_data[last_news_item['date_key']] = []
            grouped_data[last_news_item['date_key']].append(last_news_item)
            
        global_idx = 0 
        
        if grouped_data:
            sorted_dates = sorted(grouped_data.keys(), reverse=True)
            
            # --- [သစ်] ရိုက်ရှာထားသော စာသားနှင့် ရက်စွဲများအလိုက် Data စစ်ထုတ်ခြင်း (Filtering Logic) ---
            filtered_grouped_data = {}
            for d_key in sorted_dates:
                # ရက်စွဲ Filter စစ်ဆေးခြင်း
                if search_date is not None:
                    try:
                        # ရှာဖွေတဲ့ ရက်စွဲနဲ့ Data ထဲက ရက်စွဲ တူမတူ နှိုင်းယှဉ်ရန် Format ညှိခြင်း
                        sheet_date_obj = pd.to_datetime(d_key).date()
                        if sheet_date_obj != search_date:
                            continue
                    except:
                        # အကယ်၍ ရက်စွဲပြောင်းလဲရခက်ခဲသော စာသားဖြစ်နေလျှင် စာသားချင်း တိုက်စစ်ပါမည်
                        if str(search_date) not in d_key:
                            continue
                
                # စာသား Search Filter စစ်ဆေးခြင်း
                news_list_under_date = []
                for news in grouped_data[d_key]:
                    if search_query:
                        q = search_query.lower()
                        match_company = q in news['company'].lower()
                        match_th = q in news['content_th'].lower()
                        match_mm = q in news['content_mm'].lower()
                        
                        if not (match_company or match_th or match_mm):
                            continue # မကိုက်ညီရင် ကျော်သွားမယ်
                    
                    news_list_under_date.append(news)
                
                if news_list_under_date:
                    filtered_grouped_data[d_key] = news_list_under_date

            # --- ရလဒ် ထုတ်ပြခြင်း ---
            if filtered_grouped_data:
                for date_key in sorted(filtered_grouped_data.keys(), reverse=True):
                    st.markdown(f"<h2 style='color: #ff6600; background-color: #f0f7ff; padding: 10px; border-radius: 5px;'> Date: {date_key}</h2>", unsafe_allow_html=True)
                    
                    for news in filtered_grouped_data[date_key]:
                        with st.container(border=True):
                            st.subheader(f"🏢 {news['company']}")
                            
                            c_th = news.get('content_th', '').strip()
                            if c_th:
                                st.markdown("**🇹🇭 ภาษาไทย**")
                                st.markdown(c_th.replace("\n", "  \n"))
                            
                            if c_th and news.get('content_mm', '').strip():
                                st.write("---")
                                
                            c_mm = news.get('content_mm', '').strip()
                            if c_mm:
                                st.markdown("**🇲🇲 မြန်မာဘာသာ**")
                                st.markdown(c_mm.replace("\n", "  \n"))
                            
                            img_data = news.get('image_url', '').strip()
                            if img_data:
                                img_list = [i.strip() for i in img_data.split(',')]
                                st.write("---")
                                for img in img_list:
                                    if img.startswith("http"):
                                        # ကွန်ပျူတာအတွက် မူရင်းအတိုင်း ပုံပြခြင်း
                                        st.image(img, use_container_width=True) 
                                        # --- [သစ်] ဖုန်းသမားများ ချဲ့ကြည့်ရန် ဒေါင်းလုဒ်ဆွဲရန် လင့်ခ်အပို ထည့်သွင်းခြင်း ---
                                        st.markdown(f"[🔍 ပုံကို အကြီးချဲ့ကြည့်ရန် (သို့မဟုတ်) ဒေါင်းလုဒ်ဆွဲရန် နှိပ်ပါ]({img})")
                            
                            promo = news.get('promo', '')
                            if promo not in ['', '0']:
                                st.info(f"💡 {promo}")
                            
                            fb_link = news.get('facebook', '').strip()
                            tt_link = news.get('tiktok', '').strip()
                            tg_link = news.get('telegram', '').strip()

                            if (fb_link and fb_link.startswith("http")) or \
                               (tt_link and tt_link.startswith("http")) or \
                               (tg_link and tg_link.startswith("http")):
                                st.write("---")
                                btn_col1, btn_col2, btn_col3 = st.columns(3)
                                if fb_link and fb_link.startswith("http"):
                                    with btn_col1: st.link_button("🔵 Facebook", fb_link, use_container_width=True)
                                if tt_link and tt_link.startswith("http"):
                                    with btn_col2: st.link_button("⚫ TikTok", tt_link, use_container_width=True)
                                if tg_link and tg_link.startswith("http"):
                                    with btn_col3: st.link_button("✈️ Telegram", tg_link, use_container_width=True)
                            
                            st.write("<br>", unsafe_allow_html=True)
                            global_idx += 1 
            else:
                st.info("❌ ရှာဖွေမှုရလด်မရှိပါ။ စာသား သို့မဟုတ် ရက်စွဲကို ပြန်စစ်ပေးပါ။")
                
    except Exception as e:
        st.error(f"Error loading data: {e}")














 














