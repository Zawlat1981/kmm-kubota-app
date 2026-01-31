import streamlit as st
import pandas as pd

# Google Sheet Link
sheet_id = "1tJv_LdIn6Aol-p3zOa0D1pD_67z878-3K9K9K9K9K9" # <--- လူကြီးမင်းရဲ့ Sheet ID ကို ဒီမှာ ပြန်ထည့်ပါ
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

st.set_page_config(page_title="KMM Kubota Price List", page_icon="🚜")

st.title("🚜 KMM Kubota Price List")

try:
    # Google Sheet ဖတ်ခြင်း (Header က Row 1 မှာ ရှိတယ်လို့ ယူဆပါတယ်)
    df = pd.read_csv(url)
    
    # Model အမည်မပါတဲ့ Row တွေကို ဖယ်ထုတ်ခြင်း
    df = df.dropna(subset=['Model'])
    df = df[df['Model'] != '0'] # '0' လို့ ရေးထားတဲ့ Row တွေကို ဖယ်ထုတ်ခြင်း
    
    # Model ရွေးချယ်ခြင်း
    model_list = df['Model'].tolist()
    selected_model = st.selectbox("Product Model ကိုရွေးပါ -", model_list)
    
    # ရွေးချယ်ထားသော Model ၏ Row ကို ရှာခြင်း
    model_row = df[df['Model'] == selected_model].iloc[0]
    
    # Base Price ပြသခြင်း
    base_price = float(model_row['Base Price'])
    st.subheader(f"💰 Base Price: {base_price:,.0f} Ks")
    st.write("---")
    
    # Attachment Columns များကို ရှာဖွေခြင်း (Column နာမည်မှာ '_Price' ပါတာတွေကို ယူပါမယ်)
    attachment_cols = [col for col in df.columns if '_Price' in col]
    
    st.write("🔗 **Attachments ပေါင်းထည့်ရန်:**")
    total_attachment_price = 0
    
    # Attachment တစ်ခုချင်းစီအတွက် Checkbox လေးတွေ လုပ်ခြင်း
    for col in attachment_cols:
        price_val = model_row[col]
        
        # ဈေးနှုန်းက 0 ထက်ကြီးမှသာ Website မှာ ပေါ်အောင်လုပ်ခြင်း
        if pd.notnull(price_val) and float(price_val) > 0:
            display_name = col.replace('_Price', '') # '_Price' ဆိုတဲ့ စာသားကို ဖယ်ပြီး နာမည်ပဲပြရန်
            if st.checkbox(f"{display_name} (+{float(price_val):,.0f} Ks)"):
                total_attachment_price += float(price_val)
                
    # စုစုပေါင်းတွက်ချက်ခြင်း
    grand_total = base_price + total_attachment_price
    st.write("---")
    st.success(f"📄 **Grand Total: {grand_total:,.0f} Kyats**")

except Exception as e:
    st.error(f"Error: Google Sheet ထဲက Column ခေါင်းစဉ်တွေ မှန်မမှန် ပြန်စစ်ပေးပါဗျာ။ ({e})")










