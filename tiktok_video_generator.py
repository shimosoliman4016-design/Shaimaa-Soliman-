import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

class TikTokVideoGenerator:
    def __init__(self, width=1080, height=1920, fps=30, duration=10):
        self.width = width
        self.height = height
        self.fps = fps
        self.duration = duration
        self.total_frames = fps * duration
        self.font_size = 100
        
    def create_dark_background_with_glow(self, frame_num):
        """Create dark background with neon purple glow"""
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Add neon purple glow effect
        center = (self.width // 2, self.height // 2)
        glow_intensity = int(100 * (1 + 0.3 * np.sin(frame_num * 0.05)))
        
        # Create gradient glow
        for i in range(self.width):
            for j in range(self.height):
                dist = np.sqrt((i - center[0])**2 + (j - center[1])**2)
                if dist < 800:
                    glow = int(glow_intensity * np.exp(-dist / 400))
                    frame[j, i, 2] = min(255, glow)  # Red channel for purple
                    frame[j, i, 0] = min(255, glow // 2)  # Blue channel
        
        return frame
    
    def add_arabic_text_with_blink(self, frame, frame_num):
        """Add Arabic text with blinking effect"""
        # Convert to PIL for text rendering
        pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_frame)
        
        # Blinking effect - on/off every 10 frames
        blink = (frame_num % 20) < 10
        
        if blink:
            text = "مُحَمَّدٌ مُتَمَيِّزٌ فِي المُسَابَقَةِ"
            
            # Try to use Arabic font, fallback to default
            try:
                font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansArabic-Regular.ttf", self.font_size)
            except:
                font = ImageFont.load_default()
            
            # Get text bounding box for centering
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (self.width - text_width) // 2
            y = (self.height - text_height) // 2 - 200
            
            # Draw text with neon purple color
            draw.text((x, y), text, font=font, fill=(255, 0, 255))
        
        # Convert back to OpenCV format
        frame = cv2.cvtColor(np.array(pil_frame), cv2.COLOR_RGB2BGR)
        return frame
    
    def apply_zoom_effect(self, frame, frame_num):
        """Apply slow zoom in and out effect"""
        zoom_factor = 1.0 + 0.2 * np.sin(frame_num * 0.08)
        h, w = frame.shape[:2]
        
        # Calculate new dimensions
        new_w = int(w * zoom_factor)
        new_h = int(h * zoom_factor)
        
        # Resize with zoom
        resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # Crop back to original size
        y_start = (new_h - h) // 2
        x_start = (new_w - w) // 2
        
        if y_start >= 0 and x_start >= 0 and y_start + h <= new_h and x_start + w <= new_w:
            cropped = resized[y_start:y_start+h, x_start:x_start+w]
            return cropped
        
        return frame
    
    def add_moving_circle_pointer(self, frame, frame_num):
        """Add moving circle pointer over text"""
        center_x = self.width // 2
        center_y = self.height // 2 - 200
        
        # Circle moves in a circular pattern
        angle = (frame_num * 6) % 360
        radius = 150
        
        x = int(center_x + radius * np.cos(np.radians(angle)))
        y = int(center_y + radius * np.sin(np.radians(angle)))
        
        # Draw circle with glow effect
        cv2.circle(frame, (x, y), 30, (0, 255, 255), 3)  # Cyan circle
        cv2.circle(frame, (x, y), 50, (0, 100, 100), 1)  # Outer glow
        
        return frame
    
    def apply_shake_effect(self, frame, frame_num):
        """Apply subtle shake effect"""
        shake_amount = int(5 * np.sin(frame_num * 0.15))
        
        h, w = frame.shape[:2]
        tx = shake_amount
        ty = int(3 * np.sin(frame_num * 0.1))
        
        M = np.float32([[1, 0, tx], [0, 1, ty]])
        shaken = cv2.warpAffine(frame, M, (w, h))
        
        return shaken
    
    def add_countdown(self, frame, frame_num):
        """Add countdown 3..2..1"""
        pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_frame)
        
        # Countdown in first 3 seconds (90 frames)
        if frame_num < 90:
            remaining_frames = 90 - frame_num
            countdown = (remaining_frames // 30) + 1
            
            if countdown > 0:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/opentype/dejavu/DejaVuSans-Bold.ttf", 200)
                except:
                    font = ImageFont.load_default()
                
                # Get text bounding box
                bbox = draw.textbbox((0, 0), str(countdown), font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (self.width - text_width) // 2
                y = (self.height - text_height) // 2 + 400
                
                # Draw with pulsing effect
                alpha = int(255 * (1 + 0.5 * np.sin(frame_num * 0.2)))
                draw.text((x, y), str(countdown), font=font, fill=(255, 0, 255))
        
        frame = cv2.cvtColor(np.array(pil_frame), cv2.COLOR_RGB2BGR)
        return frame
    
    def add_end_screen(self, frame, frame_num):
        """Add end screen with call to action"""
        # Show end screen in last 2 seconds
        if frame_num > self.total_frames - 60:
            pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_frame)
            
            text = "اكتب العدد في التعليقات 👇"
            
            try:
                font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansArabic-Regular.ttf", 80)
            except:
                font = ImageFont.load_default()
            
            # Get text bounding box
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (self.width - text_width) // 2
            y = self.height - 300
            
            draw.text((x, y), text, font=font, fill=(0, 255, 255))
            
            frame = cv2.cvtColor(np.array(pil_frame), cv2.COLOR_RGB2BGR)
        
        return frame
    
    def generate_video(self, output_path="tiktok_video.mp4"):
        """Generate the complete video"""        
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (self.width, self.height))
        
        print(f"🎬 Generating video: {output_path}")
        print(f"📊 Resolution: {self.width}x{self.height} | Duration: {self.duration}s | FPS: {self.fps}")
        
        for frame_num in range(self.total_frames):
            # Create frame
            frame = self.create_dark_background_with_glow(frame_num)
            frame = self.apply_zoom_effect(frame, frame_num)
            frame = self.add_arabic_text_with_blink(frame, frame_num)
            frame = self.add_moving_circle_pointer(frame, frame_num)
            frame = self.apply_shake_effect(frame, frame_num)
            frame = self.add_countdown(frame, frame_num)
            frame = self.add_end_screen(frame, frame_num)
            
            # Write frame
            out.write(frame)
            
            # Progress
            progress = (frame_num + 1) / self.total_frames * 100
            print(f"Progress: {progress:.1f}% [{frame_num + 1}/{self.total_frames}]", end='\r')
        
        out.release()
        print(f"\n✅ Video saved: {output_path}")
        return output_path

# Main execution
if __name__ == "__main__":
    print("🎥 TikTok Video Generator - Arabic with Effects")
    print("=" * 50)
    
    # Create generator
    generator = TikTokVideoGenerator(width=1080, height=1920, fps=30, duration=10)
    
    # Generate video
    output_video = generator.generate_video("tiktok_video_final.mp4")
    
    print("\n✨ Video generation complete!")
    print(f"📁 Output file: {output_video}")