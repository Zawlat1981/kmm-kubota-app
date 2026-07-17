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
# ၁.၁ CSS — Wide layout + Responsive News Grid
# ========================================== 
st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100% !important;
    }
    .news-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
        gap: 16px;
        margin-bottom: 20px;
    }
    .news-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 16px;
        background: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        overflow-wrap: break-word;
    }
    .news-card h3 {
        margin: 0;
    }
    .news-card hr {
        margin: 8px 0;
    }
    .news-card img {
        width: 100%;
        border-radius: 6px;
        margin-top: 8px;
        display: block;
    }
    .news-links {
        margin-top: 10px;
    }
    .news-links a {
        display: inline-block;
        margin-right: 8px;
        margin-top: 6px;
        padding: 6px 14px;
        border-radius: 6px;
        text-decoration: none;
        font-size: 13px;
        color: white !important;
    }
    .fb-link { background:#1877F2; }
    .tt-link { background:#000000; }
    .tg-link { background:#229ED9; }
    .promo-box {
        background:#eef6ff;
        padding:8px;
        border-radius:6px;
        margin-top:8px;
    }

    @media (max-width: 640px) {
        .news-grid {
            grid-template-columns: 1fr;
        }
        .block-container {
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

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
    """UI Brand Selection အတွက် Tractor နှင့် Attachment ဒေတာ Load လုပ်သည်"""
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
    """AI Agent နှင့် News အတွက် Sheet ဒေတာ Load လုပ်သည်"""
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
    """
    Competitor News Sheet ကို Grouped News List အဖြစ် ပြောင်းပေးသည်။
    Menu 2 နှင့် AI Agent နှစ်ခုလုံးအတွက် အသုံးပြုနိုင်သည်။
    """
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
                'image_url': str(row.get('image_url', '')).strip(),
            }
        else:
            if last_news_item is not None:
                if r_content_th:
                    last_news_item['content_th'] = (last_news_item['content_th'] + "\n" + r_content_th).strip()
                if r_content_mm:
                    last_news_item['content_mm'] = (last_news_item['content_mm'] + "\n" + r_content_mm).strip()
                for field in ['image_url', 'promo', 'facebook', 'tiktok', 'telegram']:
                    val = str(row.get(field, '')).strip()
                    if val:
                        last_news_item[field] = val
            else:
                last_news_item = {
                    'date': current_date,
                    'company': '💵 Exchange Rate / News',
                    'content_th': r_content_th,
                    'content_mm': r_content_mm,
                    'promo': str(row.get('promo', '')).strip(),
                    'facebook': str(row.get('facebook', '')).strip(),
                    'tiktok': str(row.get('tiktok', '')).strip(),
                    'telegram': str(row.get('telegram', '')).strip(),
                    'image_url': str(row.get('image_url', '')).strip(),
                }

    if last_news_item is not None:
        grouped_news.append(last_news_item)

    return grouped_news


# ==========================================
# ၄.၁ News Card Rendering — Responsive Grid (HTML/CSS based)
# ==========================================
def _news_card_html(news):
    """တစ်ခုချင်းစီအတွက် News Card HTML string ကို ပြင်ဆင်သည်"""
    c_th = news.get('content_th', '').strip()
    c_mm = news.get('content_mm', '').strip()

    content_html = ""
    if c_th:
        content_html += f"<b>🇹🇭 ภาษาไทย</b><p>{c_th.replace(chr(10), '<br>')}</p>"
    if c_th and c_mm:
        content_html += "<hr>"
    if c_mm:
        content_html += f"<b>🇲🇲 မြန်မာဘာသာ</b><p>{c_mm.replace(chr(10), '<br>')}</p>"

    img_html = ""
    img_data = news.get('image_url', '').strip()
    if img_data:
        img_list = [i.strip() for i in img_data.split(',') if i.strip().startswith('http')]
        for img in img_list:
            img_html += (
                f'<a href="{img}" target="_blank">'
                f'<img src="{img}" alt="news image"></a>'
            )

    promo = str(news.get('promo', '')).strip()
    promo_html = ""
    if promo and promo not in ('0', '0.0', 'nan', 'None', ''):
        promo_html = f"<div class='promo-box'>💡 {promo}</div>"

    fb_link = news.get('facebook', '').strip()
    tt_link = news.get('tiktok', '').strip()
    tg_link = news.get('telegram', '').strip()

    links_html = "<div class='news-links'>"
    if fb_link.startswith("http"):
        links_html += f'<a class="fb-link" href="{fb_link}" target="_blank">🔵 Facebook</a>'
    if tt_link.startswith("http"):
        links_html += f'<a class="tt-link" href="{tt_link}" target="_blank">⚫ TikTok</a>'
    if tg_link.startswith("http"):
        links_html += f'<a class="tg-link" href="{tg_link}" target="_blank">✈️ Telegram</a>'
    links_html += "</div>"

    return f"""
    <div class="news-card">
        <h3 style="color:#0066cc;">🏢 {news['company']}</h3>
        <small style="color:#888;">📅 Date: {news['date']}</small>
        <hr>
        {content_html}
        {img_html}
        {promo_html}
        {links_html}
    </div>
    """


def render_news_grid(news_list):
    """News list တစ်ခုလုံးကို Responsive Grid အဖြစ် တစ်ခါတည်း render လုပ်သည်
    ဖုန်းပေါ်တွင် ၁ Column၊ Screen ကျယ်လာသည်နှင့် ၂-၃ Column အလိုအလျောက် ကျယ်လာမည်"""
    if not news_list:
        return
    cards_html = "".join(_news_card_html(n) for n in news_list)
    st.markdown(f'<div class="news-grid">{cards_html}</div>', unsafe_allow_html=True)


# ==========================================
# ၅။ Google Gemini / Groq API Setup (Free tier)
# ==========================================
GEMINI_SYSTEM_INSTRUCTION = (
    "မင်းက KMM Kubota ကုမ္ပဏီက AI Assistant ဖြစ်တယ်။ "
    "KMM Kubota ကုမ္ပဏီက Kubota ထွန်စက်၊ ရိတ်သိမ်းခြွေ့လှေ့စက်၊ ကောက်စိုက်စက်၊ မြေတူးစက် တို့ကိုရောင်းချသောကုမ္ပဏီဖြစ်သည်။ "
    "ထိုင်းနိုင်ငံနှင့် မြန်မာနိုင်ငံတွင်ကုမ္ပဏီများရှိသည်။ "
    "မင်းက လယ်ယာသုံးစက်ပစ္စည်း၊ ဈေးကွက်နှင့် "
    "အခြားအထွေထွေမေးခွန်းများကို မြန်မာ/ထိုင်းဘာသာဖြင့် "
    "ရှင်းလင်းယဉ်ကျေးစွာ ဖြေကြားပေးပါ။"
    "မင်းကို မြန်မာလိုမေးရင် မြန်မာလိုဖြေပါ "
    "မင်းကို ထိုင်းလိုမေးရင် ထိုင်းလိုဖြေပါ "
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
        else:
            pass

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
        "<h1 style='text-align: center; color: #0066cc;'>📊 Competitor News Updates & News Myanmar</h1>",
        unsafe_allow_html=True
    )
    st.write("---")

    df_comp = load_all_sheet_data("Competitor News Updates")
    grouped_news_list = parse_news_sheet(df_comp)

    if grouped_news_list:
        st.markdown("### 🔍 သတင်းများ ပြန်လည်ရှာဖွေရန် / ค้นหาข่าวย้อนหลัง")
        search_col1, search_col2 = st.columns(2)
        with search_col1:
            search_query = st.text_input("📝 သတင်းခေါင်းစဉ် / ကုမ္ပဏီ / အကြောင်းအရာဖြင့် ရှာရန်", "")
        with search_col2:
            search_date = st.date_input("📅 ရက်စွဲဖြင့် ရှာရန်", value=None, format="YYYY-MM-DD")
        st.write("---")

        # Grouping by date_key
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
                        q in news['content_th'].lower() or
                        q in news['content_mm'].lower()
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
                        render_news_grid(items_to_show)

                if items_displayed < total_filtered_items:
                    col1, col2 = st.columns([2, 3])
                    with col1:
                        if st.button("👍 မှန်ပါတယ်၊ နောက်ထပ်ပြပါ / ถูกต้อง แสดงเพิ่มเติม", key="news_more_pagination_btn"):
                            st.session_state.news_display_count += 7
                            st.rerun()
                    with col2:
                        if st.button("👎 မဟုတ်ပါဘူး၊ တခြားဟာရှာမယ် / ไม่ใช่ ค้นหาอย่างอื่น", key="news_stop_pagination_btn"):
                            st.write("🤖 လူကြီးမင်း သိလိုသော အကြောင်းအရာကို ထပ်မံ အသေးစိတ် ရိုက်ထည့်ပေးပါ ခင်ဗျာ။")
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
        st.warning("⚠️ GEMINI_API_KEY မသတ်မှတ်ရသေးပါ။ Streamlit Secrets ထဲတွင် GEMINI_API_KEY ဖြည့်ပေးပါ ခင်ဗျာ။")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- Quick Buttons ---
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

    # --- Filter Expander ---
    filter_date = None
    filter_company = ""

    with st.expander("🔍 ရွေးချယ်စရာများ (ค้นหาข่าวตามวันที่หรือชื่อบริษัท)", expanded=True):
        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            filter_date = st.date_input("📅 เลือกวันที่ (Date)", value=None, format="YYYY-MM-DD")
        with col_filter2:
            filter_company = st.text_input(
                "🏢 กรอกชื่อบริษัท/องค์กร (ဥပမာ - Win Shwe Wah, Kubota)", value=""
            ).strip()

        if st.button("🔎 ค้นหาด้วยข้อมูลที่เลือก", type="primary", use_container_width=True):
            if filter_date is not None and filter_company:
                suggested_query = (
                    f"သတင်း စစ်ထုတ်မှု: {filter_date.strftime('%Y-%m-%d')} ရက်စွဲရှိ {filter_company} သတင်း"
                )
            elif filter_date is not None:
                suggested_query = f"သတင်း စစ်ထုတ်မှု: {filter_date.strftime('%Y-%m-%d')} ရက်စွဲရှိ သတင်းများ"
            elif filter_company:
                suggested_query = f"သတင်း စစ်ထုတ်မှု: {filter_company} ကုမ္ပဏီ၏ သတင်းများ"
            else:
                st.info("💡 ရက်စွဲတစ်ခု ရွေးချယ်ပေးပါ သို့မဟုတ် ကုမ္ပဏီအမည် ရိုက်ထည့်ပေးပါ ခင်ဗျာ။")

    # --- Chat Input ---
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

        # ==========================================================
        # Mode A — စက်မော်ဒယ် / ဈေးနှုန်း ရှာဖွေခြင်း
        # ==========================================================
        if not is_news_intent:
            found_tractor_data = []
            q_clean = "".join(user_query.split()).lower().replace("-", "").replace("_", "")

            with st.spinner("စက်ပစ္စည်းနှင့် ဈေးနှုန်းဒေတာများကို ရှာဖွေနေပါသည်..."):
                for brand in ALL_BRANDS:
                    df_brand = load_all_sheet_data(brand)
                    if df_brand is None or df_brand.empty:
                        continue

                    brand_clean = brand.lower().replace("-", "").replace("_", "")
                    q_model_only = q_clean.replace(brand_clean, "")

                    for _, row in df_brand.iterrows():
                        model_name = str(row.iloc[0]).strip()
                        if model_name in ["0", "0.0", "nan", "Model", ""]:
                            continue

                        model_clean = "".join(model_name.split()).lower().replace("-", "").replace("_", "")

                        match = False
                        if q_model_only:
                            if q_model_only in model_clean or model_clean in q_model_only:
                                match = True
                        else:
                            if brand.lower() in user_query.lower():
                                match = True

                        if match:
                            found_tractor_data.append({
                                "brand": brand,
                                "model": model_name,
                                "price": str(row.iloc[1]),
                                "image": str(row.iloc[2]) if len(row) > 2 else "",
                            })

            with st.chat_message("assistant"):
                if found_tractor_data:
                    st.markdown(f"### 🚜 {user_query} အတွက် ရှာဖွေတွေ့ရှိရသော မော်ဒယ်များနှင့် ဈေးနှုန်းများ")
                    st.write("---")

                    for idx, item in enumerate(found_tractor_data):
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.markdown(f"### {idx + 1}။ **{item['model']}**")
                            st.markdown(f"• **Brand:** {item['brand']}")
                            try:
                                p_val = float(str(item['price']).replace(',', '').strip())
                                st.markdown(
                                    f"• **အခြေခံဈေးနှုန်း:** "
                                    f"<span style='color:#ff6600; font-size:22px; font-weight:bold;'>"
                                    f"{p_val:,.0f}</span> MMK",
                                    unsafe_allow_html=True
                                )
                            except Exception:
                                st.markdown(f"• **ဈေးနှုန်း:** {item['price']} MMK")
                        with col2:
                            if item['image'] and item['image'].startswith("http"):
                                st.image(item['image'], use_container_width=True)
                        st.write("---")

                    try:
                        ai_reply = ask_gemini(
                            "စက်ဈေးနှုန်းပြပြီးပြီဖြစ်လို့ ဘာများ ထပ်မံကူညီပေးရမလဲလို့ မြန်မာလို ယဉ်ကျေးစွာ မေးပေးပါ။",
                            st.session_state.messages
                        )
                        st.info(ai_reply)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"🚜 {user_query} စက်ဈေးနှုန်းများကို ပြသပေးပြီးပါပြီ။",
                        })
                    except Exception as e:
                        st.warning(f"AI ဖြေကြားမှု မအောင်မြင်ပါ: {e}")

                else:
                    with st.spinner("AI က ဖြေကြားနေပါသည်..."):
                        ai_reply = ask_gemini(user_query, st.session_state.messages)
                    st.markdown(ai_reply)
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})

        # ==========================================================
        # Mode B — Competitor News ရှာဖွေပြသခြင်း
        # ==========================================================
        else:
            status_placeholder = st.empty()
            status_placeholder.text("⏳ Competitor News Updates ရှီတ်ထဲမှ အချက်အလက်များကို စုစည်းနေပါသည်...")

            df_comp = load_all_sheet_data("Competitor News Updates")
            all_news = parse_news_sheet(df_comp)

            status_placeholder.empty()

            matched_news_list = []

            for news in all_news:
                news_date_raw = news['date'].strip()
                company_lower = news['company'].lower()
                content_lower = (news['content_mm'] + news['content_th']).lower()
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

                if "စစ်ထုတ်မှု" in user_query:
                    match_date_ok = True
                    match_company_ok = True

                    if filter_date is not None:
                        match_date_ok = (news_date_obj == filter_date) if news_date_obj else False

                    if filter_company:
                        f_co = filter_company.lower()
                        match_company_ok = (f_co in company_lower or f_co in content_lower)

                    if match_date_ok and match_company_ok:
                        match_found = True

                elif "ယနေ့" in user_query or "ဒီနေ့" in user_query:
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
                    st.markdown(
                        f"### 📊 ရှာဖွေတွေ့ရှိရသော Competitor News ({len(matched_news_list)}) စောင်"
                    )
                    st.write("---")
                    render_news_grid(matched_news_list)

                    try:
                        ai_reply = ask_gemini(
                            "သတင်းများကို ပြသပေးပြီးပြီ။ မြန်မာလို ယဉ်ကျေးစွာ အကျဉ်းချုပ်ပြောကြားပေးပါ။",
                            st.session_state.messages
                        )
                        st.info(ai_reply)
                    except Exception as e:
                        st.warning(f"AI ဖြေကြားမှု မအောင်မြင်ပါ: {e}")

                else:
                    with st.spinner("AI က ဖြေကြားနေပါသည်..."):
                        ai_reply = ask_gemini(user_query, st.session_state.messages)
                    st.markdown(ai_reply)
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
