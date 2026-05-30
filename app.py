import streamlit as st
import pandas as pd
from datetime import datetime

# ==============================================================================
# ⚙️ အပိုင်း (၁) - PAGE CONFIGURATION & SETUP
# ==============================================================================
st.set_page_config(page_title="Kubota Maesod Myanmar Co., Ltd", page_icon="🚜", layout="centered")

# Google Sheet ID (မူရင်း ID အတိုင်း ကွက်တိ)
SHEET_ID = "1QqQvPKH7G0hqqhd_0V6cP40Htl8qdFEZ6nHBVe_53_g"

@st.cache_data(ttl=60)
def load_data(tab_name):
    """ Google Sheet မှ ဒေတာများကို ပုံမှန်အတိုင်း အော်တိုဆွဲဖတ်သည့်စနစ် """
    base_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet="
    
    # စက်ပစ္စည်းစျေးနှုန်းစာမျက်နှာ ဖတ်ခြင်း
    try:
        df_tractor = pd.read_csv(base_url + tab_name).fillna(0)
    except:
        df_tractor = pd.DataFrame()

    # နောက်တွဲပစ္စည်းစာမျက်နှာ ဖတ်ခြင်း (Kubota နှင့် Yanmar အတွက်သာ)
    df_attach = pd.DataFrame() 
    if tab_name in ["Kubota", "Yanmar"]:
        attachment_tab = f"Attachments_{tab_name}"
        try:
            df_attach = pd.read_csv(base_url + attachment_tab).fillna(0)
        except:
            pass
            
    # News စာမျက်နှာကို ဖတ်ခြင်း (မပျောက်ပျက်စေရန် သေချာထည့်သွင်းထားပါသည်)
    try:
        df_news = pd.read_csv(base_url + "News").fillna("")
    except:
        df_news = pd.DataFrame()
        
    return df_tractor, df_attach, df_news

# --- Sidebar အတွက် အမှတ်တံဆိပ်ရွေးချယ်မှု ကဏ္ဍ ---
st.sidebar.header("🚜 Brand Selection")
selected_brand = st.sidebar.selectbox(
    "အမှတ်တံဆိပ် ရွေးချယ်ပါ -", 
    ["Kubota", "Yanmar", "Win-Shwe-Wah(2nd)", "John-Deere", "New-Holland", "YTO", "Mahindra", "Sonalika", "Yamabisi", "DongFeng"]
)

# ဒေတာများ စတင်ခေါ်ယူခြင်း
df_tractor, df_attach, df_news = load_data(selected_brand)


# ==============================================================================
# 🧠 အပိုင်း (၂) - AUTOMATIC CODE & NAME SPLITTING LOGIC
# ==============================================================================
def get_machine_details(model_name):
    """ စက်မော်ဒယ်အလိုက် အမျိုးအစားကုဒ်နှင့် မြင်းကောင်ရေ (HP) ကို အလိုအလျောက် ခွဲခြားပေးခြင်း """
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
# 🚜 အပိုင်း (၃) - စက်ပစ္စည်းနှင့် စျေးနှုန်းကဏ္ဍ (PRICE LIST & MEMO)
# ==============================================================================
if not df_tractor.empty:
    st.markdown("<h1 style='text-align: center; color: #ff6600;'>🚜 KMM Kubota Price List</h1>", unsafe_allow_html=True)
    st.write("---") 

    # 📝 [MANUAL INPUT] ဘောက်ချာအတွက် ကိုယ်တိုင်ရိုက်ထည့်ရမည့် အချက်အလက်များ
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
        # ကွင်းထဲက လစဥ်အပြောင်းအလဲရှိမည့် စာသားကို ကိုယ်တိုင်ဖြည့်ရန် ကွက်လပ်
        promo_text = st.text_input("ပရိုမိုးရှင်း အမှတ်အသား ဖြည့်ရန် (ဥပမာ - ပရိုမိုးရှင်း 50 % လျှော့ပြီး)", "ပရိုမိုးရှင်း 50 % လျှော့ပြီး")
    with col_p2:
        # လျှော့ဈေး ပမာဏကို ကိုယ်တိုင်ဖြည့်ရန် ကွက်လပ်
        discount_input = st.number_input("လျှော့ဈေး ပမာဏ (Discount MMK)", min_value=0, value=500000, step=50000)
        
    note_info = st.text_area("မှတ်ချက် (Note)", "Exchange rate -2106$,\n05-Broker, Cash, Promotion")

    st.write("---")
    st.subheader("🚜 စက်ပစ္စည်းနှင့် နောက်တွဲပစ္စည်းများ ရွေးချယ်ခြင်း")

    # စက်မော်ဒယ် ရွေးချယ်ခြင်း
    model_list = df_tractor.iloc[:, 0].astype(str).tolist()
    model_list = [m for m in model_list if m not in ["0", "0.0", "nan", "Model"]]
    selected_model = st.selectbox(f"{selected_brand} မော်ဒယ်ကို ရွေးပါ -", model_list)
    
    # [AUTO FROM SHEET] ပင်မစက်ဈေးနှုန်းနှင့် ပုံရိပ်ကို ဖတ်ခြင်း
    t_info = df_tractor[df_tractor.iloc[:, 0].astype(str) == selected_model].iloc[0]
    try:
        raw_p = str(t_info.iloc[1]).replace(',', '').strip()
        base_price = float(raw_p) if raw_p != "" else 0
    except:
        base_price = 0
    img_url = str(t_info.iloc[2])

    if img_url and img_url.startswith("http"):
        st.image(img_url, use_container_width=True)

    # နောက်တွဲများ ရွေးချယ်ခြင်း
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

    # [AUTO CALCULATED] တွက်ချက်မှု Logic (စက်ဈေး + နောက်တွဲဈေး မူရင်းအတိုင်း ပေါင်းပေးမည့်ပုံစံ)
    total_machine_amount = base_price * qty_input
    total_attachments_amount = selected_att_total * qty_input
    grand_total = total_machine_amount + total_attachments_amount
    
    st.write("---")
    st.success(f"## 📄 စုစုပေါင်းကျသင့်ငွေ: {grand_total:,.0f} MMK")


    # ==============================================================================
    # 🖨 အပိုင်း (၄) - SALES MEMO VOUCHER GENERATOR (HTML/PDF)
    # ==============================================================================
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 Export Section")
    
    # [AUTO] ယနေ့ရက်စွဲကို DD-MM-YYYY ပုံစံဖြင့် အော်တိုရယူခြင်း
    current_date_str = datetime.now().strftime("%d-%m-%Y")
    
    # [AUTO] မော်ဒယ်အလိုက် အမျိုးအစားနှင့် မြင်းကောင်ရေ အော်တိုခွဲခြားမှု ခေါ်ယူခြင်း
    full_machine_name, machine_code = get_machine_details(selected_model)

    # ဇယားကွက် HTML Rows များ တည်ဆောက်ခြင်း
    item_no = 1
    machine_display_name = f"{full_machine_name} <br><small style='color:#555;'>({promo_text})</small>" if promo_text else full_machine_name
    
    table_rows_html = f"""
    <tr>
        <td style="text-align: center;">{item_no}</td>
        <td>{machine_code}</td>
        <td>{machine_display_name}</td>
        <td style="text-align: right;">{base_price:,.0f}</td>
        <td style="text-align: center;">{qty_input}.00</td>
        <td style="text-align: right;">{discount_input:,.0f}</td>
        <td style="text-align: right; font-weight: bold;">{total_machine_amount:,.0f}</td>
    </tr>
    """
    
    for att in chosen_attachments:
        item_no += 1
        att_amount = att['price'] * qty_input
        table_rows_html += f"""
        <tr>
            <td style="text-align: center;">{item_no}</td>
            <td>ATT-CODE</td>
            <td>{att['type']} - {att['model']}</td>
            <td style="text-align: right;">{att['price']:,.0f}</td>
            <td style="text-align: center;">{qty_input}.00</td>
            <td style="text-align: right;">0</td>
            <td style="text-align: right; font-weight: bold;">{att_amount:,.0f}</td>
        </tr>
        """

    sales_memo_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; padding: 20px; background-color: #f5f5f5; color: #000; }}
            .btn-container {{ text-align: center; margin-bottom: 15px; }}
            .btn-print {{ background-color: #2b7deb; color: white; padding: 12px 25px; border: none; border-radius: 4px; cursor: pointer; font-size: 15px; font-weight: bold; }}
            .invoice-box {{ max-width: 850px; margin: auto; padding: 30px; background: #fff; border: 1px solid #ddd; font-size: 13px; line-height: 20px; color: #000; }}
            .header-title {{ font-size: 18px; font-weight: bold; margin: 0; }}
            .header-subtitle {{ font-size: 12px; color: #333; margin: 2px 0; }}
            .divider-line {{ border-top: 2px solid #2b7deb; margin: 12px 0 20px 0; }}
            .memo-title {{ font-size: 26px; font-weight: bold; margin-bottom: 20px; }}
            
            .info-grid {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; }}
            .info-grid td {{ padding: 4px 6px; vertical-align: top; border: none; }}
            .label-cell {{ width: 12%; }}
            .val-cell {{ width: 45%; }}
            
            .products-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            .products-table th {{ background-color: #58a5f7 !important; color: white !important; font-weight: bold; padding: 8px; border: 1px solid #58a5f7; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
            .products-table td {{ border: 1px solid #e2e2e2; padding: 10px 8px; }}
            .total-row td {{ border: none; border-top: 1px solid #000; border-bottom: 1px solid #000; padding: 8px; font-size: 15px; font-weight: bold; }}
            
            @media print {{
                body {{ background-color: white; padding: 0; margin: 0; }}
                .btn-container {{ display: none !important; }}
                .invoice-box {{ border: none; padding: 10px; width: 100%; }}
                .products-table th {{ background-color: #58a5f7 !important; color: white !important; }}
                @page {{ size: A4 portrait; margin: 10mm; }}
            }}
        </style>
    </head>
    <body>
        <div class="btn-container">
            <button class="btn-print" onclick="window.print()">🖨 Print / Save as PDF (Sales Memo ထုတ်ရန်)</button>
        </div>
        
        <div class="invoice-box">
            <div class="header-title">Kubota Maesod Myanmar Co., Ltd (Tharyarwaddy Branch)</div>
            <div class="header-subtitle">No.253, Yangon-Pyay Main Road, Ahlekone Quarter, Thonze Township, Bago Division, Myanmar</div>
            <div class="header-subtitle">Tel. +95978999848</div>
            <div class="divider-line"></div>
            <div class="memo-title">Sales Memo</div>
            
            <table class="info-grid">
                <tr>
                    <td class="label-cell">Customer</td>
                    <td class="val-cell">: &nbsp; {cust_info}</td>
                    <td style="width:13%;">Document</td>
                    <td style="width:30%;">: &nbsp; {doc_no}</td>
                    <td style="width:10%;">Deliver</td>
                    <td>: &nbsp; {current_date_str}</td>
                </tr>
                <tr>
                    <td class="label-cell">Sale</td>
                    <td class="val-cell">: &nbsp; {sale_name}</td>
                    <td>Quotation</td>
                    <td>: &nbsp; </td>
                    <td>Date</td>
                    <td style="font-weight: bold;">: &nbsp; {current_date_str}</td>
                </tr>
                <tr>
                    <td class="label-cell">Address</td>
                    <td class="val-cell" colspan="5">: &nbsp; {address_info}</td>
                </tr>
                <tr>
                    <td class="label-cell">Note</td>
                    <td class="val-cell" colspan="5" style="white-space: pre-line;">: &nbsp; {note_info}</td>
                </tr>
            </table>
            
            <div style="font-weight: bold; font-size: 15px; margin-bottom: 5px;">Products</div>
            <table class="products-table">
                <thead>
                    <tr>
                        <th style="width: 5%; text-align: center;">No</th>
                        <th style="width: 15%;">Code</th>
                        <th style="width: 40%;">Name</th>
                        <th style="width: 13%; text-align: right;">Price/Unit</th>
                        <th style="width: 7%; text-align: center;">Qty</th>
                        <th style="width: 10%; text-align: right;">Discount</th>
                        <th style="width: 13%; text-align: right;">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows_html}
                    <tr class="total-row">
                        <td colspan="4"></td>
                        <td style="text-align: center;">{qty_input * item_no}.00</td>
                        <td></td>
                        <td style="text-align: right; color: #2b7deb; font-size: 16px;">{grand_total:,.0f}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    st.sidebar.download_button(
        label="📥 Download Sales Memo (HTML)",
        data=sales_memo_html,
        file_name=f"Sales_Memo_{doc_no}.html",
        mime="text/html"
    )
else:
    st.error("Google Sheet မှ ဒေတာများကို မဖတ်နိုင်ပါ။ သို့မဟုတ် စာမျက်နှာအမည် မှားယွင်းနေပါသည်။")


# ==============================================================================
# 📰 အပိုင်း (၅) - သတင်းကဏ္ဍ (NEWS SECTION - အပြည့်အစုံ ပြန်ထည့်ပေးထားပါသည်)
# ==============================================================================
st.write("---")
st.markdown("<h2 style='text-align: center; color: #0066cc;'>📰 KMM Official News Section</h2>", unsafe_allow_html=True)

if not df_news.empty:
    news_titles = df_news.iloc[:, 2].astype(str).tolist()
    st.subheader("📌 သတင်းများကို ရွေးချယ်ဖတ်ရှုရန်")
    selected_news_title = st.selectbox("ဖတ်ရှုလိုသည့် သတင်းခေါင်းစဉ်ကို ရွေးပါ -", news_titles)
    
    news_info = df_news[df_news.iloc[:, 2].astype(str) == selected_news_title].iloc[0]
    news_id = str(news_info.iloc[0])
    news_date = str(news_info.iloc[1]) 
    news_detail = str(news_info.iloc[3])
    news_img_url = str(news_info.iloc[4])
    
    st.info(f"📅 သတင်းတင်သည့်ရက်စွဲ: {news_date}")
    st.markdown(f"### 📌 {selected_news_title}")
    
    if news_img_url and news_img_url.startswith("http"):
        st.image(news_img_url, use_container_width=True)
    st.write(news_detail)
else:
    st.warning("Google Sheet ထဲတွင် 'News' စာမျက်နှာ ဒေတာများကို မတွေ့ရှိပါ။")

st.markdown("<br><hr><center><small>© 2026 Kubota Maesod Myanmar Co., Ltd.</small></center>", unsafe_allow_html=True) 















