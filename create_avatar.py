
from PIL import Image, ImageDraw
import os

# 创建一个 200x200 的图像
image = Image.new('RGBA', (200, 200), (79, 70, 229, 255))
draw = ImageDraw.Draw(image)

# 绘制一个简单的卡通头像
# 脸部
draw.ellipse((50, 50, 150, 150), fill=(255, 255, 255, 255))

# 眼睛
draw.ellipse((70, 70, 85, 85), fill=(79, 70, 229, 255))
draw.ellipse((115, 70, 130, 85), fill=(79, 70, 229, 255))

# 嘴巴
draw.ellipse((85, 100, 115, 110), fill=(79, 70, 229, 255))

# 头发
draw.ellipse((50, 40, 150, 70), fill=(139, 69, 19, 255))

# 保存图像
avatar_path = '/workspace/app/static/images/teacher-avatar.png'
os.makedirs(os.path.dirname(avatar_path), exist_ok=True)
image.save(avatar_path, 'PNG')

print(f"头像已保存到: {avatar_path}")
