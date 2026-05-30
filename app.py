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
# ၁။ BRAND SELECTION MENU (စက်ဈေးနှုန်း + SALE MEMO PRINT)
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
        chosen_attachments = [] 
        
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
                                options.append({"model_name": str(row[m_col]), "label": f"{row[m_col]} (+{p:,.0f} MMK)", "price": p})
                            except: continue
                    if options:
                        c = st.selectbox(f"{label}:", ["မယူပါ"] + [o["label"] for o in options], key=f"{label}_{selected_model}")
                        if c != "မယူပါ":
                            selected_item = next(item for item in options if item["label"] == c)
                            chosen_attachments.append({"type": label, "model": selected_item["model_name"], "price": selected_item["price"]})
                            return selected_item["price"]
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
        
        # --- 🖨️ SALE MEMO GENERATOR ---
        st.write("---")
        st.subheader("📋 Sale Memo / Quotation ထုတ်ရန်")
        
        customer_name = st.text_input("ဝယ်ယူသူအမည် (Customer Name):", placeholder="ဦးမောင်မောင်")
        memo_remark = st.text_area("မှတ်ချက် / မှတ်စု (Remark):", placeholder="ဥပမာ - အပိုလက်ဆောင် ပေးရန်ရှိသည်များ...")
        
        today_str = datetime.date.today().strftime("%d-%b-%Y")
        
        items_rows_html = f"""
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">1</td>
            <td style="padding: 10px; border: 1px solid #ddd;"><b>{selected_brand} Tractor</b><br>Model: {selected_model}</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">{base_price:,.0f} MMK</td>
        </tr>
        """
        
        for idx, att in enumerate(chosen_attachments, start=2):
            items_rows_html += f"""
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">{idx}</td>
                <td style="padding: 10px; border: 1px solid #ddd;"><b>{att['type']}</b><br>Model: {att['model']}</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">{att['price']:,.0f} MMK</td>
            </tr>
            """
            
        memo_html = f"""
        <div id="printArea" style="font-family: Arial, sans-serif; padding: 25px; border: 2px solid #ff6600; border-radius: 8px; background-color: #fff; color: #333;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #ff6600; margin: 0;">KMM KUBOTA HEAVY MACHINERY</h2>
                <p style="margin: 5px 0; font-size: 14px; color: #666;">စက်ကိရိယာနှင့် နောက်တွဲယာဉ် အရောင်းဌာန</p>
                <h3 style="margin: 10px 0; border-bottom: 2px solid #ff6600; padding-bottom: 5px; display: inline-block;">SALE MEMO / QUOTATION</h3>
            </div>
            
            <table style="width: 100%; font-size: 14px; margin-bottom: 20px;">
                <tr>
                    <td><b>ဝယ်ယူသူအမည်:</b> {customer_name if customer_name else '-'}</td>
                    <td style="text-align: right;"><b>ရက်စွဲ:</b> {today_str}</td>
                </tr>
                <tr>
                    <td><b>အမှတ်တံဆိပ်:</b> {selected_brand}</td>
                    <td style="text-align: right;"><b>အခြေအနေ:</b> စျေးနှုန်းစိစစ်ချက်</td>
                </tr>
            </table>
            
            <table style="width: 100%; border-collapse: collapse; font-size: 14px; margin-bottom: 20px;">
                <thead>
                    <tr style="background-color: #ff6600; color: white;">
                        <th style="padding: 10px; border: 1px solid #ddd; text-align: left; width: 10%;">စဉ်</th>
                        <th style="padding: 10px; border: 1px solid #ddd; text-align: left; width: 60%;">အမျိုးအမည် / မော်ဒယ်</th>
                        <th style="padding: 10px; border: 1px solid #ddd; text-align: right; width: 30%;">စျေးနှုန်း (MMK)</th>
                    </tr>
                </thead>
                <tbody>
                    {items_rows_html}
                    <tr style="background-color: #f9f9f9; font-weight: bold;">
                        <td colspan="2" style="padding: 10px; border: 1px solid #ddd; text-align: right;">စုစုပေါင်း ကျသင့်ငွေ:</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: right; color: #ff6600; font-size: 16px;">{grand_total:,.0f} MMK</td>
                    </tr>
                </tbody>
            </table>
            
            {f'<div style="margin-top: 15px; font-size: 13px; background: #f5f5f5; padding: 10px; border-radius: 4px;"><b>မှတ်ချက်:</b> {memo_remark}</div>' if memo_remark else ''}
        </div>
        """
        
        with st.expander("👀 Sale Memo Preview ကိုကြည့်ရန်", expanded=True):
            st.markdown(memo_html, unsafe_allow_html=True)
            
        st.write("<br>", unsafe_allow_html=True)
        print_btn_html = f"""
        <script>
        function printDiv() {{
            var printContents = document.getElementById('printArea').innerHTML;
            var originalContents = document.body.innerHTML;
            document.body.innerHTML = printContents;
            window.print();
            document.body.innerHTML = originalContents;
            window.location.reload();
        }}
        </script>
        <button onclick="printDiv()" style="width: 100%; background-color: #4CAF50; color: white; padding: 12px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: bold;">
            🖨️ စာရွက်ထုတ်ရန် / PDF သိမ်းရန် (Print Memo)
        </button>
        """
        st.components.v1.html(print_btn_html, height=60)
        
    else:
        st.warning("Sheet Not Found")

# ==========================================
# ၂။ COMPETITOR NEWS UPDATES MENU (စာသား၊ ပုံနှင့် Social Links အားလုံးပြသပေးသည့်အပိုင်း)
# ==========================================
elif menu_choice == "Competitor News Updates":
    st.markdown("<h1 style='text-align: center; color: #0066cc;'>📊 Competitor News Updates & News Myanmar</h1>", unsafe_allow_html=True)
    st.write("---")
    
    tab_view, tab_post = st.tabs(["📌 သတင်းများ ဖတ်ရှုရန်", "✍️ သတင်းအသစ်တင်ရန် (Post)"])
    
    timestamp = int(time.time())
    comp_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Competitor%20News%20Updates&cache_bust={timestamp}"
    
    # --- TAB 1: သတင်းများဖတ်ရှုရန် ---
    with tab_view:
        st.markdown("## 📰 Sheet ထဲရှိ နေ့စဉ်တင်ထားသော သတင်းများ")
        
        try:
            # Google Sheet ဒေတာကို ကော်လံအပြည့် ဖတ်ခြင်း
            df_comp = pd.read_csv(comp_url).fillna('')
            df_comp.columns = [str(c).strip().lower() for c in df_comp.columns]
            
            current_date = "No Date"
            
            for idx, row in df_comp.iterrows():
                r_date = str(row.get('date', '')).strip()
                r_company = str(row.get('company', '')).strip()
                r_content_th = str(row.get('content_th', '')).strip()
                r_content_mm = str(row.get('content_mm', '')).strip()
                r_promo = str(row.get('promo', '')).strip()
                
                # Social Links များနှင့် ပုံလင့်ခ်ကို တိုက်ရိုက်ရယူခြင်း
                r_fb = str(row.get('facebook', '')).strip()
                r_tt = str(row.get('tiktok', '')).strip()
                r_tg = str(row.get('telegram', '')).strip()
                r_image = str(row.get('image_url', '')).strip()
                
                # အားလုံး ဗလာဖြစ်နေလျှင် ကျော်သွားမည်
                if not r_date and not r_company and not r_content_th and not r_content_mm:
                    continue
                
                # ရက်စွဲအသစ်တွေ့ရင် ခေါင်းစဉ်တပ်မည်
                if r_date:
                    current_date = r_date
                    st.markdown(f"<h3 style='color: #ff6600; background-color: #f0f7ff; padding: 10px; border-radius: 5px; margin-top: 20px;'>📅 ရက်စွဲ: {current_date}</h3>", unsafe_allow_html=True)
                
                # သတင်းကတ်ပြားပုံစံ ဖန်တီးပြသခြင်း
                with st.container(border=True):
                    # ခေါင်းစဉ် (Company)
                    title_display = r_company if r_company else "💵 Exchange Rate / News Updates"
                    st.markdown(f"#### 🏢 {title_display}")
                    
                    # ထိုင်းဘာသာစာသား ပြသခြင်း
                    if r_content_th:
                        st.markdown("**🇹🇭 ภาษาไทย:**")
                        st.write(r_content_th)
                    
                    if r_content_th and r_content_mm:
                        st.write("---")
                        
                    # မြန်မာဘာသာစာသား ပြသခြင်း
                    if r_content_mm:
                        st.markdown("**🇲🇲 မြန်မာဘာသာ:**")
                        st.write(r_content_mm)
                        
                    # ပရိုမိုးရှင်း ရှိလျှင်ပြမည်
                    if r_promo and r_promo != '0':
                        st.info(f"💡 **Promo:** {r_promo}")
                        
                    # 🖼️ ပုံလင့်ခ်ပါဝင်ပါက ပုံကို App ထဲ၌ တိုက်ရိုက်ဆွဲပြခြင်း
                    if r_image and r_image.startswith("http"):
                        st.image(r_image, use_container_width=True)
                    
                    # 🔗 Facebook, TikTok, Telegram Link များအတွက် ခလုတ်များ ဖန်တီးခြင်း
                    if (r_fb and r_fb.startswith("http")) or (r_tt and r_tt.startswith("http")) or (r_tg and r_tg.startswith("http")):
                        st.write("---")
                        btn_col1, btn_col2, btn_col3 = st.columns(3)
                        if r_fb and r_fb.startswith("http"):
                            with btn_col1: st.link_button("🔵 Facebook သို့သွားရန်", r_fb, use_container_width=True)
                        if r_tt and r_tt.startswith("http"):
                            with btn_col2: st.link_button("⚫ TikTok သို့သွားရန်", r_tt, use_container_width=True)
                        if r_tg and r_tg.startswith("http"):
                            with btn_col3: st.link_button("✈️ Telegram သို့သွားရန်", r_tg, use_container_width=True)
                            
        except Exception as e:
            st.error(f"Error loading news: {e}")

    # --- TAB 2: သတင်းအသစ်တင်ရန် ---
    with tab_post:
        st.markdown("## ✍️ သတင်းအချက်အလက်အသစ် တင်ရန် (Post)")
        
        with st.form("news_post_form", clear_on_submit=True):
            post_date = st.date_input("ရက်စွဲရွေးချယ်ရန် (Date):", datetime.date.today())
            post_company = st.text_input("ကုမ္ပဏီ / ခေါင်းစဉ် (Company/Title):", placeholder="ဥပမာ - Voice of Myanmar, Win Shwe Wah")
            post_content_th = st.text_area("သတင်းအကြောင်းအရာ (ภาษาไทย):", placeholder="กรอกเนื้อหาข่าวภาษาไทย...")
            post_content_mm = st.text_area("သတင်းအကြောင်းအရာ (မြန်မာဘာသာ):", placeholder="မြန်မာဘာသာဖြင့် ရေးသားရန်...")
            post_promo = st.text_input("ပရိုမိုးရှင်း အချက်အလက် (Promo):", placeholder="ဥပမာ - Promotion - 20,000 THB")
            post_img_url = st.text_input("ပုံ Link (Image URL):", placeholder="https://i.postimg.cc/...")
            
            col_b1, col_b2, col_b3 = st.columns(3)
            post_fb = col_b1.text_input("Facebook Link:")
            post_tt = col_b2.text_input("TikTok Link:")
            post_tg = col_b3.text_input("Telegram Link:")
            
            submit_btn = st.form_submit_button("🚀 သတင်း အချက်အလက် တင်မည် (Post Now)", type="primary")
            
            if submit_btn:
                if post_company or post_content_mm or post_content_th:
                    st.success("🎯 သတင်းပေးပို့မှု စနစ်သို့ ရောက်ရှိသွားပါပြီ!")
                    st.balloons()
                else:
                    st.warning("⚠️ ကျေးဇူးပြု၍ အချက်အလက်တစ်ခုခု ဖြည့်စွက်ပေးပါ ခင်ဗျာ။") 














