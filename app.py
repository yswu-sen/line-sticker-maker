import streamlit as st
import random
from PIL import Image, ImageFilter, ImageColor
import numpy as np
import io
import zipfile
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from streamlit_option_menu import option_menu 
from datetime import datetime

# ==========================================
# 🎨 1. 頁面與 ADI 品牌化 CSS 設定
# ==========================================
st.set_page_config(
    page_title="Line 貼圖半自動產生器", 
    page_icon="🎨", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🌟 CSS 魔術：注入 ADI 品牌規範 + 便利貼特效 + Code Block 修復 + Hero標題
st.markdown("""
    <style>
    /* 引入 Poppins 字體 */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    /* 全局字體設定 */
    html, body, [class*="css"] {
        font-family: 'Poppins', 'PingFang TC', 'Microsoft JhengHei', sans-serif;
        color: #1F323D;
    }

    /* 全局背景色 */
    .stApp {
        background-color: #F8F9FA;
    }
    
    /* 🏆 Hero Header (主標題區) */
    .hero-container {
        text-align: center;
        padding: 20px 0 10px 0;
        margin-bottom: 20px;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1F323D;
        margin: 0;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #5F5F5F;
        margin-top: 5px;
    }
    
    /* 卡片樣式 */
    .css-card {
        background-color: #FFFFFF;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(31, 50, 61, 0.08);
        margin-bottom: 20px;
        border-left: 5px solid #B4C43F;
    }
    
    /* 🛠️ [修復] Prompt Code Block 樣式 */
    div[data-testid="stCodeBlock"] {
        background-color: #F1F3F6 !important; /* 淺灰藍底色 */
        border: 2px solid #E0E4EB;
        border-radius: 8px;
        padding: 10px;
    }
    div[data-testid="stCodeBlock"] button {
        background-color: #FFFFFF !important;
        border: 1px solid #ccc !important;
        color: #333 !important;
    }

    /* 📒 便利貼樣式 (Sticky Note) */
    .sticky-note {
        padding: 20px;
        width: 100%;
        min-height: 150px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.15);
        font-family: 'Comic Sans MS', 'Microsoft JhengHei', cursive; 
        font-size: 1.1em;
        color: #333;
        transform: rotate(-1deg);
        transition: transform 0.3s;
        margin-bottom: 20px;
    }
    .sticky-note:hover {
        transform: scale(1.05) rotate(0deg);
        z-index: 10;
        box-shadow: 10px 10px 20px rgba(0,0,0,0.2);
    }
    .note-yellow { background-color: #FFF740; }
    .note-pink { background-color: #FF7EB9; }
    .note-blue { background-color: #7AFcFF; }
    .note-green { background-color: #98FB98; }

    /* 標題與文字顏色 */
    h1, h2, h3 { color: #1F323D !important; font-weight: 700; }
    .stMarkdown p, .caption { color: #5F5F5F !important; }
    
    /* 按鈕優化 */
    .stButton>button {
        border-radius: 6px;
        height: 3em;
        font-weight: 600;
        border: 1px solid #1F323D;
        color: #1F323D;
        background-color: transparent;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #1F323D;
        color: #FFFFFF;
    }
    
    /* Primary Button */
    button[kind="primary"] {
        background-color: #B4C43F !important;
        color: #1F323D !important;
        border: none !important;
    }
    button[kind="primary"]:hover {
        background-color: #A3B330 !important;
        box-shadow: 0 4px 12px rgba(180, 196, 63, 0.4);
    }

    /* 標籤 Tag */
    .custom-tag {
        background: rgba(180, 196, 63, 0.15);
        color: #1F323D;
        padding: 4px 10px;
        margin: 3px;
        border-radius: 20px;
        font-size: 0.9em;
        display: inline-block;
        border: 1px solid #B4C43F;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 2. 完整資料庫 (含水墨畫風)
# ==========================================
STICKER_CATEGORIES = {
    "日常問候": ["早安", "安安", "抱歉假日打擾", "晚安瑪卡巴卡", "睡了沒？", "在嗎？", "呷霸沒", "撤！", "回家囉", "已出門", "到家！", "在路上", "修但幾勒", "放假~", "開工啦", "哈囉", "Bye Bye"],
    "工作職場": ["收到", "了解", "我看看", "處理中", "快好了", "鶴", "好勒", "沒問題", "金都蝦", "辛苦了", "這裡有Bug", "開會中", "不想上班", "會後討論", "開不完的會", "加班命…", "請幫確認", "麻煩您！", "感謝支援～", "坐等下班", "我愛(恨)工作", "可以"],
    "情緒表達": ["哭阿", "笑死", "怕豹！", "傻眼", "無言", "???", "!!!", "真的假的", "氣死", "心累", "懷疑人生", "壓力山大", "嚇死寶寶", "母湯喔", "想躺平", "不想動", "悶…", "QQ", "扯爆扯", "傻爆眼", "沒get到", "耶死", "啵兒棒", "送啦！", "有你真好～"],
    "網路流行/梗": ["歸剛欸", "我就爛", "Duck不必", "是在哈囉", "像極了愛情", "真香", "ㄜ…", "芭比Q了", "回答我Look in eyes", "Tell Me Why ", "牛～逼", "見笑轉生氣", "要確誒", "再泉啊(齁懶)", "先緩緩", "太狠了", "頂不住", "笑爛", "破防", "蛤？", "穩了", "翻車了", "來吃瓜~", "4 ni？", "UCCU你看看你", "超ㄎㄧㄤ ", "甘阿捏？", "哩洗咧烤！"],
    "簡短回應": ["+1", "OK", "No", "Yes", "GOGOGO", "讚", "強", "行", "不行啦", "沒差", "隨你", "是喔？", "不會吧…", "也是啦", "對啦", "錯了吧", "再看看？", "等一下", "馬上來", "咖緊捏", "慢慢來", "幾霸分100"],
    "生活日常": ["吃飯中", "剛吃飽", "去呷奔", "餓", "我請", "需補充咖啡因…", "來睏", "熬夜中", "早起痛苦", "追劇ing", "手機滑起來", "放空中", "這禮拜吃土", "領錢囉", "買買買", "剁手", "減肥明天再說", "High~起來"],
    "可愛短句/撒嬌": ["來啦", "走啦", "好了啦", "不要啦", "拜託啦", "救我", "求幫忙", "愛老虎油", "Sorry！", "謝啦", "感恩", "感謝你", "死勾以～", "厲～害", "交給偶", "我負責"],
    "收尾萬用": ["下次再說", "改天啦", "再聯絡", "先醬", "掰啦", "晚點聊", "明天續戰", "Take care", "注意安全", "保重身體"]
}

ART_STYLES = {
    "🌟 可愛 Q 版 (預設)": "可愛、活潑、2D平面、Q版二頭身、向量插畫風格",
    "🖌️ 水墨畫風 (New!)": "傳統水墨畫風格、Sumi-e、毛筆筆觸(Brush strokes)、渲染效果(Ink wash)、寫意、留白藝術、(black and white ink:1.2)、東方美學",
    "📸 寫實風格": "高度寫實、照片質感、(flat lighting:1.5)、(studio lighting)、無陰影",
    "🎮 像素藝術 (Pixel Art)": "8-bit 像素風格、復古遊戲感、點陣圖藝術",
    "🎌 日系動漫 (Anime)": "日系賽璐璐動畫風格、線條俐落、鮮豔明亮、2D渲染",
    "🧸 3D 盲盒公仔": "3D 渲染(C4D/Blender風格)、泡泡瑪特(Pop Mart)質感、黏土材質、(soft light)、正面打光",
    "🇺🇸 美式卡通": "美式卡通(Cartoon Network風格)、粗獷線條、誇張動態、高飽和色彩",
    "🎨 水彩手繪": "水彩暈染質感、柔和筆觸、藝術插畫風格、白邊明顯",
    "✒️ 黑白素描": "鉛筆/炭筆素描風格、手繪線稿、黑白藝術感",
    "🕶️ 賽博龐克 (Cyberpunk)": "霓虹色彩、機械科技元素、高對比度、(bright green background:1.5)",
    "🔷 扁平向量 (Vector)": "極簡扁平化設計(Flat Design)、幾何圖形、向量圖示感"
}

PRESET_COLORS = {
    "⚫ 黑色 (Black)": "#000000",
    "⚪ 白色 (White)": "#FFFFFF",
    "🔴 紅色 (Red)": "#FF0000",
    "🔵 藍色 (Blue)": "#0000FF",
    "🟡 黃色 (Yellow)": "#FFFF00",
    "🟢 綠色 (Green - 慎用)": "#00FF00",
    "🟣 紫色 (Purple)": "#800080",
    "🟠 橘色 (Orange)": "#FFA500",
    "🟤 棕色 (Brown)": "#A52A2A",
    "👽 螢光粉 (Hot Pink)": "#FF69B4"
}

# ==========================================
# 🛠️ 3. 完整核心演算法
# ==========================================

def add_outline(input_image, thickness=1.5, color="#000000"):
    if thickness <= 0: return input_image
    img = input_image.convert("RGBA")
    radius = int(round(thickness))
    if radius < 1: radius = 1
    padding = radius + 5
    old_w, old_h = img.size
    new_w = old_w + (padding * 2)
    new_h = old_h + (padding * 2)
    padded_img = Image.new('RGBA', (new_w, new_h), (0, 0, 0, 0))
    padded_img.paste(img, (padding, padding))
    mask = padded_img.getchannel('A')
    filter_size = radius * 2 + 1
    dilated_mask = mask.filter(ImageFilter.MaxFilter(filter_size))
    rgba_color = ImageColor.getrgb(color) + (255,)
    outline_bg = Image.new('RGBA', padded_img.size, rgba_color)
    output_img = Image.new('RGBA', padded_img.size, (0, 0, 0, 0))
    output_img.paste(outline_bg, mask=dilated_mask)
    output_img.paste(padded_img, (0, 0), padded_img)
    bbox = output_img.getbbox()
    if bbox: return output_img.crop(bbox)
    return output_img

def remove_green_halo(image, threshold=30):
    img_np = np.array(image.convert("RGBA"))
    r, g, b, a = img_np.T
    g_dominance = g.astype(np.int16) - np.maximum(r, b).astype(np.int16)
    green_mask = (g_dominance > threshold) & (a > 0)
    img_np[..., 3][green_mask.T] = 0
    return Image.fromarray(img_np)

def resize_contain(image, target_size):
    target_w, target_h = target_size
    img_w, img_h = image.size
    if img_w == 0 or img_h == 0: return image
    ratio = min(target_w / img_w, target_h / img_h)
    new_size = (int(img_w * ratio), int(img_h * ratio))
    resized_img = image.resize(new_size, Image.Resampling.LANCZOS)
    final_img = Image.new("RGBA", target_size, (0, 0, 0, 0))
    paste_x = (target_w - new_size[0]) // 2
    paste_y = (target_h - new_size[1]) // 2
    final_img.paste(resized_img, (paste_x, paste_y))
    return final_img

def generate_dynamic_prompt(phrases, style_desc):
    phrases_str = "、".join(phrases)
    lighting_prompt = "平面光照(Flat Lighting)，背景無陰影(No Shadow)，"
    prompt = f"""
請參考上傳圖片中的角色，生成一張包含12個不同動作的角色貼圖集。
[角色與風格]:
- 必須維持原圖主角的特徵。
- 風格設定：【{style_desc}】。
- 光影設定：{lighting_prompt} 角色與文字外圍皆需加入粗白色外框(Sticker Style)。
- 背景：統一為 #00FF00 (純綠色)，不可有雜點。
- 佈局：先橫後直4x3 佈局，共12張，總尺寸 1480x960 px。

[文字內容]:
請使用以下隨機選出的12組文字，並搭配對應的情境動作(切勿重複)：
【{phrases_str}】

[設計規範]:
- 文字語言：台灣繁體中文。
- 字型：配合畫風的設計字體，顏色鮮豔高對比，**絕對禁止綠色與黑色**。
- 表情與動作：需誇張且與文字情境一致。
- 輸出：一張大圖，內含12張貼圖，綠底去背友善。
""" 
    return prompt

def process_sticker_grid(image_file, green_threshold, border_thickness, border_color_hex, safety_margin, shave_bottom_px):
    img = Image.open(image_file).convert("RGBA")
    target_size = (1480, 960)
    if img.size != target_size:
        img = img.resize(target_size, Image.Resampling.LANCZOS)

    data = np.array(img)
    red, green, blue, alpha = data.T
    green_areas = (green > green_threshold) & (red < 120) & (blue < 120)
    data[..., 3][green_areas.T] = 0
    result_img = Image.fromarray(data)
    
    col_count = 4
    row_count = 3
    unit_w = 1480 // col_count 
    unit_h = 960 // row_count  
    
    stickers = []
    
    for r in range(row_count):
        for c in range(col_count):
            left = c * unit_w
            upper = r * unit_h
            right = left + unit_w
            lower = upper + unit_h
            
            cell_crop = result_img.crop((left, upper, right, lower))
            cell_crop = remove_green_halo(cell_crop, threshold=20)

            if shave_bottom_px > 0:
                cw, ch = cell_crop.size
                if ch > shave_bottom_px:
                    cell_crop = cell_crop.crop((0, 0, cw, ch - shave_bottom_px))

            bbox = cell_crop.getbbox()
            final_canvas = Image.new("RGBA", (unit_w, unit_h), (0, 0, 0, 0))
            
            if bbox:
                content_img = cell_crop.crop(bbox)
                if border_thickness > 0:
                    content_img = add_outline(content_img, thickness=border_thickness, color=border_color_hex)
                
                safe_w = unit_w - (safety_margin * 2)
                safe_h = unit_h - (safety_margin * 2)
                if safe_w < 10: safe_w = 10
                if safe_h < 10: safe_h = 10
                
                safe_img = resize_contain(content_img, (safe_w, safe_h))
                s_w, s_h = safe_img.size
                paste_x = (unit_w - s_w) // 2
                paste_y = (unit_h - s_h) // 2
                final_canvas.paste(safe_img, (paste_x, paste_y), safe_img)
            
            stickers.append(final_canvas)
            
    return stickers

# ==========================================
# 📧 4. Email 與 留言板邏輯
# ==========================================
def send_feedback_email(category, user_msg, user_contact):
    if "email" in st.secrets:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = st.secrets["email"]["sender"]
        sender_password = st.secrets["email"]["password"]
        receiver_email = st.secrets["email"].get("receiver", "yesenwu@gmail.com")

        subject = f"【貼圖工廠反饋】{category}"
        body = f"<h3>使用者反饋</h3><p>內容：{user_msg}</p><p>聯絡：{user_contact}</p>"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)
            server.quit()
            return True, "✅ 感謝！您的便利貼已貼上牆，並同步通知開發者。"
        except Exception as e:
            return False, f"❌ Email 發送失敗：{e}"
    else:
        return True, "✅ (模擬模式) 便利貼已貼上！(若有設定 Secrets 則會同步寄出)"

# 初始化留言板資料
if 'board_messages' not in st.session_state:
    st.session_state.board_messages = [
        {"type": "note-yellow", "msg": "希望可以增加更多貓咪的動作！", "author": "愛貓人", "date": "2023-10-01"},
        {"type": "note-blue", "msg": "介面很漂亮，操作很直覺～", "author": "UI設計師", "date": "2023-10-05"},
        {"type": "note-pink", "msg": "許願：想要有黑白漫畫風格！", "author": "漫畫家", "date": "2023-10-12"},
    ]

def add_message(category, msg, author):
    colors = ["note-yellow", "note-pink", "note-blue", "note-green"]
    new_note = {
        "type": random.choice(colors),
        "msg": f"[{category}] {msg}",
        "author": author if author else "匿名創意家",
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    st.session_state.board_messages.insert(0, new_note)

# ==========================================
# 🖥️ 5. UI 佈局邏輯
# ==========================================

# 🏆 新增：Hero Header (主視覺標題)
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">🎨 Line 貼圖半自動產生器</h1>
    <p class="hero-subtitle">ADI Edition • 專為創作者打造的 AI 輔助工具</p>
</div>
""", unsafe_allow_html=True)

# 導覽列
selected_nav = option_menu(
    menu_title=None, 
    options=["創意生成 (Step 1)", "後製工廠 (Step 2)", "使用說明", "留言板"], 
    icons=["lightbulb", "magic", "info-circle", "sticky"], 
    menu_icon="cast", 
    default_index=0, 
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#FFFFFF", "border-radius": "8px", "box-shadow": "0 2px 8px rgba(0,0,0,0.1)"},
        "icon": {"color": "#B4C43F", "font-size": "18px"},
        "nav-link": {"font-size": "16px", "text-align": "center", "margin": "5px", "color": "#5F5F5F", "--hover-color": "#F0F2F6"},
        "nav-link-selected": {"background-color": "#1F323D", "color": "#FFFFFF"},
    }
)

st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True) 

# ==========================================
# 分頁 1: 創意生成 (Step 1)
# ==========================================
if selected_nav == "創意生成 (Step 1)":
    
    with st.container():
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("🧙‍♂️ 設定你的貼圖靈感")
        
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.info("上傳角色參考圖")
            char_img = st.file_uploader(" ", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
            if char_img:
                st.image(char_img, use_container_width=True)
            else:
                st.image("https://placehold.co/400x400/png?text=Upload+Image", use_container_width=True)

        with c2:
            st.write("**風格與文字設定**")
            
            col_style, col_mode = st.columns(2)
            with col_style:
                selected_style_name = st.selectbox("🎨 選擇畫風", list(ART_STYLES.keys()))
            with col_mode:
                generation_mode = st.radio("📝 文字模式", ["🎲 隨機混搭", "✅ 自選分類"], horizontal=True)

            phrase_pool = []
            if generation_mode == "🎲 隨機混搭":
                for cat in STICKER_CATEGORIES.values(): phrase_pool.extend(cat)
            else:
                cats = st.multiselect("選擇分類", list(STICKER_CATEGORIES.keys()), default=["日常問候", "工作職場"])
                for c in cats: phrase_pool.extend(STICKER_CATEGORIES[c])
            
            if st.button("🔄 抽取隨機文字組合", use_container_width=True):
                if len(phrase_pool) < 12: phrase_pool = ["無文字"] * 12
                st.session_state.selected_phrases = random.sample(phrase_pool, 12) if len(phrase_pool) >= 12 else random.choices(phrase_pool, k=12)

            if 'selected_phrases' not in st.session_state:
                if len(phrase_pool) < 12: phrase_pool = ["測試文字"] * 12
                st.session_state.selected_phrases = random.sample(phrase_pool, 12) if len(phrase_pool) >= 12 else random.choices(phrase_pool, k=12)
                
            st.write("---")
            st.write("📌 **預計生成的文字：**")
            
            tags_html = "".join([f"<span class='custom-tag'>{p}</span>" for p in st.session_state.selected_phrases])
            st.markdown(tags_html, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    if char_img:
        with st.container():
            st.markdown('<div class="css-card">', unsafe_allow_html=True)
            st.subheader("🚀 你的專屬咒語 (Prompt)")
            
            prompt = generate_dynamic_prompt(st.session_state.selected_phrases, ART_STYLES[selected_style_name])
            st.code(prompt, language="markdown")
            
            st.markdown(f"<p style='color:#5F5F5F'>💡 複製上方代碼，前往 Google Gemini 貼上並上傳圖片即可。</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 分頁 2: 後製工廠 (Step 2)
# ==========================================
elif selected_nav == "後製工廠 (Step 2)":
    
    with st.container():
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("⚙️ 參數控制台")
        
        p1, p2, p3, p4 = st.columns(4)
        with p1:
            green_threshold = st.number_input("去背強度", 50, 250, 150)
        with p2:
            shave_bottom_px = st.number_input("底部修邊 (px)", 0, 10, 2)
        with p3:
            border_thickness = st.number_input("外框粗細", 0.0, 5.0, 1.5)
        with p4:
            c_name = st.selectbox("外框顏色", list(PRESET_COLORS.keys()))
            border_color_hex = PRESET_COLORS[c_name]
            st.markdown(f"預覽：<span style='color:{border_color_hex}'>■■■</span>", unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("📤 圖片處理區")
        
        uploaded_file = st.file_uploader("拖曳 Gemini 生成的綠底圖到這裡", type=['png', 'jpg'])
        
        if uploaded_file:
            if st.button("✨ 開始魔法處理", type="primary", use_container_width=True):
                with st.spinner("正在施展魔法..."):
                    processed_stickers = process_sticker_grid(
                        uploaded_file, green_threshold, border_thickness, border_color_hex, 16, shave_bottom_px
                    )
                    st.session_state.processed_stickers = processed_stickers
                    st.session_state.has_processed = True
            
            if st.session_state.get('has_processed') and 'processed_stickers' in st.session_state:
                stickers = st.session_state.processed_stickers
                st.success(f"處理完成！共 {len(stickers)} 張")
                
                cols = st.columns(4)
                for idx, sticker in enumerate(stickers):
                    with cols[idx % 4]:
                        st.image(sticker, caption=f"No.{idx+1:02d}", use_container_width=True)
                
                st.divider()
                
                d1, d2 = st.columns([2, 1])
                with d1:
                    selected_idx = st.selectbox("選擇封面代表圖", range(len(stickers)), format_func=lambda x: f"No.{x+1:02d}")
                    
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w") as zf:
                        for idx, sticker in enumerate(stickers):
                            img_byte_arr = io.BytesIO()
                            sticker.save(img_byte_arr, format='PNG')
                            zf.writestr(f"{idx+1:02d}.png", img_byte_arr.getvalue())
                        
                        main_img = resize_contain(stickers[selected_idx], (240, 240))
                        main_byte_arr = io.BytesIO()
                        main_img.save(main_byte_arr, format='PNG')
                        zf.writestr("main.png", main_byte_arr.getvalue())

                        tab_img = resize_contain(stickers[selected_idx], (96, 74))
                        tab_byte_arr = io.BytesIO()
                        tab_img.save(tab_byte_arr, format='PNG')
                        zf.writestr("tab.png", tab_byte_arr.getvalue())

                    st.download_button(
                        label="📥 下載完整上架包 (.zip)",
                        data=zip_buffer.getvalue(),
                        file_name="line_stickers_adi_edition.zip",
                        mime="application/zip"
                    )
                with d2:
                     st.image(stickers[selected_idx], caption="Main Cover", width=120)

        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 分頁 3: 使用說明
# ==========================================
elif selected_nav == "使用說明":
    with st.container():
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📖 Line 貼圖魔法工廠操作指南
        
        #### 1. 創意生成 (Step 1)
        * **上傳圖片**：選擇一張照片作為角色的基礎。
        * **選擇風格**：從 10+ 種風格中選擇。
        * **抽取文字**：點擊按鈕隨機抽取 12 組貼圖用語。
        * **複製 Prompt**：程式會自動產生給 AI 的指令，請複製並貼到 Gemini。

        #### 2. 後製工廠 (Step 2)
        * **上傳成品**：將 Gemini 算好的 4x3 綠底大圖下載並上傳到這裡。
        * **調整參數**：如果發現邊緣有綠色殘留，請調整「去背強度」或「底部修邊」。
        * **一鍵打包**：系統會自動切圖、加框、調整尺寸，最後產生 ZIP 檔。
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 分頁 4: 留言板 (Sticky Board)
# ==========================================
elif selected_nav == "留言板":
    
    with st.container():
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("📝 寫張便利貼")
        
        with st.form(key="sticky_form"):
            col_input, col_meta = st.columns([3, 1])
            with col_input:
                fb_msg = st.text_area("寫下你的想法...", height=100, placeholder="例如：希望能增加「水墨畫風格」...")
            with col_meta:
                fb_category = st.selectbox("分類", ["🎨 許願畫風", "📝 許願語錄", "🐛 報修", "💡 其他"])
                fb_author = st.text_input("署名 (選填)", placeholder="暱稱")
                st.markdown("<br>", unsafe_allow_html=True)
                submit_btn = st.form_submit_button("📌 貼上牆", type="primary", use_container_width=True)

            if submit_btn:
                if fb_msg.strip():
                    add_message(fb_category, fb_msg, fb_author)
                    success, resp = send_feedback_email(fb_category, fb_msg, fb_author)
                    st.success(resp)
                    st.rerun()
                else:
                    st.warning("請寫點東西再貼喔！")
        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("📌 大家的心聲 (每月清除)")
    
    messages = st.session_state.board_messages
    cols = st.columns(3)
    
    for idx, note in enumerate(messages):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="sticky-note {note['type']}">
                <div style="font-weight:bold; margin-bottom:10px; opacity:0.6; font-size:0.8em;">
                    {note['date']} | {note['author']}
                </div>
                <div style="font-size:1.1em; line-height:1.4;">
                    {note['msg']}
                </div>
            </div>
            """, unsafe_allow_html=True)
