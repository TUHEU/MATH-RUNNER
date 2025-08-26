from rembg import remove
from PIL import Image

input_path = 'Assets\Questions\High\\1.png'
output_path = 'output.png'

input_img = Image.open(input_path)
output_img = remove(input_img)
output_img.save(output_path)
