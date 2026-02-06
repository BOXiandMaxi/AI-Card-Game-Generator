import os

# บรรทัดนี้จะหาตำแหน่งปัจจุบันของไฟล์ config.py ให้เองอัตโนมัติ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ชี้ไปที่โฟลเดอร์ assets ที่เราเพิ่งสร้าง
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

PATHS = {
    'credential_json': os.path.join(ASSETS_DIR, 'web_file', 'read_gsheet.json'),
    
    'frame_bronze': os.path.join(ASSETS_DIR, 'frame_card', 'frame', 'frame_bronze.png'),
    'frame_silver': os.path.join(ASSETS_DIR, 'frame_card', 'frame', 'frame_silver.png'),
    'frame_gold': os.path.join(ASSETS_DIR, 'frame_card', 'frame', 'frame_gold.png'),
    'frame_diamond': os.path.join(ASSETS_DIR, 'frame_card', 'frame', 'frame_ssr.png'),
    
    'font_bold': os.path.join(ASSETS_DIR, 'frame_card', 'font', 'Taviraj', 'Taviraj-Bold.ttf'),
    'font_name': os.path.join(ASSETS_DIR, 'frame_card', 'font', 'wide latin', 'LATINWD.TTF'),
    'font_info': os.path.join(ASSETS_DIR, 'frame_card', 'font', 'kanit', 'Kanit-Regular.ttf'),
    
    'output_folder': os.path.join(ASSETS_DIR, 'output_cards'),
    
    'element_icons': {
        'Fire': os.path.join(ASSETS_DIR, 'frame_card', 'element_icon', 'icon_element_fire.png'),
        'Water': os.path.join(ASSETS_DIR, 'frame_card', 'element_icon', 'icon_element_water.png'),
        'Wind': os.path.join(ASSETS_DIR, 'frame_card', 'element_icon', 'icon_element_wind.png'),
        'Earth': os.path.join(ASSETS_DIR, 'frame_card', 'element_icon', 'icon_element_earth.png'),
        
        # [เพิ่ม] ธาตุแสงและมืด (ต้องเอารูปไปวางใน assets/frame_card/element_icon/ ด้วยนะครับ)
        'Light': os.path.join(ASSETS_DIR, 'frame_card', 'element_icon', 'icon_element_light.png'),
        'Dark': os.path.join(ASSETS_DIR, 'frame_card', 'element_icon', 'icon_element_dark.png')
    }
}

# *** แก้บรรทัดนี้ครับ ***
DEVICE = 'cpu'