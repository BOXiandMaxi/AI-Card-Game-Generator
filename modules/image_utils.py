# ------------------------------------------------------------------
# เพิ่ม 2 บรรทัดนี้ ไว้บนสุดของไฟล์เลยครับ (สำคัญมาก!)
# ------------------------------------------------------------------
import matplotlib
matplotlib.use('Agg') # สั่งให้ทำงานเบื้องหลัง ห้ามเปิดหน้าต่าง GUI
# ------------------------------------------------------------------

from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from config import PATHS
import os

class ImageProcessor:
    def create_text_image(self, text, filename, output_dir, fontsize=54, font_path=None, ha='center'):
        plt.style.use('fivethirtyeight')
        if font_path and os.path.exists(font_path):
            custom_font = FontProperties(fname=font_path)
        else:
            custom_font = None

        # --- จัดขนาดกรอบรูปตามประเภทข้อความ ---
        if 'info' in filename:
            figsize = (5, 2)
            should_wrap = True
        elif 'name' in filename:
            figsize = (12, 1.5) 
            should_wrap = False 
        elif 'stat' in filename:
            # [แก้] ใช้กรอบสี่เหลี่ยมจัตุรัสเล็กๆ สำหรับตัวเลข
            figsize = (2, 2)
            should_wrap = False
        else:
            figsize = (2, 2) 
            should_wrap = False

        fig, ax = plt.subplots(figsize=figsize)
        
        x_pos = 0.05 if ha == 'left' else 0.5
        
        ax.text(x_pos, 0.5, f"{text}", ha=ha, va='center', fontsize=fontsize, 
                color='white', alpha=1, fontproperties=custom_font, wrap=should_wrap)
        
        ax.axis('off')
        
        temp_path = os.path.join(output_dir, filename)
        
        # [แก้] เพิ่ม bbox_inches='tight' ตัดขอบขาวทิ้งให้หมด ตัวเลขจะได้ไม่ลอย
        plt.savefig(temp_path, dpi=300, format='png', facecolor='none', bbox_inches='tight', pad_inches=0.05)
        
        plt.close('all') 
        
        return Image.open(temp_path)

    def compose_card(self, generated_img, card_type, card_id, animal_name, job_class, stats_num, info_text, element_icon_path, output_folder):
        safe_name = "".join([c for c in animal_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        folder_name = safe_name.replace(" ", "_")
        target_dir = os.path.join(output_folder, folder_name)
        
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        frame_key = f'frame_{card_type}'
        frame_path = PATHS.get(frame_key, PATHS['frame_bronze'])
        if not os.path.exists(frame_path):
            return None
        # กรอบขนาด 530x639
        card_frame = Image.open(frame_path).resize((530, 639))
        
        # รูปขนาด 490x450 (ไซส์ที่เราตกลงกันว่าสวย)
        img = generated_img.resize((490, 450))
            
        # [แก้] ปรับขนาดรูปตัวเลขให้ใหญ่ขึ้นนิดนึง
        bar_img = self.create_text_image(
            stats_num, f"stat_{card_id}.png", target_dir, 60, PATHS['font_bold']
        ).resize((90, 80))
        
        name_img_raw = self.create_text_image(
            f"{animal_name}", f"name_{card_id}.png", target_dir, 54, PATHS['font_name']
        )
        aspect_ratio = name_img_raw.width / name_img_raw.height
        new_height = 40
        new_width = int(new_height * aspect_ratio)
        
        if new_width > 370:
            new_width = 370 
            
        name_img = name_img_raw.resize((new_width, new_height))
        name_x_offset = 125 + (370 - new_width) // 2

        info_img = self.create_text_image(
            info_text, f"info_{card_id}.png", target_dir, 15, PATHS['font_info'], ha='left'
        ).resize((330, 110))

        combined = Image.new("RGBA", (530, 639), (0, 0, 0, 0))
        
        # วางรูปที่ตำแหน่ง Y=80 (หลบป้ายชื่อ)
        combined.paste(img, (20, 80))

        combined.paste(card_frame, (0, 0), card_frame)
        
        if element_icon_path and os.path.exists(element_icon_path):
            icon = Image.open(element_icon_path)
            target_size = (530, 639)  # <--- *** แก้ตัวเลขตรงนี้ให้ตรงกับรูปเดิมของคุณ ***
            icon = icon.resize(target_size)
            combined.paste(icon, (0, 0), icon)

        # [แก้] ขยับตำแหน่งตัวเลขพลังมาซ้ายนิดนึง (380, 515) กันตกขอบ
        combined.paste(bar_img, (384, 515), bar_img)
        
        combined.paste(name_img, (name_x_offset, 35), name_img)
        combined.paste(info_img, (25, 500), info_img)

        filename = f"card{card_id}.png"
        save_path = os.path.join(target_dir, filename)
        combined.save(save_path)
        
        return f"{folder_name}/{filename}"