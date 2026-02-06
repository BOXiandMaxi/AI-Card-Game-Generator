import torch
from diffusers import KandinskyV22Pipeline, KandinskyV22PriorPipeline
from transformers import CLIPVisionModelWithProjection
from diffusers.models import UNet2DConditionModel
from config import DEVICE

class AIGenerator:
    def __init__(self):
        # เก็บค่า Device ปัจจุบันไว้ใช้งาน
        self.device = DEVICE 
        print(f"Loading AI Models on {self.device}... This may take a while.")
        
        # ... (โค้ด __init__ เดิมของคุณ คงไว้เหมือนเดิม) ...
        # ... (ช่วงโหลด Model ของเดิม) ...
        
        # ถ้าใช้ CPU ห้ามใช้ .half() ต้องใช้แบบปกติ (float32)
        if self.device == 'cpu':
            # ... (โค้ดเดิม) ...
            self.image_encoder = CLIPVisionModelWithProjection.from_pretrained('kandinsky-community/kandinsky-2-2-prior', subfolder='image_encoder').to(self.device)
            self.unet = UNet2DConditionModel.from_pretrained('kandinsky-community/kandinsky-2-2-decoder', subfolder='unet').to(self.device)
            self.prior = KandinskyV22PriorPipeline.from_pretrained('kandinsky-community/kandinsky-2-2-prior', image_encoder=self.image_encoder, torch_dtype=torch.float32).to(self.device)
            self.decoder = KandinskyV22Pipeline.from_pretrained('kandinsky-community/kandinsky-2-2-decoder', unet=self.unet, torch_dtype=torch.float32).to(self.device)
        else:
            # ... (โค้ดเดิม) ...
            self.image_encoder = CLIPVisionModelWithProjection.from_pretrained('kandinsky-community/kandinsky-2-2-prior', subfolder='image_encoder').half().to(self.device)
            self.unet = UNet2DConditionModel.from_pretrained('kandinsky-community/kandinsky-2-2-decoder', subfolder='unet').half().to(self.device)
            self.prior = KandinskyV22PriorPipeline.from_pretrained('kandinsky-community/kandinsky-2-2-prior', image_encoder=self.image_encoder, torch_dtype=torch.float16).to(self.device)
            self.decoder = KandinskyV22Pipeline.from_pretrained('kandinsky-community/kandinsky-2-2-decoder', unet=self.unet, torch_dtype=torch.float16).to(self.device)

        print("AI Models Loaded Successfully.")

    # ------------------------------------------------------------------
    # [NEW] ฟังก์ชันสลับ CPU <-> GPU
    # ------------------------------------------------------------------
    def switch_device(self, target_device):
        if target_device == self.device:
            return True, f"Already on {target_device}"

        try:
            # กรณีจะย้ายไป GPU
            if target_device == 'cuda':
                if not torch.cuda.is_available():
                    return False, "No NVIDIA GPU found on this machine."
                
                print("🚀 Switching AI to GPU (CUDA)...")
                # GPU ใช้ float16 เพื่อความเร็วและประหยัด VRAM
                self.prior.to("cuda", torch.float16)
                self.decoder.to("cuda", torch.float16)
                self.device = 'cuda'
                return True, "Switched to GPU (High Performance)"

            # กรณีจะย้ายกลับ CPU
            elif target_device == 'cpu':
                print("🐢 Switching AI to CPU...")
                # CPU ต้องกลับมาใช้ float32
                self.prior.to("cpu", torch.float32)
                self.decoder.to("cpu", torch.float32)
                self.device = 'cpu'
                return True, "Switched to CPU (Low Performance)"
                
        except Exception as e:
            print(f"❌ Switch failed: {e}")
            return False, str(e)

    # ... (ฟังก์ชัน generate_image เดิมของคุณ) ...
    def generate_image(self, prompt, negative_prompt, seed, num_inference_steps=25):
        # ... (โค้ดเดิม) ...
        # แก้ไขบรรทัด generator ให้ใช้ self.device แทน DEVICE จาก config
        generator = torch.Generator(device=self.device).manual_seed(int(seed))
        
        # ... (ส่วนที่เหลือเหมือนเดิม) ...
        img_emb = self.prior(prompt=prompt, num_inference_steps=num_inference_steps, generator=generator)
        negative_emb = self.prior(prompt=negative_prompt, num_inference_steps=num_inference_steps, num_images_per_prompt=1, generator=generator)
        images = self.decoder(image_embeds=img_emb.image_embeds, negative_image_embeds=negative_emb.image_embeds, num_inference_steps=num_inference_steps, height=512, width=512, generator=generator)
        
        return images.images[0]