from font_source_sans_pro import SourceSansProSemibold
from PIL import Image, ImageFont, ImageDraw
from inky import InkyWHAT
import scraper
import random
import os
# font_source_sans_pro==0.0.1
# inky==2.2.1
# Pillow==12.0.0
root = os.path.dirname(os.path.realpath("what_explosm.py"))

# choose a random comic out of the dir comic
def choose_random_comic():
    # get all images in the folder
    comics = os.listdir('comics')
    # choose a random image
    comic = comics[random.randint(0, len(comics) - 1)]
    print('chose comic: ' + comic)
    return Image.open(os.path.join(root, 'comics', comic))

if __name__ == '__main__':

    xkdc_scraper.get_current_comic()
    comic_image = choose_random_comic()

    inky_display = InkyWHAT("black")
    inky_display.set_border(inky_display.WHITE)
    img = comic_image

    w, h = img.size
    ptype = ''
    # determin if imgage is portrait or landscape
    ptype = 'landscape' if w > h else 'portrait'

    if ptype == 'landscape':
        w_new = 400
        h_new = int((float(h) / w) * w_new)
        h_cropped = 300
        img = img.resize((w_new, h_new), resample=Image.LANCZOS)

        img_ratio = w_new / h_new
        x0 = 0
        x1 = w_new
        y0 = int((h_new - h_cropped) / 2)
        y1 = int(y0 + h_cropped)

    else:
        h_new = 300
        w_new = int((float(w) / h) * h_new)
        w_cropped = 400
        img = img.resize((w_new, h_new), resample=Image.LANCZOS)

        x0 = int((w_new - w_cropped) / 2)
        x1 = int(x0 + w_cropped)
        y0 = 0
        y1 = h_new

    img = img.crop((x0, y0, x1, y1))
    pal_img = Image.new("P", (1, 1))
    pal_img.putpalette((255, 255, 255, 0, 0, 0, 255, 0, 0) + (0, 0, 0) * 252)

    img = img.convert("RGB").quantize(palette=pal_img)
    img = img.rotate(180)  # flip the image so it's right side up
    inky_display.set_image(img)
    inky_display.show()