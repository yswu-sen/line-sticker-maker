import streamlit as st
import random
from PIL import Image, ImageFilter, ImageChops
import numpy as np
import io
import zipfile

# --- 設定頁面 ---
st.set_page_config(page_title="Line 貼圖工廠 V3.8 (全覽+強化去邊)", layout="wide")

# --- 1. 貼圖常用語資料庫 ---
STICKER_CATEGORIES = {
    "日常問候": ["早安", "安安", "抱歉假日打擾", "晚安瑪卡巴卡", "睡了沒？", "在嗎？", "呷霸沒", "撤！", "回家囉", "已出門", "到家！", "在路上", "修但幾勒", "放假~", "開工啦", "哈囉", "Bye Bye"],
    "工作職場": ["收到", "了解", "我看看", "處理中", "快好了", "鶴", "好勒", "沒問題", "金都蝦", "辛苦了", "這裡有Bug", "開會中", "不想上班", "會後討論", "開不完的會", "加班命…", "請幫確認", "麻煩您！", "感謝支援～", "坐等下班", "我愛(ㄏㄣˋ)工作", "可以"],
    "情緒表達": ["哭阿", "笑死", "怕豹！", "傻眼", "無言", "???", "!!!", "真的假的", "氣死", "心累", "懷疑人生", "壓力山大", "嚇死寶寶", "母湯喔", "想躺平", "不想動", "悶…", "QQ", "扯爆扯", "傻爆眼", "沒get到", "耶死", "啵兒棒", "送啦！", "有你真好～"],
    "網路流行/梗": ["歸剛欸", "我就爛", "Duck不必", "是在哈囉", "像極了愛情", "真香", "ㄜ…", "芭比Q了", "回答我Look in eyes", "Tell Me Why ", "牛～逼", "見笑轉生氣", "要確誒", "再泉啊(齁懶)", "先緩緩", "太狠了", "頂不住", "笑爛", "破防", "蛤？", "穩了", "翻車了", "來吃瓜~", "4 ni？", "UCCU你看看你", "超ㄎㄧㄤ ", "甘阿捏？", "哩洗咧烤！"],
    "簡短回應": ["+1", "OK", "No", "Yes", "GOGOGO", "讚", "強", "可轉", "行", "不行啦", "沒差", "隨你", "是喔？", "不會吧…", "也是啦", "對啦", "錯了吧", "再看看？", "等一下", "馬上來", "咖緊捏", "慢慢來", "幾霸分100"],
    "生活日常": ["吃飯中", "剛吃飽", "去呷奔", "餓", "我請", "需補充咖啡因…", "來睏", "熬夜中", "早起痛苦", "追劇ing", "手機滑起來", "放空中", "這禮拜吃土", "領錢囉", "買買買", "剁手", "減肥明天再說", "起來嗨"],
    "可愛短句/撒嬌": ["來啦", "走啦", "好了啦", "不要啦", "拜託啦", "救我", "求幫忙", "愛老虎油", "Sorry！", "謝啦", "感恩", "感謝你", "死給～", "厲～害", "交給偶", "我負責"],
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

# --- 3. 輔助函式 ---
def add_black_border(input_image, thickness=3):
    """為圖片加上黑色邊框"""
    img = input_image.convert("RGBA")
    # 取得 Alpha 通道作為遮罩
    mask = img.getchannel('A')
    
    # 擴張遮罩 (Dilation) 來製作邊框區域
    # MaxFilter 會讓白色區域變大，模擬擴張效果
    dilated_mask = mask.filter(ImageFilter.MaxFilter(thickness * 2 + 1))
    
    # 建立純黑背景
    black_bg = Image.new('RGBA', img.size, (0, 0, 0, 255))
    output_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
    
    # 先貼上黑色擴張後的樣子
    output_img.paste(black_bg, mask=dilated_mask)
    # 再貼上原圖
    output_img.paste(img, (0, 0), img)
    
    return output_img

def erode_edges(input_image, pixels=1):
    """侵蝕邊緣 (消除綠邊關鍵)"""
    if pixels <= 0: return input_image
    
    img = input_image.convert("RGBA")
    r, g, b, a = img.split()
    
    # 使用 MinFilter 進行侵蝕 (讓 Alpha 通道縮小)
    # 奇數 filter size: 3=侵蝕1px, 5=侵蝕2px
    filter_size = pixels * 2 + 1 
    new_a = a.filter(ImageFilter.MinFilter(filter_size))
    
    # 重新組合
    img.putalpha(new_a)
    return img

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

def process_sticker_grid(image_file, green_threshold=150, color_tolerance=100, enable_erode=0, border_thickness=0):
    """處理圖片核心邏輯"""
    img = Image.open(image_file).convert("RGBA")
    
    target_size = (1480, 960)
    if img.size != target_size:
        img = img.resize(target_size, Image.Resampling.LANCZOS)

    data = np.array(img)
    red, green, blue, alpha = data.T
    
    # 1. 執行基礎去背
    green_areas = (green > green_threshold) & (red < color_tolerance) & (blue < color_tolerance)
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
            final_canvas = Image.new("RGBA", (unit_w, unit_h), (0, 0, 0, 0))
            bbox = cell_crop.getbbox()
            
            if bbox:
                content_img = cell_crop.crop(bbox)
                
                # --- 新增：邊緣處理流程 ---
                # A. 侵蝕 (Erode) - 向內縮小，切掉綠邊
                if enable_erode > 0:
                    content_img = erode_edges(content_img, pixels=enable_erode)
                
                # B. 加框 (Border) - 在處理完邊緣後加上黑框
                if border_thickness > 0:
                    content_img = add_black_border(content_img, thickness=border_thickness)
                
                # --- 尺寸調整與置中 ---
                c_w, c_h = content_img.size
                if c_w > unit_w or c_h > unit_h:
                    content_img.thumbnail((unit_w, unit_h), Image.Resampling.LANCZOS)
                    c_w, c_h = content_img.size 

                paste_x = (unit_w - c_w) // 2
                paste_y = (unit_h - c_h) // 2
                final_canvas.paste(content_img, (paste_x, paste_y), content_img)
            
            stickers.append(final_canvas)
            
    return stickers

# --- Streamlit 主介面 ---
st.title("🤖 Line 貼圖工廠 V3.8 (全覽+強化去邊)")

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
st.sidebar.subheader("🔧 後製設定 (進階)")
green_threshold = st.sidebar.slider("1. 綠色判定閥值", 50, 250, 150, help="數字越大，只有越綠的地方會被去掉")
erode_level = st.sidebar.slider("2. 邊緣內縮 (px)", 0, 5, 1, help="有效消除綠邊！建議設為 1 或 2，會將邊緣往內切")
border_thickness = st.sidebar.slider("3. 黑框粗細 (px)", 0, 10, 3, help="設為 0 則不加框")

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
st.subheader("2. 上傳 Gemini 結果圖")
uploaded_file = st.file_uploader("Drag and drop file here", type=['png', 'jpg', 'jpeg'], key="uploader_v3_8")

if uploaded_file:
    spinner_text = '正在執行去背、內縮邊緣與加框處理...' 
    with st.spinner(spinner_text):
        try:
            stickers = process_sticker_grid(
                uploaded_file, 
                green_threshold=green_threshold, 
                enable_erode=erode_level, 
                border_thickness=border_thickness
            )
            st.success(f"🎉 處理完成！共 {len(stickers)} 張貼圖")
            
            # --- 修正：全覽顯示 (4欄佈局) ---
            st.markdown(f"##### 貼圖預覽 (共 {len(stickers)} 張)")
            cols = st.columns(4) # 建立 4 個欄位
            for idx, sticker in enumerate(stickers):
                # 利用餘數 (idx % 4) 決定圖片要放在第幾個欄位
                with cols[idx % 4]:
                    st.image(sticker, caption=f"No.{idx+1}", use_column_width=True)
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for idx, sticker in enumerate(stickers):
                    img_byte_arr = io.BytesIO()
                    sticker.save(img_byte_arr, format='PNG')
                    zf.writestr(f"sticker_{idx+1:02d}.png", img_byte_arr.getvalue())
            
            st.download_button("📥 下載完整貼圖包 (ZIP)", zip_buffer.getvalue(), "stickers.zip", "application/zip", type="primary")
        except Exception as e:
            st.error(f"發生錯誤：{e}")
