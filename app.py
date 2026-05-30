import streamlit as st
import pandas as pd
from datetime import datetime

# ==============================================================================
# ⚙️ အပိုင်း (၁) - PAGE CONFIGURATION & NAVIGATION SETUP
# ==============================================================================
st.set_page_config(page_title="Good Brother Co., Ltd", page_icon="🚜", layout="centered")

# --- SIDEBAR NAVIGATION (စာမျက်နှာ ရွေးချယ်မှုကဏ္ဍ) ---
st.sidebar.markdown("## 🧭 Navigation")
page_selection = st.sidebar.radio(
    "သွားလိုသည့် စာမျက်နှာကို ရွေးပါ -",
    ["🚜 Price List & Sales Memo", "📰 Competitor News Update"]
)

# --- SIDEBAR BRAND SELECTION ---
st.sidebar.markdown("---")
st.sidebar.header("🚜 Brand Selection")
selected_brand = st.sidebar.selectbox(
    "အမှတ်တံဆိပ် ရွေးချယ်ပါ -", 
    ["Kubota", "Yanmar", "Win-Shwe-Wah(2nd)", "John-Deere", "New-Holland", "YTO", "Mahindra", "Sonalika", "Yamabisi", "DongFeng"]
)

# Google Sheet ID
SHEET_ID = "1QqQvPKH7G0hqqhd_0V6cP40Htl8qdFEZ6nHBVe_53_g"

@st.cache_data(ttl=10)
def load_data(tab_name):
    """ Google Sheet မှ ဒေတာများကို ပုံမှန်အတိုင်း အော်တိုဆွဲဖတ်သည့်စနစ် """
    base_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet="
    
    # စက်ပစ္စည်းစျေးနှုန်းစာမျက်နှာ ဖတ်ခြင်း
    try:
        df_tractor = pd.read_csv(base_url + tab_name).fillna(0)
    except:
        df_tractor = pd.DataFrame()

    # နောက်တွဲပစ္စည်းစာမျက်နှာ ဖတ်ခြင်း
    df_attach = pd.DataFrame() 
    if tab_name in ["Kubota", "Yanmar"]:
        attachment_tab = f"Attachments_{tab_name}"
        try:
            df_attach = pd.read_csv(base_url + attachment_tab).fillna(0)
        except:
            pass
            
    # News စာမျက်နှာကို ဖတ်ခြင်း (Column ခေါင်းစဉ်များကို သေချာရှင်းလင်းအောင် လုပ်ဆောင်ပါသည်)
    try:
        df_news = pd.read_csv(base_url + "News").fillna("")
        # ကော်လံအမည်များ သတ်မှတ်ရလွယ်ကူစေရန် သန့်စင်ခြင်း
        if not df_news.empty and len(df_news.columns) >= 4:
            df_news.columns = ['ID', 'Date', 'Title', 'Detail', 'Image'] + list(df_news.columns[5:])
    except:
        df_news = pd.DataFrame()
        
    return df_tractor, df_attach, df_news

# ဒေတာများ စတင်ခေါ်ယူခြင်း
df_tractor, df_attach, df_news = load_data(selected_brand)


# ==============================================================================
# 🧠 AUTOMATIC CODE & NAME SPLITTING LOGIC
# ==============================================================================
def get_machine_details(model_name):
    model_upper = str(model_name).upper().strip()
    if model_upper.startswith('B'):
        hp = "21 HP" if "21" in model_upper else "24 HP" if "24" in model_upper else "27 HP" if "27" in model_upper else "B Series"
        return f"Tractor {model_name} ({hp})", "B-Series"
    elif model_upper.startswith('L'):
        hp = "32 HP" if "32" in model_upper else "40 HP" if "40" in model_upper else "50 HP" if "50" in model_upper else "L Series"
        return f"Tractor {model_name} ({hp})", "L-Series"
    elif model_upper.startswith('MU'):
        hp = "45 HP" if "45" in model_upper else "57 HP" if "57" in model_upper else "MU Series"
        return f"Tractor {model_name} ({hp})", "MU-Series"
    elif model_upper.startswith('M') and not model_upper.startswith('MU'):
        hp = "60 HP" if "60" in model_upper else "70 HP" if "70" in model_upper else "85 HP" if "85" in model_upper else "95 HP" if "95" in model_upper else "108 HP" if "108" in model_upper else "M Series"
        return f"Tractor {model_name} ({hp})", "M-Series"
    elif "DC" in model_upper:
        hp = "70 HP Pro" if "70G" in model_upper else "Combine Harvester"
        return f"Combine Harvester {model_name} ({hp})", "Harvester"
    elif "SPV" in model_upper or "SP" in model_upper:
        return f"Rice Transplanter {model_name}", "Transplanter"
    elif model_upper.startswith('U') or model_upper.startswith('KX'):
        hp = "17 HP Class" if "17" in model_upper else "33 HP Class" if "033" in model_upper else "55 HP Class" if "U55" in model_upper else "80 HP Class" if "080" in model_upper else "Excavator"
        return f"Excavator {model_name} ({hp})", "Excavator"
    return f"{model_name}", "Machinery"


# ==============================================================================
# 🚜 စာမျက်နှာ (၁) - PRICE LIST & SALES MEMO VOUCHER
# ==============================================================================
if page_selection == "🚜 Price List & Sales Memo":
    if not df_tractor.empty:
        st.markdown("<h1 style='text-align: center; color: #ff6600;'>🚜 GBS Tractor Price List</h1>", unsafe_allow_html=True)
        st.write("---") 

        st.subheader("📝 ဘောက်ချာအတွက် ကိုယ်တိုင်ရိုက်ထည့်ရန် အချက်အလက်များ")
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            cust_info = st.text_input("ဝယ်သူအမည် နှင့် ဖုန်းနံပါတ် (Customer)", "Aung Naing Win (Nattalin) (09-423737582)")
            sale_name = st.text_input("အရောင်းဝန်ထမ်းအမည် (Sale)", "HLA MYO OO")
            address_info = st.text_input("ဝယ်သူလိပ်စာ (Address)", "San Chaung Village, Nattalin, Bagowest, Myanmar")
        with col_v2:
            doc_no = st.text_input("ဘောက်ချာနံပါတ် (Document No.)", "121-2605-0016")
            qty_input = st.number_input("စက်အရေအတွက် (Qty)", min_value=1, value=1, step=1)
            
        st.markdown("#### 🎁 လစဉ်ပြောင်းလဲမည့် ပရိုမိုးရှင်းနှင့် လျှော့ဈေး သတ်မှတ်ရန်")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            promo_text = st.text_input("ပရိုမိုးရှင်း အမှတ်အသား ဖြည့်ရန်", "ပရိုမိုးရှင်း 50 % လျှော့ပြီး")
        with col_p2:
            discount_input = st.number_input("လျှော့ဈေး ပမာဏ (Discount MMK)", min_value=0, value=500000, step=50000)
            
        note_info = st.text_area("မှတ်ချက် (Note)", "Exchange rate -2106$,\n05-Broker, Cash, Promotion")

        st.write("---")
        st.subheader("🚜 စက်ပစ္စည်းနှင့် နောက်တွဲပစ္စည်းများ ရွေးချယ်ခြင်း")

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

        st.write("---")
        st.caption("🛠 နောက်တွဲပစ္စည်းများ စိတ်ကြိုက်ရွေးချယ်ရန်")
        filtered_att = df_attach[df_attach.iloc[:, 0].astype(str) == selected_model] if not df_attach.empty else pd.DataFrame()
        
        selected_att_total = 0
        chosen_attachments = [] 

        def add_att_ui(label, m_col, p_col):
            if not filtered_att.empty and m_col in df_attach.columns:
                items = filtered_att[[m_col, p_col]].drop_duplicates()
                options = []
                for _, row in items.iterrows():
                    if str(row[m_col]) not in ["0", "0.0", "nan"]:
                        try:
                            p_val = str(row[p_col]).replace(',', '').strip()
                            p = float(p_val)
                            options.append({"label": f"{row[m_col]} (+{p:,.0f} MMK)", "price": p, "name": str(row[m_col])})
                        except:
                            continue
                if options:
                    c = st.selectbox(f"{label}:", ["မယူပါ"] + [o["label"] for o in options])
                    if c != "မယူပါ":
                        price = next(item["price"] for item in options if item["label"] == c)
                        name = next(item["name"] for item in options if item["label"] == c)
                        chosen_attachments.append({"type": label, "model": name, "price": price})
                        return price
            return 0

        col_att1, col_att2 = st.columns(2)
        with col_att1:
            selected_att_total += add_att_ui("Rotary", "Rotary_Model1", "Rotary_Price")
            selected_att_total += add_att_ui("Disc Harrow", "Harrow_Model1", "Harrow_Price")
            selected_att_total += add_att_ui("Disc Plow", "Plow_Model1", "Plow_Price")
        with col_att2:
            selected_att_total += add_att_ui("Combine Harvester Attach", "Combine_Model1", "Combine_Price")
            selected_att_total += add_att_ui("Hydraulic Breaker", "Breaker_Model1", "Breaker_Price")
            selected_att_total += add_att_ui("Sowing/Transplanter", "Transplanter_Model1", "Transplanter_Price")

        total_machine_amount = base_price * qty_input
        total_attachments_amount = selected_att_total * qty_input
        grand_total = total_machine_amount + total_attachments_amount
        
        st.write("---")
        st.success(f"## 📄 စုစုပေါင်းကျသင့်ငွေ: {grand_total:,.0f} MMK")

        # HTML Sales Voucher
        current_date_str = datetime.now().strftime("%d-%m-%Y")
        full_machine_name, machine_code = get_machine_details(selected_model)
        item_no = 1
        machine_display_name = f"{full_machine_name} <br><small style='color:#555;'>({promo_text})</small>" if promo_text else full_machine_name
        
        table_rows_html = f"<tr><td style='text-align:center;'>{item_no}</td><td>{machine_code}</td><td>{machine_display_name}</td><td style='text-align:right;'>{base_price:,.0f}</td><td style='text-align:center;'>{qty_input}.00</td><td style='text-align:right;'>{discount_input:,.0f}</td><td style='text-align:right; font-weight:bold;'>{total_machine_amount:,.0f}</td></tr>"
        for att in chosen_attachments:
            item_no += 1
            table_rows_html += f"<tr><td style='text-align:center;'>{item_no}</td><td>ATT-CODE</td><td>{att['type']} - {att['model']}</td><td style='text-align:right;'>{att['price']:,.0f}</td><td style='text-align:center;'>{qty_input}.00</td><td style='text-align:right;'>0</td><td style='text-align:right; font-weight:bold;'>{(att['price']*qty_input):,.0f}</td></tr>"

        sales_memo_html = f"""
        <!DOCTYPE html><html><head><meta charset="utf-8"><style>
        body {{ font-family: sans-serif; padding: 20px; background-color: #f5f5f5; }}
        .btn-container {{ text-align: center; margin-bottom: 15px; }}
        .btn-print {{ background-color: #2b7deb; color: white; padding: 12px 25px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }}
        .invoice-box {{ max-width: 850px; margin: auto; padding: 30px; background: #fff; border: 1px solid #ddd; font-size: 13px; }}
        .products-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        .products-table th {{ background-color: #58a5f7!important; color: white!important; padding: 8px; border: 1px solid #58a5f7; }}
        .products-table td {{ border: 1px solid #e2e2e2; padding: 10px 8px; }}
        @media print {{ .btn-container {{ display: none !important; }} .invoice-box {{ border: none; padding: 0; }} }}
        </style></head><body>
        <div class="btn-container"><button class="btn-print" onclick="window.print()">🖨 Print / Save as PDF</button></div>
        <div class="invoice-box"><h2>Good Brother Co., Ltd</h2><hr>
        <p><b>Customer:</b> {cust_info} &nbsp;|&nbsp; <b>Doc No:</b> {doc_no} &nbsp;|&nbsp; <b>Date:</b> {current_date_str}</p>
        <table class="products-table"><thead><tr><th>No</th><th>Code</th><th>Name</th><th>Price</th><th>Qty</th><th>Discount</th><th>Amount</th></tr></thead>
        <tbody>{table_rows_html}</tbody></table></div></body></html>
        """
        st.sidebar.download_button("📥 Download Sales Memo (HTML)", data=sales_memo_html, file_name=f"Sales_Memo_{doc_no}.html", mime="text/html")
    else:
        st.error("ဒေတာများကို မဖတ်နိုင်ပါ။ Sheet အမည် မှားယွင်းနေနိုင်ပါသည်။")


# ==============================================================================
# 📰 စာမျက်နှာ (၂) - COMPETITOR NEWS UPDATE (သတင်းစာမျက်နှာ သီးသန့်)
# ==============================================================================
elif page_selection == "📰 Competitor News Update":
    st.markdown("<h1 style='text-align: center; color: #0066cc;'>📰 Competitor News Update</h1>", unsafe_allow_html=True)
    st.write("---")
    
    news_tab1, news_tab2 = st.tabs(["📌 သတင်းများ ဖတ်ရှုရန်နှင့် စာရွက်ထုတ်ရန်", "✍️ သတင်းအသစ်တင်ရန် (Post)"])
    
    with news_tab1:
        if not df_news.empty:
            st.markdown("### 📰 နေ့စဉ်တင်ထားသော သတင်းများ စာရင်း")
            st.caption("💡 မိမိ သိမ်းဆည်းလိုသော သတင်းများကို Checkbox တွင် နှိပ်၍ အစုံလိုက် ရွေးချယ်ထုတ်ယူနိုင်ပါသည်ဗျာ။")
            
            selected_news_indices = []
            
            # loop ပတ်ပြီး သတင်းတစ်ခုချင်းစီကို ကတ်ပုံစံလှလှလေးနဲ့ Checkbox ပြသခြင်း
            for idx, row in df_news.iterrows():
                news_id = row['ID']
                news_date = row['Date']
                news_title = row['Title']
                news_detail = row['Detail']
                news_img = row['Image']
                
                # Checkbox တပ်ဆင်ခြင်း
                is_selected = st.checkbox(f"[{news_date}] - {news_title}", key=f"news_check_{idx}")
                if is_selected:
                    selected_news_indices.append(idx)
                    
                # သတင်းအချက်အလက်ကို UI ပေါ်တွင် ပြသခြင်း
                with st.expander("🔍 သတင်းအသေးစိတ်နှင့် ပုံကို ကြည့်ရန်"):
                    st.info(f"📅 ရက်စွဲ: {news_date} | ID: {news_id}")
                    if news_img and str(news_img).startswith("http"):
                        st.image(str(news_img), use_container_width=True)
                    st.write(news_detail)
                st.write("---")
            
            # --- ရွေးချယ်လိုက်သော သတင်းများကို အစုံလိုက် HTML/PDF စုထုတ်ပေးမည့်အပိုင်း ---
            if selected_news_indices:
                st.success(f"📌 သတင်း စုစုပေါင်း ({len(selected_news_indices)}) ခု ရွေးချယ်ထားပါသည်")
                
                # HTML တည်ဆောက်ခြင်း
                news_items_html = ""
                for idx in selected_news_indices:
                    row = df_news.loc[idx]
                    img_tag = f'<center><img src="{row["Image"]}" style="max-width:100%; border-radius:6px; margin:15px 0;"></center>' if row["Image"] and str(row["Image"]).startswith("http") else ""
                    
                    news_items_html += f"""
                    <div class="news-card">
                        <div class="meta-info">📅 ရက်စွဲ: {row['Date']} &nbsp;|&nbsp; News ID: {row['ID']}</div>
                        <div class="news-title">📌 {row['Title']}</div>
                        {img_tag}
                        <div class="news-content">{row['Detail']}</div>
                    </div>
                    <hr style="border: 1px dashed #ddd; margin: 30px 0;">
                    """
                
                full_news_report_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <style>
                        body {{ font-family: sans-serif; padding: 20px; background-color: #ffffff; color: #333; line-height: 1.6; }}
                        .container {{ max-width: 800px; margin: auto; padding: 20px; }}
                        .header {{ text-align: center; border-bottom: 3px solid #0066cc; padding-bottom: 10px; margin-bottom: 30px; }}
                        .news-card {{ background: #fff; padding: 10px; margin-bottom: 20px; }}
                        .meta-info {{ font-size: 13px; color: #666; margin-bottom: 5px; }}
                        .news-title {{ font-size: 22px; font-weight: bold; color: #111; margin-bottom: 15px; }}
                        .news-content {{ font-size: 15px; color: #222; text-align: justify; white-space: pre-line; }}
                        .btn-print-container {{ text-align: center; margin-bottom: 20px; }}
                        .btn-print {{ background-color: #0066cc; color: white; padding: 12px 25px; border: none; border-radius: 4px; cursor: pointer; font-size: 15px; font-weight: bold; }}
                        @media print {{ .btn-print-container {{ display: none !important; }} .container {{ width: 100%; }} }}
                    </style>
                </head>
                <body>
                    <div class="btn-print-container">
                        <button class="btn-print" onclick="window.print()">🖨 Print / Save as PDF (ရွေးချယ်ထားသော သတင်းများကို Print ထုတ်ရန်)</button>
                    </div>
                    <div class="container">
                        <div class="header">
                            <h2>Good Brother Co., Ltd</h2>
                            <div style="color:#666; text-transform:uppercase;">Competitor News Summary Report</div>
                        </div>
                        {news_items_html}
                    </div>
                </body>
                </html>
                """
                
                # Download ခလုတ်ပြသခြင်း
                st.download_button(
                    label="📥 Download Selected News Summary (HTML/PDF)",
                    data=full_news_report_html,
                    file_name=f"News_Summary_Report_{datetime.now().strftime('%d%m%Y')}.html",
                    mime="text/html"
                )
                st.caption("💡 အပေါ်က ခလုတ်ကိုနှိပ်ပြီး ဖိုင်ကို ဒေါင်းလုဒ်ဆွဲပါ။ ထို့နောက် ဖိုင်ကိုဖွင့်ပြီး 'Print / Save as PDF' ခလုတ်ဖြင့် လိုအပ်သလို စက္ကန့်ပိုင်းအတွင်း စာရွက်ထုတ်ခြင်း သို့မဟုတ် PDF အဖြစ် အလွယ်တကူ သိမ်းဆည်းနိုင်ပါတယ်ဗျာ။")
            else:
                st.warning("👉 ကျေးဇူးပြု၍ ဖိုင်ထုတ်ယူလိုသည့် သတင်းများ၏ ရှေ့ရှိ Checkbox များတွင် အမှန်ခြစ် ပေးပါဗျာ။")
        else:
            st.error("သတင်းဒေတာများ မတွေ့ရှိပါ။")

    # မူရင်းအတိုင်း ဘာမှမပြောင်းလဲထားသော သတင်းအသစ်တင်သည့်အပိုင်း (Post Tab)
    with news_tab2:
        st.subheader("✍️ သတင်းအချက်အလက်အသစ် ဖြည့်စွက်ရန်")
        new_title = st.text_input("သတင်းခေါင်းစဉ် (Title)", placeholder="ဥပမာ - စက်ပစ္စည်းအသစ်များ ရောက်ရှိခြင်း")
        new_detail = st.text_area("သတင်းအသေးစိတ် (Detail)", placeholder="သတင်းအကြောင်းအရာများကို ဤနေရာတွင် ရေးသားပါ...")
        new_img = st.text_input("ဓာတ်ပုံ Link (Image URL)", placeholder="https://example.com/image.jpg (မရှိလျှင် အလွတ်ထားပါ)")
        
        if st.button("📢 သတင်းအသစ်တင်မည် (Post News)"):
            if new_title and new_detail:
                next_id = len(df_news) + 1 if not df_news.empty else 1
                today_date = datetime.now().strftime("%d-%m-%Y")
                st.success("🎉 သတင်းတင်ခြင်း အောင်မြင်ပါသည်။ (မှတ်ချက် - Google Sheet API ချိတ်ဆက်မှုအဆင့် သတ်မှတ်ပြီးပါက ဒေတာများ Sheet ထဲသို့ တိုက်ရိုက်အော်တို ဝင်ရောက်သွားမည်ဖြစ်ပါသည်)")
                st.balloons()
            else:
                st.error("ကျေးဇူးပြု၍ သတင်းခေါင်းစဉ် နှင့် သတင်းအသေးစိတ်ကို မဖြစ်မနေ ဖြည့်စွက်ပေးပါဗျာ။")

st.markdown("<br><hr><center><small>© 2026 Good Brother Co., Ltd.</small></center>", unsafe_allow_html=True) 














