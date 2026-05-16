import streamlit as st
import pandas as pd

# ၁။ Page Config
st.set_page_config(page_title="KMM Kubota Price List", page_icon="🚜", layout="centered")

# Google Sheet ID (Tractor Price & Competitor Activities)
SHEET_ID = "1QqQvPKH7G0hqqhd_0V6cP40Htl8qdFEZ6nHBVe_53_g"

# --- Sidebar Menu Navigation ---
with st.sidebar:
    st.markdown("## 🚜 KMM Service")
    # Menu ရွေးချယ်မှု
    menu_choice = st.radio("သွားလိုရာကို ရွေးပါ -", ["Brand Selection", "Competitor Activities"])
    st.write("---")
    
    # Brand Selection ကို ရွေးထားမှသာ အမှတ်တံဆိပ်ရွေးခိုင်းမယ်
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
# ၁။ BRAND SELECTION MENU
# ==========================================
if menu_choice == "Brand Selection":
    df_tractor, df_attach = load_data(selected_brand)

    if not df_tractor.empty:
        st.markdown("<h1 style='text-align: center; color: #ff6600;'>🚜 KMM Kubota Price List</h1>", unsafe_allow_html=True)

        # နိုင်ငံအမည် သတ်မှတ်ခြင်း
        if selected_brand in ["John-Deere", "New-Holland", "Mahindra", "Sonalika"]:
            origin = "Indian"
        elif selected_brand in ["YTO", "Yamabisi", "DongFeng"]:
            origin = "China"
        elif selected_brand == "Kubota":
            origin = "Japan/Thailand"
        elif selected_brand == "Yanmar":
            origin = "Japan"
        else:
            origin = ""

        display_text = f"({selected_brand} Brand - {origin})" if origin else f"({selected_brand} Brand)"
        st.markdown(f"<p style='text-align: center; color: #555; font-weight: bold;'>{display_text}</p>", unsafe_allow_html=True)
        st.write("---") 

        # စက်မော်ဒယ် ရွေးချယ်ခြင်း
        model_list = df_tractor.iloc[:, 0].astype(str).tolist()
        model_list = [m for m in model_list if m not in ["0", "0.0", "nan", "Model"]]
        selected_model = st.selectbox(f"{selected_brand} မော်ဒယ်ကို ရွေးပါ -", model_list)
        
        t_info = df_tractor[df_tractor.iloc[:, 0].astype(str) == selected_model].iloc[0]
        
        try:
            raw_p = str(t_info.iloc[1]).replace(',', '').strip()
            base_price = float(raw_p) if raw_p != "" else 0
        except:
            base_price = 0
        img_url = str(t_info.iloc[2])

        if img_url and img_url.startswith("http"):
            st.image(img_url, use_container_width=True)

        st.markdown(f"### 💰 စက်ဈေးနှုန်း: **{base_price:,.0f}** MMK")
        st.write("---")

        # နောက်တွဲများ ရွေးချယ်ရန်
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
                        c = st.selectbox(f"{label}:", ["မယူပါ"] + [o["label"] for o in options])
                        if c != "မယူပါ":
                            return next(item["price"] for item in options if item["label"] == c)
                return 0

            col1, col2 = st.columns(2)
            with col1:
                selected_att_total += add_att_ui("Rotary", "Rotary_Model1", "Rotary_Price")
                selected_att_total += add_att_ui("Disc Harrow", "Harrow_Model1", "Harrow_Price")
                selected_att_total += add_att_ui("Disc Plow", "Plow_Model1", "Plow_Price")
            with col2:
                selected_att_total += add_att_ui("Combine Attach", "Combine_Model1", "Combine_Price")
                selected_att_total += add_att_ui("Breaker", "Breaker_Model1", "Breaker_Price")
                selected_att_total += add_att_ui("Sowing", "Transplanter_Model1", "Transplanter_Price")
        else:
            st.info("ဤ Brand အတွက် နောက်တွဲပစ္စည်းစာရင်း မရှိသေးပါ။")

        # စုစုပေါင်း
        grand_total = base_price + selected_att_total
        st.write("---")
        st.success(f"## 📄 စုစုပေါင်းကျသင့်ငွေ: {grand_total:,.0f} MMK")
        st.info(f"စက်ဈေး: {base_price:,.0f} + နောက်တွဲ: {selected_att_total:,.0f}")
    else:
        st.warning(f"Google Sheet ထဲမှာ '{selected_brand}' ဆိုတဲ့ Tab ကို မတွေ့ပါဘူး။")

# ==========================================
# ၂။ COMPETITOR ACTIVITIES MENU
# ==========================================
elif menu_choice == "Competitor Activities":
    st.markdown("<h1 style='text-align: center; color: #0066cc;'>📊 Competitor Activities</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # Competitor Sheet URL
    sheet_name = "Competitor%20Activities"
    comp_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    
    try:
        df_comp = pd.read_csv(comp_url)
        # Date column ကို အသုံးပြု၍ အသစ်ဆုံးကို အပေါ်တင်ရန် စီခြင်း
        df_comp = df_comp.sort_values(by='Date', ascending=False)
        
        st.dataframe(
            df_comp,
            column_config={
                "Date": st.column_config.DateColumn("ရက်စွဲ"),
                "Company": "ကုမ္ပဏီ",
                "Content": st.column_config.TextColumn("အကြောင်းအရာ", width="large"),
                "Promo": "ပရိုမိုးရှင်း/ဈေးနှုန်း",
                "Link": st.column_config.LinkColumn("Link", display_text="Facebook တွင်ကြည့်ရန်")
            },
            hide_index=True,
            use_container_width=True
        )
    except Exception as e:
        st.error("သတင်းအချက်အလက်များကို ခေါ်ယူ၍မရပါ။ Google Sheet Tab နာမည် မှန်၊ မမှန် စစ်ဆေးပေးပါ။")

st.markdown("<br><hr><center><small>© 2026 KMM Service Co., Ltd.</small></center>", unsafe_allow_html=True)
















