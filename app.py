import streamlit as st
import pandas as pd

# ၁။ Page Config
st.set_page_config(page_title="KMM Kubota Price List", page_icon="🚜", layout="centered")

# Google Sheet ID
SHEET_ID = "1QqQvPKH7G0hqqhd_0V6cP40Htl8qdFEZ6nHBVe_53_g"

# --- Sidebar Menu Navigation ---
with st.sidebar:
    st.markdown("## 🚜 KMM Service")
    menu_choice = st.radio("သွားလိုရာကို ရွေးပါ -", ["Brand Selection", "Competitor Activities"])
    st.write("---")
    
    if menu_choice == "Brand Selection":
        st.header("🔍 Filter")
        selected_brand = st.selectbox(
            "အမှတ်တံဆိပ် ရွေးချယ်ပါ -", 
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
# ၁။ BRAND SELECTION MENU (စျေးနှုန်းကြည့်ရန်)
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
# ၂။ COMPETITOR ACTIVITIES MENU (သတင်းကြည့်ရန်)
# ==========================================
elif menu_choice == "Competitor Activities":
    st.markdown("<h1 style='text-align: center; color: #0066cc;'>📊 Market Updates</h1>", unsafe_allow_html=True)
    st.write("---")
    
    comp_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Competitor%20Activities"
    
    try:
        # ဒေတာဖတ်ပြီး အလွတ်များကို ဖြည့်စွက်ပါ
        df_comp = pd.read_csv(comp_url).fillna('')
        
        # စာကြောင်းခြားထားသမျှကို တစ်ခုတည်းဖြစ်အောင် ပြန်ပေါင်းမည့် Logic
        current_data = []
        temp_row = None

        for _, row in df_comp.iterrows():
            # Date ပါလာလျှင် သတင်းအသစ်တစ်ခုအဖြစ် သတ်မှတ်သည်
            if str(row['Date']).strip() != '':
                if temp_row is not None:
                    current_data.append(temp_row)
                temp_row = row.to_dict()
            else:
                # Date မပါလျှင် အပေါ်ကသတင်း၏ စာသားအဆက်အဖြစ် ပေါင်းထည့်သည်
                if temp_row is not None and str(row['Content']).strip() != '':
                    temp_row['Content'] = str(temp_row['Content']) + "\n" + str(row['Content'])
        
        # နောက်ဆုံးသတင်းကို ထည့်သွင်းခြင်း
        if temp_row is not None:
            current_data.append(temp_row)

        # သတင်းများကို Card ပုံစံဖြင့် ပြသခြင်း
        if not current_data:
            st.info("ယနေ့အတွက် သတင်းအချက်အလက်များ မရှိသေးပါ။")
        else:
            # ရက်စွဲအလိုက် အသစ်ဆုံးကို အပေါ်တင်ရန် (Sorting)
            current_data.sort(key=lambda x: str(x['Date']), reverse=True)

            for news in current_data:
                with st.container(border=True):
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        st.subheader(f"🏢 {news['Company']}")
                    with col_b:
                        st.caption(f"📅 {news['Date']}")
                    
                    st.write("**Description:**")
                    st.write(news['Content'])
                    
                    # Promo ရှိမှသာ ပြမည်
                    if str(news['Promo']).strip() not in ['', '0']:
                        st.info(f"💡 {news['Promo']}")
                    
                    # Facebook Link ရှိမှသာ ပြမည်
                    if str(news['Link']).startswith("http"):
                        st.link_button("Facebook တွင်ကြည့်ရန်", news['Link'])
                st.write("") 
            
    except Exception as e:
        st.error(f"ဒေတာဖတ်ရာတွင် အမှားအယွင်းရှိနေပါသည်: {e}")

st.markdown("<br><hr><center><small>© 2026 KMM Service Co., Ltd.</small></center>", unsafe_allow_html=True)
















