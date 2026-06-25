import streamlit as st
import pandas as pd
import time
import datetime
from openai import OpenAI

# ၁။ Page Config
st.set_page_config(page_title="KMM Kubota Price List", page_icon="🚜", layout="centered")

# Google Sheet ID
SHEET_ID = "1QqQvPKH7G0hqqhd_0V6cP40Htl8qdFEZ6nHBVe_53_g" 

# အသုံးပြုထားသော Brand စာရင်းအားလုံး (Tab အမည်များ)
ALL_BRANDS = ["Kubota", "Yanmar", "Win-Shwe-Wah(2nd)", "John-Deere", "New-Holland", "YTO", "Mahindra", "Sonalika", "Yamabisi", "DongFeng"]

# --- ဒေတာ Load လုပ်သည့် Function (UI ဘက်မှ သုံးရန်) ---
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

# --- ဒေတာ Load လုပ်သည့် Function (AI Agent အတွက် သီးသန့် Sheet ဖတ်ရန်) ---
@st.cache_data(ttl=60)
def load_all_sheet_data(tab_name):
    timestamp = int(time.time())
    csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={tab_name}&cache_bust={timestamp}"
    try:
        return pd.read_csv(csv_url)
    except:
        return None

# --- Sidebar Menu ---
with st.sidebar:
    st.markdown("## 🚜 KMM Service")
    menu_choice = st.radio(
        "သွားလိုရာကို ရွေးချယ်ပါ (กรุณาเลือกเมนู) -", 
        ["Brand Selection", "Competitor News Updates", "KMM Tractor AI Agent"]
    )
    st.write("---")
    
    if menu_choice == "Brand Selection":
        st.header("🔍 Filter")
        selected_brand = st.selectbox(
            "အမှတ်တံဆိပ် ရွေးချယ်ပါ (กรุณาเลือกยี่ห้อ) -", 
            ALL_BRANDS
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
            st.markdown(f"[🔍 ပုံကို အကြီးချဲ့ကြည့်ရန် (သို့မဟုတ်) Download ဆွဲရန် နှိပ်ပါ/คลิกเพื่อดูรูปภาพขนาดใหญ่ หรือ ดาวน์โหลด]({img_url})")
            
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
# ၂။ COMPETITOR NEWS UPDATES MENU (ပြင်ဆင်ပြီး)
# ==========================================
elif menu_choice == "Competitor News Updates":
    st.markdown("<h1 style='text-align: center; color: #0066cc;'>📊 Competitor News Updates & News Myanmar</h1>", unsafe_allow_html=True)
    st.write("---")
    
    timestamp = int(time.time())
    comp_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Competitor%20News%20Updates&cache_bust={timestamp}"
    
    try:
        df_comp = pd.read_csv(comp_url).fillna('')
        df_comp.columns = [str(c).strip().lower() for c in df_comp.columns]
        
        st.markdown("### 🔍 သတင်းများ ပြန်လည်ရှာဖွေရန်/ค้นหาข่าวย้อนหลัง")
        search_col1, search_col2 = st.columns(2)
        
        with search_col1:
            search_query = st.text_input("📝 သတင်းခေါင်းစဉ်/ကုမ္ပဏီ/အကြောင်းအရာဖြင့် ရှာရန်", "")
        with search_col2:
            search_date = st.date_input("📅 ရက်စွဲဖြင့် ရွေးချယ်ရန်", value=None, format="YYYY-MM-DD")
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
            
        if grouped_data:
            sorted_dates = sorted(grouped_data.keys(), reverse=True)
            filtered_grouped_data = {}
            for d_key in sorted_dates:
                if search_date is not None:
                    try:
                        sheet_date_obj = pd.to_datetime(d_key).date()
                        if sheet_date_obj != search_date:
                            continue
                    except:
                        if str(search_date) not in d_key:
                            continue
                
                news_list_under_date = []
                for news in grouped_data[d_key]:
                    if search_query:
                        q = search_query.lower()
                        match_company = q in news['company'].lower()
                        match_th = q in news['content_th'].lower()
                        match_mm = q in news['content_mm'].lower()
                        if not (match_company or match_th or match_mm):
                            continue 
                    news_list_under_date.append(news)
                
                if news_list_under_date:
                    filtered_grouped_data[d_key] = news_list_under_date

            # 💡 [Conversational Pagination UI Integration]
            if filtered_grouped_data:
                # Query ပြောင်းလဲမှုရှိမရှိ စစ်ဆေးပြီး Session State သတ်မှတ်ခြင်း
                current_query_state = (search_query, str(search_date))
                if "news_display_count" not in st.session_state or st.session_state.get("news_last_query") != current_query_state:
                    st.session_state.news_display_count = 7
                    st.session_state.news_last_query = current_query_state

                current_limit = st.session_state.news_display_count
                total_filtered_items = sum(len(items) for items in filtered_grouped_data.values())
                
                items_displayed = 0
                break_all = False
                
                with st.chat_message("assistant"):
                    st.write(f"🔍 ရှာဖွေမှုရလဒ် စုစုပေါင်း ({total_filtered_items}) စောင်အနက်မှ အသစ်ဆုံးသတင်းများကို ဖော်ပြပေးလိုက်ပါတယ် ခင်ဗျာ။")
                    st.write("---")
                    
                    for date_key in sorted(filtered_grouped_data.keys(), reverse=True):
                        if break_all:
                            break
                        
                        date_items = filtered_grouped_data[date_key]
                        items_to_show_this_date = []
                        
                        for news in date_items:
                            if items_displayed < current_limit:
                                items_to_show_this_date.append(news)
                                items_displayed += 1
                            else:
                                break_all = True
                                break
                        
                        if items_to_show_this_date:
                            st.markdown(f"<h2 style='color: #ff6600; background-color: #f0f7ff; padding: 10px; border-radius: 5px;'> Date: {date_key}</h2>", unsafe_allow_html=True)
                            for news in items_to_show_this_date:
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
                                                st.image(img, use_container_width=True) 
                                                st.markdown(f"[🔍 ပုံကို အကြီးချဲ့ကြည့်ရန်]({img})")
                                                
                                    promo = news.get('promo', '')
                                    if promo not in ['', '0']: st.info(f"💡 {promo}")
                                    
                                    fb_link = news.get('facebook', '').strip()
                                    tt_link = news.get('tiktok', '').strip()
                                    tg_link = news.get('telegram', '').strip()
                                    if (fb_link and fb_link.startswith("http")) or (tt_link and tt_link.startswith("http")) or (tg_link and tg_link.startswith("http")):
                                        st.write("---")
                                        btn_col1, btn_col2, btn_col3 = st.columns(3)
                                        if fb_link and fb_link.startswith("http"):
                                            with btn_col1: st.link_button("🔵 Facebook", fb_link, use_container_width=True)
                                        if tt_link and tt_link.startswith("http"):
                                            with btn_col2: st.link_button("⚫ TikTok", tt_link, use_container_width=True)
                                        if tg_link and tg_link.startswith("http"):
                                            with btn_col3: st.link_button("✈️ Telegram", tg_link, use_container_width=True)
                                    st.write("<br>", unsafe_allow_html=True)

                    st.write("🤖 **လူကြီးမင်း ရှာဖွေနေတာ / သိလိုတာ မှန်ပါသလား ခင်ဗျာ။**")
                    
                    # နောက်ထပ် ပြစရာ သတင်းကျန်သေးရင် ခလုတ်ပြပေးခြင်း
                    if items_displayed < total_filtered_items:
                        col1, col2 = st.columns([2, 3])
                        with col1:
                            if st.button("👍? မှန်ပါတယ်၊ နောက်ထပ်ပြပါ", key="news_more_pagination_btn"):
                                st.session_state.news_display_count += 7
                                st.rerun()
                        with col2:
                            if st.button("👎? မဟုတ်ပါဘူး၊ တခြားဟာရှာမယ်", key="news_stop_pagination_btn"):
                                st.write("🤖 လူကြီးမင်း သိလိုသော အကြောင်းအရာကို ထပ်မံ အသေးစိတ် ရိုက်ထည့်ပေးပါ ခင်ဗျာ။")
                    else:
                        st.info("👋 လူကြီးမင်း ရှာဖွေနေတဲ့ အကြောင်းအရာနဲ့ ပတ်သက်တဲ့ သတင်းအားလုံးကို ပြသပေးပြီးပါပြီ ခင်ဗျာ။")
            else:
                st.info("❌ ရှာဖွေမှုရလဒ်မရှိပါ။")
    except Exception as e:
        st.error(f"Error loading data: {e}")

# ==========================================
# ၃။ KMM TRACTOR AI AGENT MENU (မေးခွန်းခွဲခြားမှုစနစ် အဆင့်မြှင့်တင်ပြီး)
# ==========================================
elif menu_choice == "KMM Tractor AI Agent":
    st.markdown("<h1 style='text-align: center; color: #ff6600;'>🤖 KMM Tractor AI Agent</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #555;'>Tractor မော်ဒယ်များ၊ ဈေးနှုန်းများနှင့် ပြိုင်ဘက်သတင်းများကို စမတ်ကျကျ မေးမြန်းနိုင်ပါသည်</p>", unsafe_allow_html=True)
    st.write("---")
    
    if "OPENROUTER_API_KEY" in st.secrets:
        api_key = st.secrets["OPENROUTER_API_KEY"]
    else:
        api_key = "YOUR_OPENROUTER_API_KEY"
        
    if api_key == "YOUR_OPENROUTER_API_KEY":
        st.warning("⚠️ OpenRouter API Key ထည့်သွင်းရန် လိုအပ်နေပါသည်။ Streamlit Secrets ထဲတွင် ဖြည့်စွက်ပေးပါ။")
    else:
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if isinstance(message["content"], str):
                    st.markdown(message["content"])
                
        if user_query := st.chat_input("ဥပမာ - 'M6240 ဈေးဘယ်လောက်လဲ' သို့မဟုတ် 'မနေ့ကသတင်းပြပါ'"):
            with st.chat_message("user"):
                st.markdown(user_query)
            st.session_state.messages.append({"role": "user", "content": user_query})
            
            # --- 💡 အဓိကပြင်ဆင်ချက်- User မေးခွန်းကို Intent (ရည်ရွယ်ချက်) ခွဲခြားခြင်း ---
            # စကားလုံးများကို စစ်ထုတ်ပြီး သတင်းမေးတာလား၊ စက်ဈေးနှုန်းမေးတာလား ခွဲခြားမည်
            is_news_intent = any(keyword in user_query for keyword in ["သတင်း", "news", "report", "တင်ထားတာ", "ယနေ့", "မနေ့က"])
            
            today_date_obj = datetime.date.today()
            today_date = today_date_obj.strftime("%Y-%m-%d")
            yesterday_date = (today_date_obj - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            
            # ==========================================================
            # ပုံစံ (က) - စက်မော်ဒယ် သို့မဟုတ် ဈေးနှုန်းမေးမြန်းခြင်း (is_news_intent မဟုတ်လျှင်)
            # ==========================================================
            if not is_news_intent:
                context_tractor = ""
                found_tractor_data = []
                
                with st.spinner("စက်ပစ္စည်းနှင့် ဈေးနှုန်းဒေတာများကို ရှာဖွေနေပါသည်..."):
                    for brand in ALL_BRANDS:
                        df_brand = load_all_sheet_data(brand)
                        if df_brand is not None and not df_brand.empty:
                            # User ရိုက်လိုက်တဲ့ စာသား (ဥပမာ - M6240) ပါဝင်တဲ့ Row ကို အမှတ်တံဆိပ်အားလုံးထဲ လိုက်ရှာမယ်
                            matched_rows = df_brand[df_brand.astype(str).apply(lambda x: x.str.contains(user_query, case=False)).any(axis=1)]
                            if not matched_rows.empty:
                                for _, row in matched_rows.iterrows():
                                    found_tractor_data.append({
                                        "brand": brand,
                                        "model": str(row.iloc[0]),
                                        "price": str(row.iloc[1]),
                                        "image": str(row.iloc[2]) if len(row) > 2 else ""
                                    })
                
                with st.chat_message("assistant"):
                    if found_tractor_data:
                        st.markdown(f"### 🚜 {user_query} အတွက် ရှာဖွေတွေ့ရှိရသော မော်ဒယ်များနှင့် ဈေးနှုန်းများ")
                        st.write("---")
                        
                        for idx, item in enumerate(found_tractor_data):
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                st.markdown(f"### {idx+1}။ **{item['model']}**")
                                st.markdown(f"• **အမှတ်တံဆိပ် (Brand):** {item['brand']}")
                                try:
                                    p_val = float(str(item['price']).replace(',', '').strip())
                                    st.markdown(f"• **အခြေခံဈေးနှုန်း (Base Price):** <span style='color:#ff6600; font-size:20px; font-weight:bold;'>{p_val:,.0f}</span> MMK", unsafe_allow_html=True)
                                except:
                                    st.markdown(f"• **ဈေးနှုန်း (Price):** {item['price']} MMK")
                            
                            with col2:
                                if item['image'] and item['image'].startswith("http"):
                                    st.image(item['image'], use_container_width=True)
                            st.write("---")
                        
                        st.session_state.messages.append({"role": "assistant", "content": f"🚜 {user_query} နှင့် ပတ်သက်သည့် မော်ဒယ်နှင့် ဈေးနှုန်းအချက်အလက်များကို ပြသပေးခဲ့ပြီးပါပြီ။"})
                    else:
                        st.warning(f"⚠️ လူကြီးမင်းမေးမြန်းထားသော မော်ဒယ် '{user_query}' ကို စက်ဈေးနှုန်း List ထဲတွင် ရှာမတွေ့ပါသဖြင့် AI အား ထပ်မံမေးမြန်းပေးပါမည်။")
                        # ဒေတာ တိုက်ရိုက်မတွေ့ရင် AI ကို သာမန်အတိုင်း ပတ်သက်တာ ဖြေခိုင်းမည်
                        try:
                            response = client.chat.completions.create(
                                model="openai/gpt-4o-mini",
                                messages=[{"role": "user", "content": user_query}]
                            )
                            st.write(response.choices[0].message.content)
                        except: pass

            # ==========================================================
            # ပုံစံ (ခ) - သတင်း သီးသန့်မေးမြန်းခြင်း (is_news_intent ဖြစ်လျှင်)
            # ==========================================================
            else:
                search_keyword = user_query
                is_date_query = False
                
                if "မနေ့က" in user_query:
                    search_keyword = yesterday_date
                    is_date_query = True
                elif "ယနေ့" in user_query or "ဒီနေ့" in user_query:
                    search_keyword = today_date
                    is_date_query = True
                
                df_news = load_all_sheet_data("Competitor News Updates")
                matched_news_list = []
                
                if df_news is not None and not df_news.empty:
                    df_news.columns = [str(c).strip().lower() for c in df_news.columns]
                    current_date = "No Date"
                    last_news_item = None
                    all_structured_news = []
                    
                    for _, row in df_news.iterrows():
                        r_date = str(row.get('date', '')).strip()
                        r_company = str(row.get('company', '')).strip()
                        r_content_th = str(row.get('content_th', '')).strip()
                        r_content_mm = str(row.get('content_mm', '')).strip()
                        
                        if r_date == '' and r_company == '' and r_content_th == '' and r_content_mm == '':
                            continue
                        if r_date != '' or r_company != '':
                            if r_date != '': current_date = r_date
                            if last_news_item is not None:
                                all_structured_news.append(last_news_item)
                            last_news_item = {
                                'date': current_date,
                                'company': r_company if r_company != '' else '💵 Exchange Rate / News',
                                'content_th': r_content_th,
                                'content_mm': r_content_mm,
                                'promo': str(row.get('promo', '')).strip(),
                                'image_url': str(row.get('image_url', '')).strip()
                            }
                        else:
                            if last_news_item is not None:
                                if r_content_th: last_news_item['content_th'] = (last_news_item['content_th'] + "\n" + r_content_th).strip()
                                if r_content_mm: last_news_item['content_mm'] = (last_news_item['content_mm'] + "\n" + r_content_mm).strip()
                                if str(row.get('image_url', '')).strip(): last_news_item['image_url'] = str(row.get('image_url', '')).strip()
                                if str(row.get('promo', '')).strip(): last_news_item['promo'] = str(row.get('promo', '')).strip()
                    if last_news_item is not None:
                        all_structured_news.append(last_news_item)
                    
                    for news in all_structured_news:
                        if is_date_query:
                            if search_keyword in news['date']:
                                matched_news_list.append(news)
                        else:
                            if (search_keyword.lower() in news['company'].lower() or 
                                search_keyword.lower() in news['content_mm'].lower() or 
                                search_keyword.lower() in news['content_th'].lower()):
                                matched_news_list.append(news)

                with st.chat_message("assistant"):
                    if matched_news_list:
                        st.markdown(f"### 📅 {search_keyword} အတွက် ရှာဖွေတွေ့ရှိသော သတင်းများ")
                        st.write("---")
                        for idx, news in enumerate(matched_news_list):
                            brief_text = news['content_mm'][:60] + "..." if len(news['content_mm']) > 60 else news['content_mm']
                            st.markdown(f"#### 🏢 {news['company']} ({news['date']})")
                            st.write(f"📝 {brief_text}")
                            
                            img_url = news.get('image_url', '').split(',')[0].strip()
                            if img_url and img_url.startswith("http"):
                                st.image(img_url, width=150)
                            
                            with st.expander("🔍 သတင်းအပြည့်အစုံနှင့် ပုံကို ထပ်မံအသေးစိတ်ကြည့်ရန်"):
                                if news['content_mm']: st.write(news['content_mm'])
                                all_imgs = [i.strip() for i in news.get('image_url', '').split(',') if i.strip().startswith("http")]
                                for img in all_imgs: st.image(img, use_container_width=True)
                            st.write("---")
                    else:
                        st.warning("⚠️ မေးမြန်းထားသော သတင်းအချက်အလက်ကို ရှာမတွေ့ပါခင်ဗျာ။")
