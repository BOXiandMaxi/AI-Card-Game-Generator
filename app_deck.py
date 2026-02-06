import streamlit as st
import os
import json
import base64
from io import BytesIO  # [เพิ่ม] ต้องใช้ตัวนี้เพื่อจัดการไฟล์ใน RAM
from PIL import Image   # [เพิ่ม] ต้องใช้ PIL เพื่อย่อรูป
from config import PATHS

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="My Card Deck", layout="wide")

# 1. ฟังก์ชันโหลด CSS
def load_css(file_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(base_dir, 'assets', 'css', file_name)
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    else:
        st.error(f"❌ หาไฟล์ CSS ไม่เจอที่: {css_path}")

# 2. [แก้ใหม่] ฟังก์ชันแปลงรูปเป็น Base64 แบบย่อขนาด (Thumbnail)
def get_image_base64(image_path, size=(300, 420)): # กำหนดขนาดรูปให้เล็กลง
    try:
        # เปิดรูปด้วย PIL
        with Image.open(image_path) as img:
            # ย่อรูปให้เล็กลงเพื่อลดภาระ WebSocket (รักษาอัตราส่วน)
            img.thumbnail(size)
            
            # บันทึกลง RAM (Buffer) แทนการบันทึกไฟล์จริง
            buffered = BytesIO()
            img.save(buffered, format="PNG", optimize=True, quality=80)
            
            # แปลงเป็น Base64
            return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}"
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return ""

# 3. ฟังก์ชันโหลดการ์ด
def load_cards_from_folder():
    cards = []
    root_folder = PATHS['output_folder']
    if not os.path.exists(root_folder): return []

    for folder_name, subfolders, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith(".png") and filename.startswith("card"):
                full_path = os.path.join(folder_name, filename)
                animal_name = os.path.basename(folder_name)
                cards.append({
                    "name": animal_name,
                    "path": full_path,
                    "file": filename
                })
    return cards

# --- เริ่มแสดงผล ---
load_css("app_deck.css") 

# เพิ่ม CSS พิเศษสำหรับดัน Z-Index การ์ดให้กดติดแน่นอน
st.markdown("""
<style>
    /* บังคับให้การ์ดลอยเหนือทุกอย่าง และเปลี่ยนเมาส์เป็นรูปมือ */
    .gallery-card-trigger {
        position: relative;
        z-index: 10 !important; 
        cursor: pointer !important;
        transition: transform 0.2s;
    }
    .gallery-card-trigger:hover {
        transform: scale(1.05);
        z-index: 20 !important;
    }
    /* ให้รูปภาพไม่บังการคลิก */
    .gallery-card-trigger img {
        pointer-events: none;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎴 คลังการ์ดของฉัน (My Deck)")

# ปุ่มกลับหน้าเกม
st.markdown("""
    <a href="http://localhost:5000" target="_self" class="btn-back">
        ⬅️ Back to Game
    </a>
    <br><br>
""", unsafe_allow_html=True)

# โหลดข้อมูลการ์ด
my_cards = load_cards_from_folder()

if not my_cards:
    st.warning("ยังไม่มีการ์ดในคลังเลย! ลองไปรันโปรแกรมสร้างการ์ดก่อนนะ")
else:
    st.write(f"ตอนนี้มีการ์ดทั้งหมด **{len(my_cards)}** ใบ")

    # =================================================================================
    # [ส่วน Javascript & Modal]
    # =================================================================================
    
    # เตรียมข้อมูล JSON (แปลงรูปทีละใบ)
    # [แก้] ย้าย Logic มาตรงนี้เพื่อลดการทำงานซ้ำซ้อน
    cards_data_for_js = []
    
    # สร้าง Container สำหรับ Grid
    cols = st.columns(4)
    
    for i, card in enumerate(my_cards):
        # แปลงรูปเป็น Base64 (แบบย่อแล้ว)
        img_b64 = get_image_base64(card['path'])
        
        # เก็บใส่ List ไว้ส่งให้ JS
        cards_data_for_js.append({'name': card['name'], 'img': img_b64})
        
        # วาดการ์ดลงจอ
        col = cols[i % 4]
        with col:
            card_html = f"""
            <div class="gallery-card gallery-card-trigger" data-index="{i}">
                <img src="{img_b64}" style="width:100%; border-radius:6px;">
                <div class="gallery-card-name">{card['name']}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

    # แปลงข้อมูลเป็น JSON String
    js_data = json.dumps(cards_data_for_js)

    # ฝัง Script และ Modal ไว้ท้ายสุด
    st.markdown(f"""
    <div id="card3DModal" class="card-3d-modal" style="display: none;">
        <div class="modal-close" id="btnCloseModal">×</div>
        <div class="view-instructions">🖱️ คลิกค้างและลากเพื่อหมุน 360°</div>
        
        <div class="card-3d-scene">
            <div id="card3DObject" class="card-3d-object">
                <div class="card-face face-front">
                    <img id="card3DImage" src="" alt="Front">
                </div>
                <div class="card-face face-back">
                    <div style="width:100%; height:100%; background:#1a0033; border:2px solid #6b0dad; border-radius:20px; display:flex; justify-content:center; align-items:center;">
                        <img src="https://i.imgur.com/Pj6qQk0.png" style="width:100%; height:100%; object-fit:cover; opacity:0.5;">
                    </div>
                </div>
            </div>
        </div>
        <div class="card-name-3d" id="cardName3D"></div>
    </div>

    <script>
    // --- รับข้อมูลการ์ดทั้งหมดเข้าตัวแปร JS ---
    const allCards = {js_data};

    // --- ตัวแปรควบคุมการหมุน ---
    var isDragging = false;
    var lastMouseX = 0, lastMouseY = 0;
    var currentRotateX = 0, currentRotateY = 0;

    // --- ฟังก์ชันเปิด Modal ---
    function openModal(index) {{
        const cardData = allCards[index];
        if (!cardData) return;

        const modal = document.getElementById('card3DModal');
        const cardImg = document.getElementById('card3DImage');
        const cardName = document.getElementById('cardName3D');
        const cardObj = document.getElementById('card3DObject');

        // รีเซ็ตมุมหมุน
        currentRotateX = 0; currentRotateY = 0;
        if(cardObj) cardObj.style.transform = 'rotateY(0deg) rotateX(0deg)';

        // ใส่ข้อมูล
        if(cardImg) cardImg.src = cardData.img;
        if(cardName) cardName.textContent = cardData.name;

        // แสดงผล
        if(modal) modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }}

    // --- ฟังก์ชันปิด Modal ---
    function closeModal() {{
        const modal = document.getElementById('card3DModal');
        if(modal) modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }}

    // ===============================================================
    // [จุดแก้สำคัญ] ใช้ Event Delegation แบบ Polling (วนเช็ค)
    // เพราะ window.parent บางทีเข้าถึงไม่ได้ถ้าติด Cross-Origin
    // ===============================================================
    
    function handleGlobalClick(e) {{
        // 1. เช็คการ์ด
        const cardTrigger = e.target.closest('.gallery-card-trigger');
        if (cardTrigger) {{
            e.preventDefault(); 
            e.stopPropagation(); // หยุดไม่ให้ Streamlit เอาไปกิน
            const index = cardTrigger.getAttribute('data-index');
            openModal(index);
            return;
        }}

        // 2. เช็คปุ่มปิด
        if (e.target.id === 'btnCloseModal' || e.target.closest('#btnCloseModal')) {{
            closeModal();
            return;
        }}
        
        // 3. เช็คพื้นที่ว่าง
        if (e.target.id === 'card3DModal') {{
            closeModal();
        }}
    }}

    // แปะ Event Listener ที่ body ของ document นี้ (ไม่ต้องไป parent)
    document.addEventListener('click', handleGlobalClick, true); // true = Capture phase (ดักจับก่อนใคร)

    // --- Logic การหมุน 3D ---
    document.addEventListener('mousedown', function(e) {{
        if (e.target.closest('.card-3d-scene')) {{
            isDragging = true;
            lastMouseX = e.pageX;
            lastMouseY = e.pageY;
            e.preventDefault();
        }}
    }});

    document.addEventListener('mousemove', function(e) {{
        if (!isDragging) return;
        var deltaX = e.pageX - lastMouseX;
        var deltaY = e.pageY - lastMouseY;
        
        currentRotateY += deltaX * 0.5;
        currentRotateX -= deltaY * 0.5;
        currentRotateX = Math.max(-90, Math.min(90, currentRotateX));

        lastMouseX = e.pageX;
        lastMouseY = e.pageY;

        var cardObj = document.getElementById('card3DObject');
        if(cardObj) {{
            cardObj.style.transform = "rotateY(" + currentRotateY + "deg) rotateX(" + currentRotateX + "deg)";
        }}
    }});

    document.addEventListener('mouseup', function() {{ isDragging = false; }});
    document.addEventListener('keydown', function(e) {{ if (e.key === 'Escape') closeModal(); }});

    </script>
    """, unsafe_allow_html=True)