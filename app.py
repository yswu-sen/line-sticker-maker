import streamlit as st
import random
from PIL import Image, ImageFilter, ImageColor
import numpy as np
import io
import zipfile

# --- 設定頁面 ---
st.set_page_config(page_title="Line 貼圖工廠 V4.4 (修復外框裁切)", layout="wide")

# --- 1. 貼圖常用語資料庫 ---
STICKER_CATEGORIES = {
    "日常問候": ["早安", "安安", "抱歉假日打擾", "晚安瑪卡巴卡", "睡了沒？", "在嗎？", "呷霸沒", "撤！", "回家囉", "已出門", "到家！", "在路上", "修但幾勒", "放假~", "開工啦", "哈囉", "Bye Bye"],
    "工作職場": ["收到", "了解", "我看看", "處理中", "快好了", "鶴", "好勒", "沒問題", "金都蝦", "辛苦了", "這裡有Bug", "開會中", "不想上班", "會後討論", "開不完的會", "加班命…", "請幫確認", "麻煩您！", "感謝支援～", "坐等下班", "我愛(恨)工作", "可以"],
    "情緒表達": ["哭阿", "笑死", "怕豹！", "傻眼", "無言", "???", "!!!", "真的假的", "氣死", "心累", "懷疑人生", "壓力山大", "嚇死寶寶", "母湯喔", "想躺平", "不想動", "悶…", "QQ", "扯爆扯", "傻爆眼", "沒get到", "耶死", "啵兒棒", "送啦！", "有你真好～"],
    "網路流行/梗": ["歸剛欸", "我就爛", "Duck不必", "是在哈囉", "像極了愛情", "真香", "ㄜ…", "芭比Q了", "回答我Look in eyes", "Tell Me Why ", "牛～逼", "見笑轉生氣", "要確誒", "再泉啊(齁懶)", "先緩緩", "太狠了", "頂不住", "笑爛", "破防", "蛤？", "穩了", "翻車了", "來吃瓜~", "4 ni？", "UCCU你看看你", "超ㄎㄧㄤ ", "甘阿捏？", "哩洗咧烤！"],
    "簡短回應": ["+1", "OK", "No", "Yes", "GOGOGO", "讚", "強", "行", "不行啦", "沒差", "隨你", "是喔？", "不會吧…", "也是啦", "對啦", "錯了吧", "再看看？", "等一下", "馬上來", "咖緊捏", "慢慢來", "幾霸分100"],
    "生活日常": ["吃飯中", "剛吃飽", "去呷奔", "餓", "我請", "需補充咖啡因…", "來睏", "熬夜中", "早起痛苦", "追劇ing", "手機滑起來", "放空中", "這禮拜吃土", "領錢囉", "買買買", "剁手", "減肥明天再說", "起來嗨"],
    "可愛短句/撒嬌": ["來啦", "走啦", "好了啦", "不要啦", "拜託啦", "救我", "求幫忙", "愛老虎油", "Sorry！", "謝啦", "感恩", "感謝你", "死勾以～", "厲～害", "交給偶", "我負責"],
    "收尾萬用": ["下次再說", "改天啦", "再聯絡", "先醬", "掰啦", "晚點聊", "明天續戰", "Take care", "注意安全", "保重身體"]
}

# --- 2. 風格定義資料庫 ---
ART_STYLES = {
    "🌟 可愛 Q 版 (預設)": "可愛、活潑、2D平面、Q版二頭身、向量插畫風格",
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

# --- 3. 精選色票 ---
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

# --- 4. 輔助函式 ---

def add_outline(input_image, thickness=1.5, color="#000000"):
    """
    【修正版】為圖片加上指定顏色的邊框 (自動擴充畫布防止裁切)
    """
    if thickness <= 0:
        return input_image
        
    img = input_image.convert("RGBA")
    
    # 1. 計算需要的擴充邊距 (半徑 + 安全緩衝)
    radius = int(round(thickness))
    if radius < 1: radius = 1
    padding = radius + 5  # 多留一點空間，確保外框完全不被切到
    
    # 2. 建立擴大的畫布
    old_w, old_h = img.size
    new_w = old_w + (padding * 2)
    new_h = old_h + (padding * 2)
    
    padded_img = Image.new('RGBA', (new_w, new_h), (0, 0, 0, 0))
    
    # 3. 將原圖貼在正中間
    padded_img.paste(img, (padding, padding))
    
    # 4. 針對擴大後的圖片進行濾鏡處理 (製作遮罩)
    mask = padded_img.getchannel('A')
    filter_size = radius * 2 + 1
    dilated_mask = mask.filter(ImageFilter.MaxFilter(filter_size))
    
    # 5. 組合外框層
    rgba_color = ImageColor.getrgb(color) + (255,)
    outline_bg = Image.new('RGBA', padded_img.size, rgba_color)
    
    output_img = Image.new('RGBA', padded_img.size, (0, 0, 0, 0))
    output_img.paste(outline_bg, mask=dilated_mask)       # 先貼外框
    output_img.paste(padded_img, (0, 0), padded_img)      # 再貼本體
    
    # 6. 最後根據新的邊界裁切，確保不留多餘空白
    bbox = output_img.getbbox()
    if bbox:
        return output_img.crop(bbox)
    
    return output_img

def remove_green_halo(image, threshold=30):
    """
    強力去綠邊算法
    """
    img_np = np.array(image.convert("RGBA"))
    r, g, b, a = img_np.T
    
    # 綠色優勢計算
    g_dominance = g.astype(np.int16) - np.maximum(r, b).astype(np.int16)
    
    # 判定去背
    green_mask = (g_dominance > threshold) & (a > 0)
    
    img_np[..., 3][green_mask.T] = 0
    return Image.fromarray(img_np)

def resize_contain(image, target_size):
    """將圖片等比例縮放並置中"""
    target_w, target_h = target_size
    img_w, img_h = image.size
    
    # 避免除以零
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
    """處理圖片核心邏輯"""
    img = Image.open(image_file).convert("RGBA")
    
    target_size = (1480, 960)
    if img.size != target_size:
        img = img.resize(target_size, Image.Resampling.LANCZOS)

    data = np.array(img)
    red, green, blue, alpha = data.T
    
    # 1. 基礎去背
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
            
            # 初步裁切
            cell_crop = result_img.crop((left, upper, right, lower))
            
            # --- 去綠邊處理 (Despill) ---
            cell_crop = remove_green_halo(cell_crop, threshold=20)

            # --- 底部物理修邊 (Pixel Shave) ---
            if shave_bottom_px > 0:
                cw, ch = cell_crop.size
                # 只有當高度足夠時才切
                if ch > shave_bottom_px:
                    cell_crop = cell_crop.crop((0, 0, cw, ch - shave_bottom_px))

            bbox = cell_crop.getbbox()
            
            final_canvas = Image.new("RGBA", (unit_w, unit_h), (0, 0, 0, 0))
            
            if bbox:
                # 1. 取得去背後的內容
                content_img = cell_crop.crop(bbox)
                
                # 2. 先加框 (修正版：這裡尺寸會變大，但不會被切掉)
                if border_thickness > 0:
                    content_img = add_outline(content_img, thickness=border_thickness, color=border_color_hex)
                
                # 3. 計算安全區域
                # 重點：安全區域必須扣除留白
                safe_w = unit_w - (safety_margin * 2)
                safe_h = unit_h - (safety_margin * 2)
                
                if safe_w < 10: safe_w = 10
                if safe_h < 10: safe_h = 10
                
                # 4. 將「加框後」的圖片縮放至安全區域
                # 這保證了 (內容+框) 絕對小於 (格子 - 留白)
                safe_img = resize_contain(content_img, (safe_w, safe_h))
                
                # 5. 置中貼上
                s_w, s_h = safe_img.size
                paste_x = (unit_w - s_w) // 2
                paste_y = (unit_h - s_h) // 2
                final_canvas.paste(safe_img, (paste_x, paste_y), safe_img)
            
            stickers.append(final_canvas)
            
    return stickers

# --- Streamlit 主介面 ---
st.title("🤖 Line 貼圖工廠 V4.4 (精準留白+外框修復版)")

# 側邊欄
st.sidebar.header("1. 角色與風格")
char_img = st.sidebar.file_uploader("上傳角色參考圖", type=['png', 'jpg', 'jpeg'])

st.sidebar.subheader("🎨 風格選擇")
selected_style_name = st.sidebar.selectbox("選擇畫風", options=list(ART_STYLES.keys()), index=0)
st.sidebar.caption(ART_STYLES[selected_style_name])

st.sidebar.markdown("---")
st.sidebar.subheader("📝 貼圖文字設定")

generation_mode = st.sidebar.radio("文字生成模式", ["🎲 全部隨機", "✅ 自選分類"])
phrase_pool = []

if generation_mode == "🎲 全部隨機":
    for cat_phrases in STICKER_CATEGORIES.values():
        phrase_pool.extend(cat_phrases)
else:
    selected_categories = st.sidebar.multiselect(
        "選擇要包含的分類 (可複選)",
        options=list(STICKER_CATEGORIES.keys()),
        default=["日常問候", "工作職場"]
    )
    for cat in selected_categories:
        phrase_pool.extend(STICKER_CATEGORIES[cat])

st.sidebar.markdown("---")
st.sidebar.subheader("🔧 後製設定 (參數調整)")

# 1. 綠色處理
green_threshold = st.sidebar.slider("1. 綠色判定閥值", 50, 250, 150)
shave_bottom_px = st.sidebar.slider("2. 底部修邊 (px)", 0, 10, 2, help="若圖片底部出現綠線，請增加此數值以直接切除底部像素")

st.sidebar.divider()

# 2. 外框設定
st.sidebar.write("3. 外框設定")
col_thick, col_color = st.sidebar.columns([1, 1])

with col_thick:
    border_thickness = st.number_input("外框粗細 (px)", min_value=0.0, max_value=10.0, value=1.5, step=0.5)

with col_color:
    # 預設選取黑色 (Index 0)
    selected_color_name = st.selectbox("外框顏色", options=list(PRESET_COLORS.keys()), index=0)
    border_color_hex = PRESET_COLORS[selected_color_name]

st.sidebar.markdown(f"目前顏色：<span style='color:{border_color_hex}; font-size:20px'>■</span> {selected_color_name}", unsafe_allow_html=True)

st.sidebar.divider()

# 3. 留白
safety_margin = st.sidebar.slider("4. 邊緣留白 (px)", 0, 50, 16, help="確保外框不會貼到邊緣，建議值 15-20")

st.sidebar.markdown("---")
refresh_btn = st.sidebar.button("🔄 重新抽取文字")

if 'selected_phrases' not in st.session_state or refresh_btn:
    if len(phrase_pool) < 12:
        st.warning(f"⚠️ 詞彙不足，將使用重複填充。")
        st.session_state.selected_phrases = random.choices(phrase_pool, k=12) if phrase_pool else ["無文字"] * 12
    else:
        st.session_state.selected_phrases = random.sample(phrase_pool, 12)

# 區域 1
st.subheader("1. 獲取 Prompt 並前往 Gemini 生成")
if char_img:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(char_img, width=150, caption="角色設定")
    with col2:
        st.success(f"已套用風格：{selected_style_name}")
        final_prompt = generate_dynamic_prompt(st.session_state.selected_phrases, ART_STYLES[selected_style_name])
        st.markdown("👇 **點擊右上角 'Copy' 複製 Prompt**")
        st.code(final_prompt, language="markdown")
        st.markdown("[👉 前往 Gemini 網頁版貼上](https://gemini.google.com/app)")
else:
    st.info("請先在左側上傳角色圖片")

st.markdown("---")

# 區域 2
st.subheader("2. 上傳 Gemini 結果圖與打包")
uploaded_file = st.file_uploader("Drag and drop file here", type=['png', 'jpg', 'jpeg'], key="uploader_v4_4")

apply_settings = st.checkbox("預覽模式 (勾選後即時運算，取消勾選可暫停)", value=True)

if uploaded_file and apply_settings:
    spinner_text = '正在執行強力去綠、修邊與加框處理...' 
    with st.spinner(spinner_text):
        try:
            stickers = process_sticker_grid(
                uploaded_file, 
                green_threshold=green_threshold, 
                border_thickness=border_thickness,
                border_color_hex=border_color_hex, 
                safety_margin=safety_margin,
                shave_bottom_px=shave_bottom_px
            )
            
            st.success(f"🎉 處理完成！共 {len(stickers)} 張貼圖")
            
            # --- 全覽顯示 ---
            st.markdown(f"##### 貼圖預覽 (No.01 - No.{len(stickers)})")
            
            cols = st.columns(4)
            for idx, sticker in enumerate(stickers):
                with cols[idx % 4]:
                    st.image(sticker, caption=f"No.{idx+1:02d}", use_column_width=True)
            
            st.markdown("---")
            st.subheader("3. 選擇封面並下載")
            
            col_select, col_preview = st.columns([2, 1])
            with col_select:
                st.info("請從上方預覽圖中，選定一張作為主要封面(main)與標籤縮圖(tab)。")
                selected_idx = st.selectbox(
                    "選擇封面貼圖編號",
                    options=range(len(stickers)),
                    format_func=lambda x: f"No.{x+1:02d}",
                    index=0
                )
            
            with col_preview:
                st.image(stickers[selected_idx], caption="目前選定的封面圖", width=120)

            # --- 打包邏輯 ---
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                # 1. 寫入一般貼圖
                for idx, sticker in enumerate(stickers):
                    img_byte_arr = io.BytesIO()
                    sticker.save(img_byte_arr, format='PNG')
                    zf.writestr(f"{idx+1:02d}.png", img_byte_arr.getvalue())
                
                # 2. 寫入 Main (240x240)
                main_img = resize_contain(stickers[selected_idx], (240, 240))
                main_byte_arr = io.BytesIO()
                main_img.save(main_byte_arr, format='PNG')
                zf.writestr("main.png", main_byte_arr.getvalue())

                # 3. 寫入 Tab (96x74)
                tab_img = resize_contain(stickers[selected_idx], (96, 74))
                tab_byte_arr = io.BytesIO()
                tab_img.save(tab_byte_arr, format='PNG')
                zf.writestr("tab.png", tab_byte_arr.getvalue())
            
            st.download_button(
                label="📥 下載完整上架包 (含 main/tab/01-12)", 
                data=zip_buffer.getvalue(), 
                file_name="line_stickers_pack_v4.4.zip", 
                mime="application/zip", 
                type="primary"
            )
            
        except Exception as e:
            st.error(f"發生錯誤：{e}")
            import traceback
            st.text(traceback.format_exc())
