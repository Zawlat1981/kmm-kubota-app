import streamlit as st
import pandas as pd
import datetime
import urllib.parse
from openai import OpenAI

# ========================================== 
# ၁။ Page Config
# ==========================================
st.set_page_config(page_title="KMM Kubota Price List", page_icon="🚜", layout="wide") 

# ==========================================
# ၂။ Constants
# ==========================================
SHEET_ID = "1QqQvPKH7G0hqqhd_0V6cP40Htl8qdFEZ6nHBVe_53_g"

ALL_BRANDS = [
    "Kubota", "Yanmar", "Win-Shwe-Wah(2nd)", "John-Deere",
    "New-Holland", "YTO", "Mahindra", "Sonalika", "Yamabisi", "DongFeng"
]

# ==========================================
# ၃။ Callback Function
# ==========================================
def handle_brand_change():
    current_selection = st.session_state.main_page_brand_filter
    if current_selection != "— เลือก —":
        st.session_state.dropdown_query = current_selection
        st.session_state.main_page_brand_filter = "— เลือก —"

# ==========================================
# ၄။ Data Loading Functions
# ==========================================
@st.cache_data(ttl=60)
def load_data(tab_name):
    encoded_tab = urllib.parse.quote(tab_name)
    base_url = (
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
        f"/gviz/tq?tqx=out:csv&sheet={encoded_tab}"
    )
    try:
        df_tractor = pd.read_csv(base_url).fillna(0) 
    except Exception as e:
        st.warning(f"Tractor data load မအောင်မြင်ပါ ({tab_name}): {e}")
        df_tractor = pd.DataFrame()

    df_attach = pd.DataFrame()
    if tab_name in ["Kubota", "Yanmar"]:
        attachment_tab = f"Attachments_{tab_name}"
        encoded_attach_tab = urllib.parse.quote(attachment_tab)
        attach_url = (
            f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
            f"/gviz/tq?tqx=out:csv&sheet={encoded_attach_tab}"
        )
        try:
            df_attach = pd.read_csv(attach_url).fillna(0)
        except Exception as e:
            st.warning(f"Attachment data load မအောင်မြင်ပါ ({attachment_tab}): {e}")

    return df_tractor, df_attach


@st.cache_data(ttl=60)
def load_all_sheet_data(tab_name):
    encoded_tab = urllib.parse.quote(tab_name)
    csv_url = (
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
        f"/gviz/tq?tqx=out:csv&sheet={encoded_tab}"
    )
    try:
        return pd.read_csv(csv_url)
    except Exception as e:
        st.warning(f"Sheet data load မအောင်မြင်ပါ ({tab_name}): {e}")
        return None


def parse_news_sheet(df):
    grouped_news = []
    if df is None or df.empty:
        return grouped_news

    df.columns = [str(c).strip().lower() for c in df.columns]
    current_date = "No Date"
    last_news_item = None

    for _, row in df.iterrows():
        r_date = str(row.get('date', '')).strip()
        r_company = str(row.get('company', '')).strip()
        r_content_th = str(row.get('content_th', '')).strip()

        if r_date == '' and r_company == '' and r_content_th == '':
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
                'promo': str(row.get('promo', '')).strip(),
                'facebook': str(row.get('facebook', '')).strip(),
                'tiktok': str(row.get('tiktok', '')).strip(),
                'telegram': str(row.get('telegram', '')).strip(),
                'image_url': str(row.get('image_url', '')).strip(),
            }
        else:
            if last_news_item is not None:
                if r_content_th:
                    last_news_item['content_th'] = (last_news_item['content_th'] + "\n" + r_content_th).strip()
                for field in ['image_url', 'promo', 'facebook', 'tiktok', 'telegram']:
                    val = str(row.get(field, '')).strip()
                    if val:
                        last_news_item[field] = val
            else:
                last_news_item = {
                    'date': current_date,
                    'company': '💵 Exchange Rate / News',
                    'content_th': r_content_th,
                    'promo': str(row.get('promo', '')).strip(),
                    'facebook': str(row.get('facebook', '')).strip(),
                    'tiktok': str(row.get('tiktok', '')).strip(),
                    'telegram': str(row.get('telegram', '')).strip(),
                    'image_url': str(row.get('image_url', '')).strip(),
                }

    if last_news_item is not None:
        grouped_news.append(last_news_item)

    return grouped_news


def render_news_card(news):
    """ထိုင်းသတင်း (content_th) နှင့် ပုံများကိုသာ ပြသမည် (မြန်မာဘာသာပြန် လုံးဝမပါပါ)"""
    with st.container(border=True):
        st.markdown(
            f"<h3 style='color: #0066cc; margin: 0;'>🏢 {news['company']}</h3>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<small style='color: #888;'>📅 Date: {news['date']}</small>",
            unsafe_allow_html=True
        )
        st.write("---")

        c_th = news.get('content_th', '').strip()
        if c_th:
            st.markdown("**🇹🇭 Content (TH)**")
            st.markdown(c_th.replace("\n", "  \n"))

        img_data = news.get('image_url', '').strip()
        if img_data:
            img_list = [i.strip() for i in img_data.split(',') if i.strip().startswith('http')]
            if img_list:
                st.write("---")
                for img in img_list:
                    st.image(img)
                    st.markdown(f"[🔍 ပုံကိုကြည့်ရန်နှိပ်ပါ (กดเพื่อดูภาพ)]({img})")

        promo = str(news.get('promo', '')).strip()
        if promo and promo not in ('0', '0.0', 'nan', 'None', ''):
            st.info(f"💡 {promo}")

        fb_link = news.get('facebook', '').strip()
        tt_link = news.get('tiktok', '').strip()
        tg_link = news.get('telegram', '').strip()

        has_links = (
            (fb_link and fb_link.startswith("http")) or
            (tt_link and tt_link.startswith("http")) or
            (tg_link and tg_link.startswith("http"))
        )
        if has_links:
            st.write("---")
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            if fb_link and fb_link.startswith("http"):
                with btn_col1:
                    st.link_button("🔵 Facebook", fb_link, use_container_width=True)
            if tt_link and tt_link.startswith("http"):
                with btn_col2:
                    st.link_button("⚫ TikTok", tt_link, use_container_width=True)
            if tg_link and tg_link.startswith("http"):
                with btn_col3:
                    st.link_button("✈️ Telegram", tg_link, use_container_width=True)

        st.write("<br>", unsafe_allow_html=True)


# ==========================================
# ၅။ Groq / API Setup
# ==========================================
GEMINI_SYSTEM_INSTRUCTION = (
    "မင်းက KMM Kubota ကုမ္ပဏီက AI Assistant ဖြစ်တယ်။ "
    "KMM Kubota ကုမ္ပဏီက Kubota ထွန်စက်၊ ရိတ်သိမ်းခြွေ့လှေ့စက်၊ ကောက်စိုက်စက်၊ မြေတူးစက် တို့ကိုရောင်းချသောကုမ္ပဏီဖြစ်သည်။ "
    "ထိုင်းနိုင်ငံနှင့် မြန်မာနိုင်ငံတွင်ကုမ္ပဏီများရှိသည်။ "
    "မင်းက လယ်ယာသုံးစက်ပစ္စည်း၊ ဈေးကွက်နှင့် "
    "အခြားအထွေထွေမေးခွန်းများကို ရှင်းလင်းယဉ်ကျေးစွာ ဖြေကြားပေးပါ။"
)

groq_api_key = st.secrets.get("GROQ_API_KEY", "")
gemini_client = None
if groq_api_key:
    gemini_client = OpenAI(
        api_key=groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )


def ask_gemini(user_query: str, history: list) -> str:
    if gemini_client is None:
        return "⚠️ GROQ_API_KEY မသတ်မှတ်ရသေးပါ။ Streamlit Secrets ထဲတွင် ဖြည့်ပေးပါ ခင်ဗျာ။"
    try:
        messages = [{"role": "system", "content": GEMINI_SYSTEM_INSTRUCTION}]
        for msg in history[:-1]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_query})

        response = gemini_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI ဖြေကြားမှု မအောင်မြင်ပါ: {e}"

# ==========================================
# ၆။ Sidebar Menu
# ==========================================
with st.sidebar:
    st.markdown("## 🚜 KMM Service")
    menu_choice = st.radio(
        "သွားလိုရာကို ရွေးချယ်ပါ (กรุณาเลือกเมนู) -",
        ["Brand Selection", "Competitor News Updates", "KMM Tractor AI Agent"]
    )
    st.write("---")

    sidebar_selected_brand = None
    if menu_choice == "Brand Selection":
        st.header("🔍 Filter")
        sidebar_selected_brand = st.selectbox(
            "အမှတ်တံဆိပ် ရွေးချယ်ပါ (กรุณาเลือกยี่ห้อ) -",
            ALL_BRANDS
        )

# ==========================================
# Menu ၁။ BRAND SELECTION
# ==========================================
if menu_choice == "Brand Selection":
    if sidebar_selected_brand is None:
        st.warning("Sidebar မှ Brand တစ်ခု ရွေးချယ်ပေးပါ ခင်ဗျာ။")
        st.stop()

    df_tractor, df_attach = load_data(sidebar_selected_brand)

    if not df_tractor.empty:
        st.markdown(
            "<h1 style='text-align: center; color: #ff6600;'>🚜 KMM Kubota Price List</h1>",
            unsafe_allow_html=True
        )

        if sidebar_selected_brand in ["John-Deere", "New-Holland", "Mahindra", "Sonalika"]:
            origin = "Indian"
        elif sidebar_selected_brand in ["YTO", "Yamabisi", "DongFeng"]:
            origin = "China"
        elif sidebar_selected_brand == "Kubota":
            origin = "Japan/Thailand"
        elif sidebar_selected_brand == "Yanmar":
            origin = "Japan"
        else:
            origin = ""

        display_text = (
            f"({sidebar_selected_brand} Brand - {origin})"
            if origin else
            f"({sidebar_selected_brand} Brand)"
        )
        st.markdown(
            f"<p style='text-align: center; color: #555; font-weight: bold;'>{display_text}</p>",
            unsafe_allow_html=True
        )
        st.write("---")

        model_list = df_tractor.iloc[:, 0].astype(str).tolist()
        model_list = [m for m in model_list if m not in ["0", "0.0", "nan", "Model"]]
        selected_model = st.selectbox(
            f"{sidebar_selected_brand} မော်ဒယ်ကို ရွေးပါ (เลือก Model) -",
            model_list
        )
        t_info = df_tractor[df_tractor.iloc[:, 0].astype(str) == selected_model].iloc[0]

        try:
            raw_p = str(t_info.iloc[1]).replace(',', '').strip()
            base_price = float(raw_p) if raw_p else 0.0
        except Exception:
            base_price = 0.0

        img_url = str(t_info.iloc[2]) if len(t_info) > 2 else ""
        if img_url and isinstance(img_url, str) and (img_url.startswith("http://") or img_url.startswith("https://")):
            try:
               st.image(img_url)
               st.markdown(f"[🔍 ပုံကိုကြည့်ရန်နှိပ်ပါ (กดเพื่อดูภาพ)]({img_url})")
            except Exception as e:
               st.warning(f"ပုံကို Loading လုပ်ရာတွင် အမှားအယွင်းရှိသည်: {e}")

        st.markdown(f"### 💰 စက်ဈေးနှုန်း (ราคารถ): **{base_price:,.0f}** MMK")
        st.write("---")

        st.subheader("🛠 နောက်တွဲများ ရွေးချယ်ရန် (เลือก Implement)")
        selected_att_total = 0.0

        if not df_attach.empty:
            filtered_att = df_attach[df_attach.iloc[:, 0].astype(str) == selected_model]

            def add_att_ui(label, m_col, p_col):
                if m_col not in df_attach.columns:
                    return 0.0
                items = filtered_att[[m_col, p_col]].drop_duplicates()
                options = []
                for _, row in items.iterrows():
                    if str(row[m_col]) not in ["0", "0.0", "nan", ""]:
                        try:
                            p_val = float(str(row[p_col]).replace(',', '').strip())
                            options.append({
                                "label": f"{row[m_col]} (+{p_val:,.0f} MMK)",
                                "price": p_val
                            })
                        except Exception:
                            continue
                if not options:
                    return 0.0
                choice = st.selectbox(
                    f"{label}:",
                    ["မယူပါ (ไม่เอา)"] + [o["label"] for o in options],
                    key=f"{label}_{selected_model}"
                )
                if choice != "မယူပါ (ไม่เอา)":
                    return next(o["price"] for o in options if o["label"] == choice)
                return 0.0

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
        st.success(f"## 📄 စုစုပေါင်း (ยอดรวมทั้งหมด): {grand_total:,.0f} MMK")
    else:
        st.warning("Sheet Not Found")

# ==========================================
# Menu ၂။ COMPETITOR NEWS UPDATES
# ==========================================
elif menu_choice == "Competitor News Updates":
    st.markdown(
        "<h1 style='text-align: center; color: #0066cc;'>📊 Competitor News Updates </h1>",
        unsafe_allow_html=True
    )
    st.write("---")

    df_comp = load_all_sheet_data("Competitor News Updates")
    grouped_news_list = parse_news_sheet(df_comp)

    if grouped_news_list:
        st.markdown("### 🔍  ค้นหาข่าวย้อนหลัง (သတင်းများ ပြန်လည်ရှာဖွေရန်)")
        search_col1, search_col2 = st.columns(2)
        with search_col1:
            search_query = st.text_input("📝 ค้นหาด้วยหัวข้อข่าว / บริษัท / เนื้อหา (သတင်းခေါင်းစဉ် / ကုမ္ပဏီ / အကြောင်းအရာဖြင့် ရှာရန်)", "")
        with search_col2:
            search_date = st.date_input("📅 ค้นหาด้วยวันที่ (ရက်စွဲဖြင့် ရှာရန်)", value=None, format="YYYY-MM-DD")
        st.write("---")

        grouped_data = {}
        for news in grouped_news_list:
            d_key = news['date']
            grouped_data.setdefault(d_key, []).append(news)

        sorted_dates = sorted(grouped_data.keys(), reverse=True)
        filtered_grouped_data = {}

        for d_key in sorted_dates:
            if search_date is not None:
                try:
                    sheet_date_obj = pd.to_datetime(d_key).date()
                    if sheet_date_obj != search_date:
                        continue
                except Exception:
                    if str(search_date) not in d_key:
                        continue

            news_list_under_date = []
            for news in grouped_data[d_key]:
                if search_query:
                    q = search_query.lower()
                    if not (
                        q in news['company'].lower() or
                        q in news['content_th'].lower()
                    ):
                        continue
                news_list_under_date.append(news)

            if news_list_under_date:
                filtered_grouped_data[d_key] = news_list_under_date

        if filtered_grouped_data:
            current_query_state = (search_query, str(search_date))
            if (
                "news_display_count" not in st.session_state or
                st.session_state.get("news_last_query") != current_query_state
            ):
                st.session_state.news_display_count = 7
                st.session_state.news_last_query = current_query_state

            current_limit = st.session_state.news_display_count
            total_filtered_items = sum(len(v) for v in filtered_grouped_data.values())

            items_displayed = 0
            break_all = False

            with st.chat_message("assistant"):
                st.write(
                    f"🔍 ရှာဖွေမှုရလဒ် စုစုပေါင်း ({total_filtered_items}) စောင်အနက်မှ "
                    f"နောက်ဆုံးသတင်းများကို ဖော်ပြပေးလိုက်ပါတယ် ခင်ဗျာ။"
                )
                st.write("---")

                for date_key in sorted(filtered_grouped_data.keys(), reverse=True):
                    if break_all:
                        break

                    items_to_show = []
                    for news in filtered_grouped_data[date_key]:
                        if items_displayed < current_limit:
                            items_to_show.append(news)
                            items_displayed += 1
                        else:
                            break_all = True
                            break

                    if items_to_show:
                        st.markdown(
                            f"<h2 style='color: #ff6600; background-color: #f0f7ff; "
                            f"padding: 10px; border-radius: 5px;'> Date: {date_key}</h2>",
                            unsafe_allow_html=True 
                        )
                        for news in items_to_show:
                            render_news_card(news)

                if items_displayed < total_filtered_items:
                    col1, col2 = st.columns([2, 3])
                    with col1:
                        if st.button("👍 နောက်ထပ်ပြပါ / แสดงเพิ่มเติม", key="news_more_pagination_btn"):
                            st.session_state.news_display_count += 7
                            st.rerun()
                else:
                    st.info("👋 သတင်းအားလုံးကို ပြသပေးပြီးပါပြီ ခင်ဗျာ။ / แสดงข่าวทั้งหมดเรียบร้อยแล้วครับ")
        else:
            st.info("❌ ရှာဖွေမှုရလဒ်မရှိပါ။ / ไม่พบผลการค้นหา")
    else:
        st.error("Error loading data from sheet.")

# ==========================================
# Menu ၃။ KMM TRACTOR AI AGENT
# ==========================================
elif menu_choice == "KMM Tractor AI Agent":
    st.markdown(
        "<h1 style='text-align: center; color: #ff6600;'>🤖 KMM Tractor AI Agent</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center; color: #555;'>"
        "สามารถสอบถามได้โดยการคลิกเลือกคำถามสำเร็จรูป หรือใช้ตัวกรอง</p>",
        unsafe_allow_html=True
    )
    st.write("---")

    if not gemini_client:
        st.warning("⚠️ GEMINI_API_KEY မသတ်မှတ်ရသေးပါ။ Streamlit Secrets ထဲတွင် API Key ဖြည့်ပေးပါ ခင်ဗျာ။")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    st.markdown(
        "<small style='color: #888;'>💡 คุณสามารถคลิกคำถามด้านล่างเพื่อสอบถามได้ง่ายๆ ครับ -</small>",
        unsafe_allow_html=True
    )
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
    suggested_query = None

    if "dropdown_query" in st.session_state:
        suggested_query = st.session_state.pop("dropdown_query")

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
        agent_brand_list = [
            "— เลือก —", "Kubota", "Yanmar", "Win-Shwe-Wah(2nd)",
            "John-Deere", "New-Holland", "YTO", "Mahindra", "Sonalika"
        ]
        st.selectbox(
            "Brand Filter",
            options=agent_brand_list,
            key="main_page_brand_filter",
            label_visibility="collapsed",
            on_change=handle_brand_change
        )

    user_input = st.chat_input("You can access and read the news, as well as ask questions.")
    user_query = suggested_query if suggested_query else user_input

    if user_query:
        with st.chat_message("user"):
            st.markdown(user_query)
        st.session_state.messages.append({"role": "user", "content": user_query})

        tz_offset = datetime.timezone(datetime.timedelta(hours=7))
        now_local = datetime.datetime.now(tz=tz_offset)
        today_date_obj = now_local.date()
        yesterday_date_obj = today_date_obj - datetime.timedelta(days=1)

        NEWS_KEYWORDS = [
            "သတင်း", "ယနေ့", "မနေ့က", "ဒီနေ့", "စစ်ထုတ်မှု",
            "တင်ထားတာ", "competitor", "ပတ်စာ",
            "ข่าว", "รายงาน",
        ]
        is_news_intent = any(keyword in user_query for keyword in NEWS_KEYWORDS)

        q_lower = user_query.lower().strip()
        if q_lower in ("news", "report") or q_lower.startswith("news ") or q_lower.startswith("report "):
            is_news_intent = True

        if is_news_intent:
            df_comp = load_all_sheet_data("Competitor News Updates")
            all_news = parse_news_sheet(df_comp)
            matched_news_list = []

            for news in all_news:
                news_date_raw = news['date'].strip()
                company_lower = news['company'].lower()
                content_lower = news['content_th'].lower()
                match_found = False

                news_date_obj = None
                try:
                    parsed = pd.to_datetime(news_date_raw, dayfirst=False, errors='coerce')
                    if pd.notna(parsed):
                        news_date_obj = parsed.date()
                except Exception:
                    pass

                if news_date_obj is None:
                    try:
                        parsed = pd.to_datetime(news_date_raw, dayfirst=True, errors='coerce')
                        if pd.notna(parsed):
                            news_date_obj = parsed.date()
                    except Exception:
                        pass

                if "ယနေ့" in user_query or "ဒီနေ့" in user_query:
                    if news_date_obj == today_date_obj:
                        match_found = True
                elif "မနေ့က" in user_query:
                    if news_date_obj == yesterday_date_obj:
                        match_found = True
                elif "ပတ်စာ" in user_query or "report" in user_query.lower():
                    if news_date_obj is not None:
                        seven_days_ago = today_date_obj - datetime.timedelta(days=7)
                        if seven_days_ago <= news_date_obj <= today_date_obj:
                            match_found = True
                else:
                    q_words = user_query.lower().split()
                    if any(word in company_lower or word in content_lower for word in q_words):
                        match_found = True

                if match_found:
                    matched_news_list.append(news)

            with st.chat_message("assistant"):
                if matched_news_list:
                    st.markdown(f"### 📊 ရှာဖွေတွေ့ရှိရသော Competitor News ({len(matched_news_list)}) စောင်")
                    st.write("---")
                    for news in matched_news_list:
                        render_news_card(news)
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": f"📊 ရှာဖွေတွေ့ရှိရသော Competitor News ({len(matched_news_list)}) စောင်ကို ပြသပေးပြီးပါပြီ။"
                    })
                else:
                    st.info("❌ သတ်မှတ်ထားသော အချက်အလက်အပေါ် မူတည်၍ သတင်း မတွေ့ရှိရပါ။")
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": "❌ သတ်မှတ်ထားသော အချက်အလက်အပေါ် မူတည်၍ သတင်း မတွေ့ရှိရပါ။"
                    })
        else:
            with st.spinner("AI က ဖြေကြားနေပါသည်..."):
                ai_reply = ask_gemini(user_query, st.session_state.messages)
            st.markdown(ai_reply)
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
