import json
import os

from PIL import Image, ImageDraw, ImageFont

# size of the output image in pixels
output_size_x = 1280

extra_scale_y = 1.0

# in world units
margin_top = 8
margin_bottom = 8
margin_left = 8
margin_right = 8

star_radius = 4
imagemap_radius = 8

fontsize = 9
fontfile = 'tahoma.ttf'

font = ImageFont.truetype(fontfile, fontsize)

faction_colors = {
    'AuriganDirectorate' : (63, 191, 63),
    'Davion' : (255, 191, 63),
    'Liao' : (191, 255, 63),
    'Locals' : (191, 191, 191),
    'MagistracyOfCanopus' : (63, 255, 191),
    'Marik' : (127, 63, 255),
    'NoFaction' : (127, 127, 127),
    'TaurianConcordat' : (191, 63, 63),
    }

text_offsets = {
    'starsystemdef_Carmichael' : (6, -12),
    'starsystemdef_CluffsStand' : (6, 4), 
    'starsystemdef_FlannagansNebulea' : (-40, 6),
    'starsystemdef_JansensHold' : (-24, 6),
    'starsystemdef_Hellespont' : (-48, -4),
    'starsystemdef_Ishtar' : (-28, -12),
    'starsystemdef_MacLeodsLand' : (-68, -4),
    'starsystemdef_Pinard' : (-32, -4),
    'starsystemdef_Smithon' : (6, -12),
    }

data_path = (
    'C:/Program Files (x86)/Steam/steamapps/common/' +
    'BATTLETECH/BattleTech_Data/StreamingAssets/data'
    )

starsystem_path = os.path.join(data_path, 'starsystem')

datas = []

for filename in os.listdir(starsystem_path):
    path = os.path.join(starsystem_path, filename)
    f = open(path)
    datas.append(json.load(f))
    f.close()

min_x = min(data["Position"]["x"] for data in datas) - margin_left
max_x = max(data["Position"]["x"] for data in datas) + margin_right
min_y = min(data["Position"]["y"] for data in datas) - margin_bottom
max_y = max(data["Position"]["y"] for data in datas) + margin_top

size_x = max_x - min_x
size_y = max_y - min_y

scale = output_size_x / size_x

output_size_y = int(round(scale * size_y * extra_scale_y))

political_image = Image.new('RGB', (output_size_x, output_size_y))
political_draw = ImageDraw.Draw(political_image)

shop_image = Image.new('RGB', (output_size_x, output_size_y))
shop_draw = ImageDraw.Draw(shop_image)

difficulty_image = Image.new('RGB', (output_size_x, output_size_y))
difficulty_draw = ImageDraw.Draw(difficulty_image)

result_imagemap = '<imagemap>\n'
result_imagemap += 'Image:Starsystem.png|frame' # add other image stuff here
result_imagemap += '|Click on a system to visit the corresponding article.\n\n'

def to_output_coords(x, y):
    output_x = (x - min_x) * scale
    output_y = (max_y - y) * scale
    return output_x, output_y

for data in datas:
    if "AlternateSystem" in data and data["AlternateSystem"]: continue
    
    x, y = to_output_coords(data["Position"]["x"], data["Position"]["y"])

    political_color = faction_colors[data["Owner"]]

    

    tags = data["Tags"]["items"]

    if 'planet_other_empty' in tags:
        shop_color = (31, 31, 31)
    elif 'planet_industry_manufacturing' not in tags:
        shop_color = (63, 63, 63)
    elif 'planet_industry_rich' not in tags:
        shop_color = (63, 127, 63)
    elif 'planet_industry_research' not in tags:
        shop_color = (63, 63, 255)
    elif 'planet_other_starleague' not in tags:
        shop_color = (255, 63, 255)
    else:
        shop_color = (255, 255, 0)
        
    shop_color = tuple(shop_color)

    difficulty = data["Difficulty"]
    if difficulty == 0:
        difficulty_color = (127, 127, 127)
    elif difficulty > 0:
        difficulty_color = (127 + difficulty * 42, 127 - difficulty * 42, 127 - difficulty * 42)
    elif difficulty < 0:
        difficulty_color = (127 + difficulty * 42, 127 + difficulty * 42, 127 - difficulty * 42)

    name = data["Description"]["Name"]
    
    political_draw.ellipse([
        x - star_radius,
        y - star_radius,
        x + star_radius,
        y + star_radius], fill=political_color)

    shop_draw.ellipse([
        x - star_radius,
        y - star_radius,
        x + star_radius,
        y + star_radius], fill=shop_color)

    difficulty_draw.ellipse([
        x - star_radius,
        y - star_radius,
        x + star_radius,
        y + star_radius], fill=difficulty_color)

    if 'planet_other_starleague' in tags:
        shop_draw.text((x - 2, y - 5), 'L', font=font, fill=(0,0,0))

    system_id = data["Description"]["Id"]
    if system_id in text_offsets:
        offset_x, offset_y = text_offsets[system_id]
        text_x = x + offset_x
        text_y = y + offset_y
    else:
        text_x = x + 1.5 * star_radius
        text_y = y - 0.5 * fontsize

    political_draw.text((text_x, text_y), name, font=font, fill=political_color)
    shop_draw.text((text_x, text_y), name, font=font, fill=shop_color)
    difficulty_draw.text((text_x, text_y), name, font=font, fill=difficulty_color)

    result_imagemap += 'circle %d %d %d [[%s]]\n' % (x, y, imagemap_radius, name)

political_image.save('starsystem.png')
shop_image.save('starsystem_shops.png')
difficulty_image.save('starsystem_difficulty.png')

result_imagemap += '</imagemap><br clear=all />\n'

f = open('starsystem.txt', 'w')
f.write(result_imagemap)
f.close()
