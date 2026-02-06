from flask import Flask, render_template, request, jsonify, send_from_directory
from modules.game_logic import GameLogic
from modules.image_utils import ImageProcessor
# 1. เปิดใช้งานการ Import AI
from modules.ai_generator import AIGenerator 
from config import PATHS
import os
import random
from PIL import Image
import torch

app = Flask(__name__, static_folder='assets')

game_logic = GameLogic()
img_processor = ImageProcessor()

# ---------------------------------------------------------------------------
# 2. โหลด AI Model (ขั้นตอนนี้จะรันตอนเริ่ม Server)
# ---------------------------------------------------------------------------
print("⏳ กำลังโหลด AI Model (Kandinsky 2.2)... อาจใช้เวลา 1-3 นาที กรุณารอ...")
try:
    # พยายามโหลด AI ถ้าเครื่องแรงพอ
    ai_engine = AIGenerator()
    AI_ENABLED = True
    print("✅ AI Model Loaded! ระบบสร้างภาพพร้อมใช้งาน")
except Exception as e:
    # ถ้าโหลดไม่ผ่าน (เช่น แรมไม่พอ) จะสลับไปโหมดจำลองอัตโนมัติ
    print(f"❌ Error loading AI: {e}")
    print("⚠️ ระบบจะทำงานในโหมดจำลอง (Simulation Mode - ไม่สร้างภาพจริง)")
    AI_ENABLED = False
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# เพิ่มบรรทัดนี้เข้าไปแทนครับ
# ---------------------------------------------------------------------------
# print("⚠️ AI Disabled: Running in UI Layout Mode")
# AI_ENABLED = False

@app.route('/check_gpu_status')
def check_gpu_status():
    has_gpu = torch.cuda.is_available()
    return jsonify({'has_gpu': has_gpu})

@app.route('/switch_device', methods=['POST'])
def switch_device():
    if not AI_ENABLED:
        return jsonify({'status': 'error', 'message': 'AI is disabled (Mock Mode).'})

    mode = request.form.get('mode') # รับค่า 'gpu' หรือ 'cpu'
    target = 'cuda' if mode == 'gpu' else 'cpu'
    
    # เรียกฟังก์ชันใน ai_generator
    success, message = ai_engine.switch_device(target)
    
    if success:
        return jsonify({'status': 'success', 'message': message})
    else:
        return jsonify({'status': 'error', 'message': message})


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/open_card_pack', methods=['POST'])
def open_card_pack():
    card_pack = request.form.get('card_pack')
    final_pack = game_logic.random_card_pack(card_pack)
    return jsonify({
        'card_pack': final_pack,
        'card_type': final_pack, 
        'card_power': '?'
    })

@app.route('/cards/<path:filename>') 
def get_card_image(filename):
    return send_from_directory(PATHS['output_folder'], filename)

@app.route('/get_classes')
def get_classes():
    # เพิ่ม Class ใหม่ต่อท้ายเข้าไป
    return jsonify({'classes': ['Swordman', 'Mage', 'Hunter', 'Necromancer', 'Demon Lord', 'Abomination']})

@app.route('/get_weapons/<selected_class>')
def get_weapons(selected_class):
    weapons = {
        # --- ของเดิม ---
        'Swordman': ['Sword', 'Shield', 'Greatsword','Vanguard Saber','Stormcutte','Wooden Buckler','Aegis of Valor','Tower Shield of the Sentinel','Heavy Claymore','Titans Cleaver','Grand Cross',], 
        'Mage': ['Staff', 'Orb', 'Grimoire', 'Apprentice Staff', 'Mystic Oak Staff', 'Crystal Scepter', 'Mana Sphere', 'Void Essence', 'Celestial Globe', 'Worn Notebook', 'Forbidden Scriptures', 'Chronicle of the Archmage'], 
        'Hunter': ['Bow', 'Dagger', 'Crossbow', 'Reinforced Longbow', 'Windforce', 'Eagle Eye', 'Shadow Dagger', 'Venom Fang', 'Kris', 'Heavy Crossbow', 'Repeating Crossbow', 'Demon Hunter'],

        # --- ของใหม่ (สายดาร์ก/ปีศาจ) ---
        
        # Necromancer: สายเวทย์มืด ปลุกศพ
        'Necromancer': [
            'Bone Scythe',          # เคียวกระดูก
            'Skull Lantern',        # โคมหัวกะโหลก
            'Cursed Bell',          # กระดิ่งต้องสาป
            'Spine Whip',           # แส้กระดูกสันหลัง
            'Rusty Gravedigger Shovel', # พลั่วขุดสุสานสนิมเขรอะ
            'Book of the Dead',     # คัมภีร์มรณะ
            'Soul Jar',             # ไหดักวิญญาณ
            'Ribcage Shield'        # โล่ซี่โครง
        ],

        # Demon Lord: สายจอมมาร นรกแตก
        'Demon Lord': [
            'Infernal Trident',     # สามง่ามนรก
            'Hellfire Greatsword',  # ดาบใหญ่ไฟโลกันตร์
            'Demonic Horns',        # เขาปีศาจ (ใช้อาวุธร่างกาย)
            'Blood Chalice',        # จอกเลือด
            'Chains of Tartarus',   # โซ่นรก
            'Obsidian Claws',       # กรงเล็บหินอัคนี
            'Soul Eater Blade',     # ดาบกลืนวิญญาณ
            'Dark Matter Core'      # แก่นสสารมืด
        ],

        # Abomination: สายตัวประหลาด กลายพันธุ์
        'Abomination': [
            'Flesh Hook',           # ตะขอเกี่ยวเนื้อ
            'Mutated Tentacle',     # หนวดกลายพันธุ์
            'Acid Spit Gland',      # ต่อมพ่นกรด
            'Rusted Saw Blade',     # ใบเลื่อยสนิม
            'Extra Limbs',          # แขนขาที่งอกเกินมา
            'Living Parasite',      # ปรสิตมีชีวิต
            'Broken Manacles',      # ตรวนที่ขาด (หลุดจากการคุมขัง)
            'Jawbone Club'          # กระบองกรามยักษ์
        ]
    }
    return jsonify({'weapons': weapons.get(selected_class, [])})

# แก้ไขเฉพาะฟังก์ชัน confirm_selection ใน app.py

@app.route('/confirm_selection', methods=['POST'])
def confirm_selection():
    data = request.form
    
    # 1. Logic
    card_pack = game_logic.random_card_pack(data.get('card_pack'))
    raw_animal = game_logic.get_random_animal()
    selected_class = data.get('selected_class')
    selected_weapon = data.get('selected_weapon')
    
    unique_name = game_logic.generate_unique_name(raw_animal, selected_class)
    
    # [สูตรโกง] บังคับ Power 100 (ถ้าอยากเลิกโกง ให้ลบบรรทัดนี้ทิ้ง)
    # -------------------------------------------------------------------
    stats, primary, secondary = game_logic.generate_stats(card_pack)
    # primary = (primary[0], 100) 
    # -------------------------------------------------------------------

    card_id = random.randint(1000, 9999)

    # ส่งค่า 100 ไปให้ generate_ability_desc
    ability_desc = game_logic.generate_ability_desc(primary[0], card_pack, primary[1])
    
    # 2. AI Generation (อัปเกรดความชัด)
    if AI_ENABLED:
        print(f"🎨 AI กำลังวาดรูป: {unique_name}...")
        
        # ------------------------------------------------------------------
        # [จุดที่แก้] เปลี่ยนชื่อตัวแปรให้ตรงกับ game_logic.py
        # job_class -> card_class
        # element1 -> element
        # element2 -> ลบออก (เพราะ function ไม่ได้รับค่านี้แล้ว)
        # ------------------------------------------------------------------
        prompt = game_logic.create_prompt(
            animal=raw_animal, 
            card_class=selected_class, # แก้ชื่อตรงนี้
            weapon=selected_weapon,
            element=primary[0],        # แก้ชื่อตรงนี้
            card_type=card_pack
        )
        
        # --- [วิธีที่ 1] Negative Prompt ชุดใหญ่ไฟกระพริบ ---
        # ดักทางเรื่องมือเบี้ยว นิ้วเกิน และอาวุธจม
        negative_prompt = (
    # --- 1. ห้ามการ์ตูน / 3D / งานวาด (Style Blocking) ---
    "cartoon, anime, 3d render, cgi, 3d model, plastic, glossy, low poly, "
    "drawing, painting, illustration, sketch, doodle, cel shaded, vector art, "
    "graphite, crayon, pastel, watercolor, ink, oil painting, "
    "unreal engine, octane render, "

    # --- 2. ห้ามมนุษย์ (No Humans Strict) ---
    "human, human face, man, woman, girl, boy, humanoid, people, crowd, "
    "skin, hair, body parts, silhouette, "

    # --- 3. ห้ามกายวิภาคผิดเพี้ยน (Bad Anatomy & Glitches) ---
    "bad anatomy, deformed, mutated, disfigured, mutation, "
    "mutated hands, poorly drawn hands, extra fingers, missing fingers, "
    "fused fingers, too many fingers, claw, "
    "extra limbs, malformed limbs, missing arms, missing legs, "
    "fused limbs, disconnected limbs, long neck, "
    
    # --- 4. ห้ามอาวุธ/วัตถุบั๊ก (Object Glitches) ---
    "weapon fused with hand, weapon fused with body, floating weapon, "
    "disappearing weapon, blurry weapon, "

    # --- 5. ห้ามคุณภาพต่ำ / เบลอ / สิ่งรบกวน (Quality & Artifacts) ---
    "text, watermark, signature, username, error, logo, "
    "blur, blurry, bokeh, depth of field, motion blur, "
    "low quality, worst quality, normal quality, lowres, "
    "jpeg artifacts, compression artifacts, pixelated, noise, grain, "
    "cropped, out of frame, cut off, worst composition"
)
        
        # --- [วิธีที่ 2] เพิ่มรอบการวาด (num_inference_steps) ---
        # ปกติ 25 รอบ -> เพิ่มเป็น 30 รอบ (ชัดขึ้น แต่รอนานขึ้นนิดนึง)
        # ** ถ้ามัน Error ว่าไม่รู้จัก num_inference_steps ให้ลบบรรทัดนี้ออกนะครับ **
        generated_img = ai_engine.generate_image(
            prompt=prompt, 
            negative_prompt=negative_prompt, 
            seed=random.randint(0, 100000),
            num_inference_steps=30 
        )
    else:
        print("⚠️ ใช้รูปจำลอง (Mock Image)")
        generated_img = Image.new("RGB", (490, 585), (80, 80, 100))

    # 3. ประกอบการ์ด
    info_text = (f"Ability: {ability_desc}\n"
                 f"Power: {primary[0]} {primary[1]}")
    
    icon_path = PATHS['element_icons'].get(primary[0])

    filename = img_processor.compose_card(
        generated_img, card_pack, card_id, 
        unique_name, "", primary[1], 
        info_text, icon_path, PATHS['output_folder']
    )
    
    return jsonify({
        'status': 'success',
        'card_pack': card_pack,
        'card_power': primary[1],
        'card_url': f"/cards/{filename}"
    })

if __name__ == '__main__':
    if not os.path.exists(PATHS['output_folder']):
        os.makedirs(PATHS['output_folder'])
    
    # เติม use_reloader=False เพื่อห้ามมันรีสตาร์ทเอง
    app.run(debug=True, use_reloader=False, port=5000)