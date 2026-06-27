import streamlit as st
import pandas as pd
import time
import datetime
import urllib.parse  # URL Space Bug ကို ဖြေရှင်းရန် ထည့်သွင်းထားသည်
from openai import OpenAI
from duckduckgo_search import DDGS  # Library မရှိသေးရင်: pip install duckduckgo-search

# Search Function အသစ်
def search_google(query):
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=4)]
            content = "\n".join([f"Source: {r['href']}\nInfo: {r['body']}" for r in results])
            return content
    except Exception as e:
        return f"ရှာဖွေရာတွင် အမှားဖြစ်သည်: {str(e)}"
# ၁။ Page Config
st.set_page_config(page_title="KMM Kubota Price List", page_icon="🚜", layout="centered")

def handle_brand_change():
    current_selection = st.session_state.main_page_brand_filter
    if current_selection != "— เลือก —":
        st.session_state.dropdown_query = current_selection
        # ဤနေရာတွင် Widget State ကို "— ရွေးချယ်ပါ —" သို့ Error မတက်ဘဲ ပြန်လည် Reset လုပ်ပေးနိုင်သည်
        st.session_state.main_page_brand_filter = "— ရွေးချယ်ပါ —"

# Google Sheet ID
SHEET_ID = "1QqQvPKH7G0hqqhd_0V6cP40Htl8qdFEZ6nHBVe_53_g" 

# အသုံးပြုထားသော Brand စာရင်းအားလုံး (Tab အမည်များ)
ALL_BRANDS = ["Kubota", "Yanmar", "Win-Shwe-Wah(2nd)", "John-Deere", "New-Holland", "YTO", "Mahindra", "Sonalika", "Yamabisi", "DongFeng"]

# --- ဒေတာ Load လုပ်သည့် Function (UI ဘက်မှ သုံးရန်) ---
@st.cache_data(ttl=60)
def load_data(tab_name):
    # Sheet Name များတွင် ကွက်လပ် သို့မဟုတ် Special Character ပါက အလိုအလျောက် URL Format ပြောင်းပေးရန်
    encoded_tab = urllib.parse.quote(tab_name)
    base_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_tab}" 
    try:
        df_tractor = pd.read_csv(base_url).fillna(0)
    except:
        df_tractor = pd.DataFrame()
    
    df_attach = pd.DataFrame()
    if tab_name in ["Kubota", "Yanmar"]:
        attachment_tab = f"Attachments_{tab_name}"
        encoded_attach_tab = urllib.parse.quote(attachment_tab)
        try:
            df_attach = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_attach_tab}").fillna(0)
        except:
            pass
    return df_tractor, df_attach

# --- ဒေတာ Load လုပ်သည့် Function (AI Agent အတွက် သီးသန့် Sheet ဖတ်ရန်) ---
@st.cache_data(ttl=60)
def load_all_sheet_data(tab_name):
    timestamp = int(time.time())
    # ဤနေရာတွင် URL Space Break မဖြစ်အောင် အသေအချာ Encode လုပ်ပေးထားပါသည်
    encoded_tab = urllib.parse.quote(tab_name)
    csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_tab}&cache_bust={timestamp}"
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
        selected_model = st.selectbox(f"{selected_brand} မော်ဒယ်ကို ရွေးပါ(เลือก Model) -", model_list)
        t_info = df_tractor[df_tractor.iloc[:, 0].astype(str) == selected_model].iloc[0]
        
        try:
            raw_p = str(t_info.iloc[1]).replace(',', '').strip()
            base_price = float(raw_p) if raw_p != "" else 0
        except: base_price = 0
        
        img_url = str(t_info.iloc[2])
        if img_url and img_url.startswith("http"):
            st.image(img_url, use_container_width=True)
            st.markdown(f"[🔍 ပုံကို အကြီးချဲ့ကြည့်ရန် (သို့မဟုတ်) Download ဆွဲရန် နှိပ်ပါ/คลิกเพื่อดูรูปภาพขนาดใหญ่ หรือ ดาวน์โหลด]({img_url})")
            
        st.markdown(f"### 💰 စက်ဈေးနှုန်း(ราคารถ): **{base_price:,.0f}** MMK")
        st.write("---")
        
        st.subheader("🛠 နောက်တွဲများ ရွေးချယ်ရန်(เลือก Implement)")
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
                        c = st.selectbox(f"{label}:", ["မယူပါ(ไม่เอา)"] + [o["label"] for o in options], key=f"{label}_{selected_model}")
                        if c != "မယူပါ(ไม่เอา)":
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
        st.success(f"## 📄 စုစုပေါင်း(ยอดรวมทั้งหมด): {grand_total:,.0f} MMK")
    else:
        st.warning("Sheet Not Found")

# ==========================================
# ၂။ COMPETITOR NEWS UPDATES MENU
# ==========================================
elif menu_choice == "Competitor News Updates":
    st.markdown("<h1 style='text-align: center; color: #0066cc;'>📊 Competitor News Updates & News Myanmar</h1>", unsafe_allow_html=True)
    st.write("---")
    
    df_comp = load_all_sheet_data("Competitor News Updates")
    
    if df_comp is not None and not df_comp.empty:
        df_comp.columns = [str(c).strip().lower() for c in df_comp.columns]
        
        st.markdown("### 🔍 သတင်းများ ပြန်လည်ရှာဖွေရန်/ค้นหาข่าวย้อนหลัง")
        search_col1, search_col2 = st.columns(2)
        
        with search_col1:
            search_query = st.text_input("📝 သတင်းခေါင်းစဉ်/ကုမ္ပဏီ/အကြောင်းအရာဖြင့် ရှာရန်(ตัวเลือกการค้นหา (ค้นหาข่าวตามวันที่หรือชื่อบริษัท))", "")
        with search_col2:
            search_date = st.date_input("📅 ရက်စွဲဖြင့် ရှာရန်(ค้นหาตามวันที่)", value=None, format="YYYY-MM-DD")
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

            if filtered_grouped_data:
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
                    
                    if items_displayed < total_filtered_items:
                        col1, col2 = st.columns([2, 3])
                        with col1:
                            if st.button("👍 မှန်ပါတယ်၊ နောက်ထပ်ပြပါ", key="news_more_pagination_btn"):
                                st.session_state.news_display_count += 7
                                st.rerun()
                        with col2:
                            if st.button("👎 မဟုတ်ပါဘူး၊ တခြားဟာရှာမယ်", key="news_stop_pagination_btn"):
                                st.write("🤖 လူကြီးမင်း သိလိုသော အကြောင်းအရာကို ထပ်မံ အသေးစိတ် ရိုက်ထည့်ပေးပါ ခင်ဗျာ။")
                    else:
                        st.info("👋 လူကြီးမင်း ရှာဖွေနေတဲ့ အကြောင်းအရာနဲ့ ပတ်သက်တဲ့ သတင်းအားလုံးကို ပြသပေးပြီးပါပြီ ခင်ဗျာ။")
            else:
                st.info("❌ ရှာဖွေမှုရလဒ်မရှိပါ။")
    else:
        st.error("Error loading data from sheet.")

# ==========================================
# ၃။ KMM TRACTOR AI AGENT MENU
# ==========================================
elif menu_choice == "KMM Tractor AI Agent":
    st.markdown("<h1 style='text-align: center; color: #ff6600;'>🤖 KMM Tractor AI Agent</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #555;'>สามารถสอบถามได้โดยการคลิกเลือกคำถามสำเร็จรูป หรือใช้ตัวกรอง</p>", unsafe_allow_html=True)
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
                st.markdown(message["content"])

        # --- 💡 [အသင့်မေးရန် မေးခွန်းတို ခလုတ်များ] ---
        st.markdown("<small style='color: #888;'>💡 คุณสามารถคลิกคำถามด้านล่างเพื่อสอบถามได้ง่ายๆ ครับ -</small>", unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
        suggested_query = None
        
        # Dropdown မှ ရွေးချယ်မှုရှိခဲ့ပါက တန်ဖိုးကို တစ်ကြိမ်ယူပြီး ပြန်ဖျက်ရန် စနစ်
        if "dropdown_query" in st.session_state:
            suggested_query = st.session_state.dropdown_query
            del st.session_state.dropdown_query
        
        with col_btn1:
            if st.button("📰 ข่าววันนี้", use_container_width=True):
                suggested_query = "ယနေ့သတင်း"
        with col_btn2:
            if st.button("📅 ข่าวเมื่อวาน", use_container_width=True):
                suggested_query = "မနေ့ကသတင်း"
        with col_btn3:
            if st.button("📊 รายงาน 1 สัปดาห์", use_container_width=True):
                suggested_query = "ပြီးခဲ့တဲ့တစ်ပတ်စာ သတင်း Report ထုတ်ပေးပါ"
                
        with col_btn4:
            # 🎯 ပြင်ဆင်ပြီး - Dropdown ထဲတွင် ပြသမည့် Brand စာရင်းများ (Indentation ညှိပြီး)
            brand_list = ["— เลือก —", "Kubota", "Yanmar", "Win-Shwe-Wah(2nd)", "John-Deere", "New-Holland", "YTO", "Mahindra", "Sonalika"]
            
            # label_visibility="collapsed" ဖြင့် စာတန်းကို ဖျောက်ပြီး ခလုတ်များနှင့် အမြင့်ညှိထားသည်
            selected_brand = st.selectbox(
                "Brand Filter", 
                options=brand_list,
                key="main_page_brand_filter",
                label_visibility="collapsed",
                on_change=handle_brand_change  # 🎯 Callback ကို စနစ်တကျ ချိတ်ဆက်ထားသည်
            )
        
        # --- 🔍 [ရွေးချယ်စရာများ Filters Box] ---
        with st.expander("🔍 ရွေးချယ်စရာများ (ค้นหาข่าวตามวันที่หรือชื่อบริษัท)", expanded=True):
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                filter_date = st.date_input("📅 เลือกวันที่ (Date)", value=None, format="YYYY-MM-DD")
            
            with col_filter2:
                filter_company = st.text_input("🏢 กรอกชื่อบริษัท/องค์กร (ဥပမာ - Win Shwe Wah, Kubota)", value="").strip()
            
            search_by_filter = st.button("🔎 ค้นหาด้วยข้อมูลที่เลือก", type="primary", use_container_width=True)
            if search_by_filter:
                if filter_date is not None and filter_company != "":
                    suggested_query = f"သတင်း စစ်ထုတ်မှု: {filter_date.strftime('%Y-%m-%d')} ရက်စွဲရှိ {filter_company} သတင်း"
                elif filter_date is not None:
                    suggested_query = f"သတင်း စစ်ထုတ်မှု: {filter_date.strftime('%Y-%m-%d')} ရက်စွဲရှိ သတင်းများ"
                elif filter_company != "":
                    suggested_query = f"သတင်း စစ်ထုတ်မှု: {filter_company} ကုမ္ပဏီ၏ သတင်းများ"
                else:
                    st.info("💡 အချက်အလက်များကို စစ်ထုတ်ရန် ရက်စွဲတစ်ခု ရွေးချယ်ပေးပါ သို့မဟုတ် ကုမ္ပဏီအမည် ရိုက်ထည့်ပေးပါခင်ဗျာ။")

        # Chat Input
        user_input = st.chat_input("You can ask any Question")
        user_query = suggested_query if suggested_query else user_input
                
        if user_query:
            with st.chat_message("user"):
                st.markdown(user_query)
            st.session_state.messages.append({"role": "user", "content": user_query})
            
            is_news_intent = any(keyword in user_query for keyword in ["သတင်း", "news", "report", "တင်ထားတာ", "ယနေ့", "မနေ့က", "ဒီနေ့", "စစ်ထုတ်မှု"])
            
            today_date_obj = datetime.date.today()
            yesterday_date_obj = today_date_obj - datetime.timedelta(days=1)
            
            today_formats = [today_date_obj.strftime("%Y-%m-%d"), today_date_obj.strftime("%d-%m-%Y"), today_date_obj.strftime("%d/%m/%Y")]
            yesterday_formats = [yesterday_date_obj.strftime("%Y-%m-%d"), yesterday_date_obj.strftime("%d-%m-%Y"), yesterday_date_obj.strftime("%d/%m/%Y")]

            # ==========================================================
            # 模式 (A) - စက်မော်ဒယ် သို့မဟုတ် ဈေးနှုန်းမေးမြန်းခြင်း
            # ==========================================================
            if not is_news_intent:
                found_tractor_data = []
                
                # အသုံးပြုသူရိုက်လိုက်သော စာသားကို ကွက်လပ်နှင့် Dash များဖြတ်ပြီး ညှိနှိုင်းခြင်း (Normalize)
                q_clean = "".join(user_query.split()).lower().replace("-", "").replace("_", "")
                
                with st.spinner("စက်ပစ္စည်းနှင့် ဈေးနှုန်းဒေတာများကို ရှာဖွေနေပါသည်..."):
                    for brand in ALL_BRANDS:
                        df_brand = load_all_sheet_data(brand)
                        if df_brand is not None and not df_brand.empty:
                            
                            # "Kubota DC70G Pro" ဟု တွဲရိုက်ခဲ့ပါက Brand အမည်အား ဖယ်ထုတ်၍ မော်ဒယ်သက်သက်ဖြင့် ရှာရန်
                            brand_clean = brand.lower().replace("-", "").replace("_", "")
                            q_model_only = q_clean.replace(brand_clean, "")
                            
                            for _, row in df_brand.iterrows():
                                model_name = str(row.iloc[0]).strip()
                                if model_name in ["0", "0.0", "nan", "Model", ""]:
                                    continue
                                    
                                # Sheet ထဲမှ မော်ဒယ်အမည်ကိုလည်း ကွက်လပ်နှင့် Dash များဖြတ်၍ ညှိနှိုင်းခြင်း
                                model_clean = "".join(model_name.split()).lower().replace("-", "").replace("_", "")
                                
                                match = False
                                if q_model_only:
                                    # Space ပါသည်ဖြစ်စေ၊ မပါသည်ဖြစ်စေ နှစ်ဖက်စလုံးကို နှိုင်းယှဉ်စစ်ဆေးခြင်း
                                    if q_model_only in model_clean or model_clean in q_model_only:
                                        match = True
                                else:
                                    # Brand အမည်သက်သက်သာ ရိုက်ရှာခဲ့ပါက ၎င်း Brand တစ်ခုလုံးကို ပြသရန်
                                    if brand.lower() in user_query.lower():
                                        match = True
                                        
                                if match:
                                    found_tractor_data.append({
                                        "brand": brand,
                                        "model": model_name,
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
                                    st.markdown(f"• **အခြေခံဈေးနှုန်း (Base Price):** <span style='color:#ff6600; font-size:22px; font-weight:bold;'>{p_val:,.0f}</span> MMK", unsafe_allow_html=True)
                                except:
                                    st.markdown(f"• **ဈေးနှုန်း (Price):** {item['price']} MMK")
                            
                            with col2:
                                if item['image'] and item['image'].startswith("http"):
                                    st.image(item['image'], use_container_width=True)
                            st.write("---")
                        
                        try:
                            response = client.chat.completions.create(
                                model="openai/gpt-4o-mini",
                                messages=[{"role": "system", "content": "မင်းက KMM အရောင်းဆိုင် AI ဖြစ်တယ်။ စက်ဈေးနှုန်းပြပြီးပြီဖြစ်လို့ လူကြီးမင်းအတွက် ဘာများထပ်မံကူညီပေးရမလဲလို့ မြန်မာလို ယဉ်ကျေးစွာ မေးပေးပါ။"}, {"role": "user", "content": user_query}]
                            )
                            ai_reply = response.choices[0].message.content
                            st.info(ai_reply)
                            st.session_state.messages.append({"role": "assistant", "content": f"🚜 {user_query} စက်ဈေးနှုန်းနှင့် အချက်အလက်များကို ပြသပေးခဲ့ပြီးပါပြီ။"})
                        except: pass
                    else:
                        st.warning(f"⚠️ တောင်းပန်ပါတယ်ခင်ဗျာ၊ လူကြီးမင်းမေးမြန်းထားသော မော်ဒယ် '{user_query}' ကို စက်ဈေးနှုန်း List ထဲတွင် ရှာမတွေ့ပါသဖြင့် AI အား ထပ်မံမေးမြန်းပေးပါမည်။")
                        try:
                            response = client.chat.completions.create(
                                model="openai/gpt-4o-mini",
                                messages=[{"role": "user", "content": user_query}]
                            )
                            ai_reply = response.choices[0].message.content
                            st.markdown(ai_reply)
                            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                        except: pass

            # 模式 (B) - Competitor News Updates ကို တိုက်ရိုက် UI Cards ဖြင့် ထုတ်ပြခြင်း (ကွက်တိပြင်ဆင်ပြီး)
            # ==========================================================
            else:
                matched_news_list = []
                
                status_placeholder = st.empty()
                status_placeholder.text("⏳ Competitor News Updates ရှီတ်ထဲမှ အချက်အလက်များကို Agent က စုစည်းနေပါသည်...")
                
                # ၁။ Competitor News Updates Sheet ကို Grouping ပုံစံအတိုင်း စနစ်တကျဖတ်မယ်
                df_comp = load_all_sheet_data("Competitor News Updates")
                grouped_news = []
                
                if df_comp is not None and not df_comp.empty:
                    df_comp.columns = [str(c).strip().lower() for c in df_comp.columns]
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
                                grouped_news.append(last_news_item)
                            
                            last_news_item = {
                                'date': current_date,
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
                    
                    if last_news_item is not None:
                        grouped_news.append(last_news_item)
                
                status_placeholder.empty()

                # ၂။ နေ့စွဲ သို့မဟုတ် ရှာဖွေမှုစကားလုံးအတိုင်း ကိုက်ညီတာကို စစ်ထုတ်မယ်
                for news in grouped_news:
                    news_date_clean = news['date'].replace('/', '-').strip()
                    company_lower = news['company'].lower()
                    content_lower = (news['content_mm'] + news['content_th']).lower()
                    
                    match_found = False
                    
                    if "စစ်ထုတ်မှု" in user_query:
                        match_date_ok = True
                        match_company_ok = True
                        if filter_date is not None:
                            sel_date_str = filter_date.strftime("%Y-%m-%d")
                            match_date_ok = (sel_date_str in news_date_clean)
                        if filter_company != "":
                            f_co = filter_company.lower()
                            match_company_ok = (f_co in company_lower or f_co in content_lower)
                        if match_date_ok and match_company_ok: match_found = True
                    elif any(word in user_query for word in ["ယနေ့", "ဒီနေ့", "မနေ့က", "ပတ်စာ", "report"]):
                        match_found = True
                    else:
                        q_words = user_query.lower().split()
                        if any(word in company_lower or word in content_lower for word in q_words):
                            match_found = True
                            
                    if match_found:
                        matched_news_list.append(news)
                
                # ၃။ ရလဒ်ထွက်ပေါ်လာမှုကို UI Card များဖြင့် တိုက်ရိုက် လှပစွာ ထုတ်ပြခြင်း
                with st.chat_message("assistant"):
                    if matched_news_list:
                        st.markdown(f"### 📊 ရှာဖွေတွေ့ရှိရသော Competitor News ({len(matched_news_list)}) စောင်")
                        for news in matched_news_list:
                            with st.container(border=True):
                                st.markdown(f"**🏢 {news['company']}** | 📅 {news['date']}")
                                if news['content_mm']: st.markdown(news['content_mm'])
                        
                        # AI Summary
                        context_str = "\n".join([f"- {n['company']}: {n['content_mm']}" for n in matched_news_list[:3]])
                        response = client.chat.completions.create(model="openai/gpt-4o-mini", messages=[{"role": "system", "content": "မြန်မာလို ရှင်းပြပေးပါ။"}, {"role": "user", "content": f"ဒီသတင်းတွေကို အကျဉ်းချုပ်ပေးပါ: {context_str}"}])
                        st.info(response.choices[0].message.content)

                    else:
                        # Sheet မှာ မရှိရင် DuckDuckGo သုံးမယ်
                        with st.status("အင်တာနက်ပေါ်မှ ရှာဖွေနေပါသည်...", expanded=True) as status:
                            google_result = search_google(user_query)
                            response = client.chat.completions.create(
                                model="openai/gpt-4o-mini",
                                messages=[
                                    {"role": "system", "content": "မင်းက အသိပညာပေး AI ဖြစ်တယ်။ ပေးထားသော Search ရလဒ်များကို အခြေခံ၍ မြန်မာလို ပြည့်စုံအောင်ဖြေပေးပါ။"},
                                    {"role": "user", "content": f"မေးခွန်း: {user_query}\n\nSearch ရလဒ်များ: {google_result}"}
                                ]
                            )
                            st.info(response.choices[0].message.content)
                            status.update(label="ပြီးဆုံးပါပြီ", state="complete")
