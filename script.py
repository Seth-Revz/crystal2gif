import numpy as np
import os
import shutil
import traceback
from PIL import Image, ImageOps
from resources.pokedex import name_to_dex, mirror_exclusions

def create_front_sprite(directory: str, margin=True, alpha=0):

    # Initialize arrays for our RGB tuples
    normal_rgb = []
    shiny_rgb = []

    # Open front image
    try:
        front_img = Image.open(f'sprites/{directory}/front.png')
    except FileNotFoundError:
        return

    # Get list of colors in front.png, includes black, white, transparent, and up to 2 more colors
    color_list = front_img.getcolors()
    for color in color_list:
        normal_rgb.append(color[1])

    # Get non black, white, transparent pixel colors
    normal_rgb = [rgb for rgb in normal_rgb if (rgb != (255, 255, 255, 0) and rgb != (255, 255, 255, 255) and rgb != (0, 0, 0, 255))]
    # then sort by 'brightness'
    normal_rgb.sort(key = lambda x: x[0] *0.2126 + x[1] * 0.7152 + x[2] * 0.0722, reverse=True)

    # Open shiny.pal, get the shiny rgb values, convert them from rgb555 to rgb888
    with open(f'sprites/{directory}/shiny.pal', 'r') as f:
        for line in f:
            line = line.strip()
            if 'RGB' in line:
                r = int(line.split(' ')[1].strip(',')) * 255 // 31
                g = int(line.split(' ')[2].strip(',')) * 255 // 31
                b = int(line.split(' ')[3].strip(',')) * 255 // 31
                shiny_rgb.append((r, g, b, 255))

    # Swap normal palette with shiny palette.
    pixel_data = np.array(front_img)
    pixel_data[(pixel_data == normal_rgb[0]).all(axis = -1)] = shiny_rgb[0]
    if len(normal_rgb) > 1:
        pixel_data[(pixel_data == normal_rgb[1]).all(axis = -1)] = shiny_rgb[1]
    front_img_shiny = Image.fromarray(pixel_data, mode='RGBA')

    # Create animation and save.
    img_frames, img_animation, img_frame_duration = get_animation(front_img, directory)
    img_shiny_frames, img_shiny_animation, img_shiny_frame_duration = get_animation(front_img_shiny, directory)

    # Margins are needed to align the sprites correctly in pokemmo
    if margin:
        margin_image_animation = []
        for frame in img_animation:
            w, h = frame.size
            center = (96 - w) // 2
            new_img = Image.new(frame.mode, (96, 96), (255,255,255,alpha))
            new_img.paste(frame, (center, 96-4-h)) 
            margin_image_animation.append(new_img)
        img_animation = margin_image_animation

        margin_image_shiny_animation = []
        for frame in img_shiny_animation:
            w, h = frame.size
            center = (96 - w) // 2
            new_shiny_img = Image.new(frame.mode, (96, 96), (255,255,255,alpha))
            new_shiny_img.paste(frame, (center, 96-4-h)) 
            margin_image_shiny_animation.append(new_shiny_img)
        img_shiny_animation = margin_image_shiny_animation

    # Save result to output folder
    img_animation[0].save(f'output/sprites/battlesprites/{name_to_dex[directory]}-front-n.gif', save_all=True, append_images=img_shiny_animation[1:], duration=img_frame_duration, disposal=2, loop=0)
    img_shiny_animation[0].save(f'output/sprites/battlesprites/{name_to_dex[directory]}-front-s.gif', save_all=True, append_images=img_shiny_animation[1:], duration=img_shiny_frame_duration, disposal=2, loop=0)    
    print(f'Created front battle sprites for {directory}')

def get_animation(image: Image, directory: str):

    # Initializing some stuff
    w, h = image.size
    frame_num = h//w
    frames = []
    animation = []
    frame_duration = []

    # Separate frames
    for i in range(0, frame_num):
        frames.append(image.crop((0,w*i,w,w*(i+1))))

    # Get frame durations
    for line in get_modified_asm(f'sprites/{directory}/anim.asm').splitlines():
        line = line.strip()
        if line == 'endanim':
            break

        arr = line.split(' ')
        animation.append(frames[int(arr[1].strip(','))])
        frame_duration.append(int(arr[2]) * 16)

    for line in get_modified_asm(f'sprites/{directory}/anim_idle.asm').splitlines():
        line = line.strip()
        if line == 'endanim':
            break

        arr = line.split(' ')
        animation.append(frames[int(arr[1].strip(','))])
        frame_duration.append(int(arr[2]) * 16)

    animation.append(frames[0])
    frame_duration.append(800)

    return frames, animation, frame_duration

def get_modified_asm(file_path: str) -> str:
    temp = ''
    modified_asm = ''
    repeat_amount = 0

    with open(file_path, 'r') as f:
        
        for line in f:
            if 'setrepeat' in line:
                repeat_amount = int(line.strip().split(' ')[1])
                
            if 'dorepeat' in line:
                modified_asm += temp * repeat_amount

            if 'frame' in line:
                if repeat_amount:
                    temp += line
                else:
                    modified_asm += line
            
            if 'endanim' in line:
                modified_asm += line
                break
        
    return modified_asm

def create_back_sprite(directory: str, margin=True, alpha=0):

    # Initialize arrays for our RGB tuples
    normal_rgb = []
    shiny_rgb = []

    # Open back image
    try:
        back_img = Image.open(f'sprites/{directory}/back.png')
    except FileNotFoundError:
        return

    # Get list of colors in the sprite, should be 4, including black and white.
    color_list = back_img.getcolors()
    for color in color_list:
        normal_rgb.append(color[1])

    # Get non black, white, transparent pixel colors
    normal_rgb = [rgb for rgb in normal_rgb if (rgb != (255, 255, 255, 0) and rgb != (255, 255, 255, 255) and rgb != (0, 0, 0, 255))]
    
    # Sometimes theres only one color in the back sprite. So we load the front sprite since shiny.pal has 2
    # Honestly while going through this, I dont even know if this is needed
    # ... I dont think its needed but im going to leave it here for now.
    # 
    # if len(normal_rgb) < 2:
    #     normal_rgb = []
    #     front_img = Image.open(f'sprites/{directory}/front.png')
    #     color_list = front_img.getcolors()
    #     for color in color_list:
    #         normal_rgb.append(color[1])
    #     normal_rgb = [rgb for rgb in normal_rgb if (rgb != (255, 255, 255, 0) and rgb != (255, 255, 255, 255) and rgb != (0, 0, 0, 255))]

    # then sort by 'brightness'
    normal_rgb.sort(key = lambda x: x[0] *0.2126 + x[1] * 0.7152 + x[2] * 0.0722, reverse=True)

    # Open shiny.pal, get the shiny rgb values, convert them from rgb555 to rgb888
    with open(f'sprites/{directory}/shiny.pal', 'r') as f:
        for line in f:
            line = line.strip()
            if 'RGB' in line:
                r = int(line.split(' ')[1].strip(',')) * 255 // 31
                g = int(line.split(' ')[2].strip(',')) * 255 // 31
                b = int(line.split(' ')[3].strip(',')) * 255 // 31
                a = 255
                shiny_rgb.append((r, g, b, a))

    # Swap normal palette with shiny palette.
    pixel_data = np.array(back_img)
    pixel_data[(pixel_data == normal_rgb[0]).all(axis = -1)] = shiny_rgb[0]
    if len(normal_rgb) > 1:
        pixel_data[(pixel_data == normal_rgb[1]).all(axis = -1)] = shiny_rgb[1]
    back_img_shiny = Image.fromarray(pixel_data, mode='RGBA')
    
    # Margins are needed to align the sprites correctly in pokemmo
    if margin:
        w, h = back_img.size
        center = (96 - w) // 2
        temp_img = Image.new(back_img.mode, (96, 96), (255,255,255,alpha))
        temp_img.paste(back_img, (center, 96 - 12 - h)) 
        back_img = temp_img

        w, h = back_img_shiny.size
        center = (96 - w) // 2
        temp_img = Image.new(back_img_shiny.mode, (96, 96), (255,255,255,alpha))
        temp_img.paste(back_img_shiny, (center, 96 - 12 - h))
        back_img_shiny = temp_img

    # Save result to output folder
    back_img.save(f'output/sprites/battlesprites/{name_to_dex[directory]}-back-n.gif')
    back_img_shiny.save(f'output/sprites/battlesprites/{name_to_dex[directory]}-back-s.gif')
    print(f'Created back battle sprites for {directory}')

def create_overworld_sprite(directory: str, mirror=True):                                                                                                                                                                                                                                                                                                                                                                                                                       
    files = [ f.name for f in os.scandir(f'./sprites/{directory}') if 'overworld' in f.name ]

    for file in files:
        if '-shiny' in file:
            modifier = '-b-s'
        else:
            modifier = '-b-n'

        modifier += get_form(directory)

        overword_img = Image.open(f'sprites/{directory}/{file}')

        w, h = overword_img.size

        frame_num = w//h
        frames = []
        for i in range(0, frame_num):
            frames.append(overword_img.crop((h*i, 0, h*(i+1), h)))

        left1 = frames[0]
        left2 = frames[1]
        right1 = ImageOps.mirror(frames[0])
        right2 = ImageOps.mirror(frames[1])
        up1 = frames[2]
        up2 = frames[3]
        up3 = frames[2]
        down1 = frames[4]
        down2 = frames[5]
        down3 = frames[4]

        if mirror:
            up3 = ImageOps.mirror(up1)

            up_bbox = up1.getbbox()
            if (up_bbox[2] - up_bbox[0]) % 2 != 0:
                up1_x = get_center_of_mass(up1)
                up2_x = get_center_of_mass(up2)
                up3_x = get_center_of_mass(up3)

                if up3_x - up2_x > .5:
                    up3 = Image.new("RGBA", (16,16))
                    up3.paste(ImageOps.mirror(up1), (-1, 0))

                if up3_x - up2_x < -.5:
                    up3 = Image.new("RGBA", (16,16))
                    up3.paste(ImageOps.mirror(up1), (1, 0))

                if up1_x - up2_x > .5:
                    up1 = Image.new("RGBA", (16,16))
                    up1.paste(ImageOps.mirror(up3), (-1, 0))

                if up1_x - up2_x < -.5:
                    up1 = Image.new("RGBA", (16,16))
                    up1.paste(ImageOps.mirror(up3), (1, 0))

            down3 = ImageOps.mirror(down1)

            down_bbox = down1.getbbox()
            if (down_bbox[2] - down_bbox[0]) % 2 != 0:
                down1_x = get_center_of_mass(down1)
                down2_x = get_center_of_mass(down2)
                down3_x = get_center_of_mass(down3)

                if down3_x - down2_x > .5:
                    down3 = Image.new("RGBA", (16,16))
                    down3.paste(ImageOps.mirror(down1), (-1, 0))
                
                if down3_x - down2_x < -.5:
                    down3 = Image.new("RGBA", (16,16))
                    down3.paste(ImageOps.mirror(down1), (1, 0))

                if down1_x - down2_x > .5:
                    down1 = Image.new("RGBA", (16,16))
                    down1.paste(ImageOps.mirror(down3), (-1, 0))

                if down1_x - down2_x < -.5:
                    down1 = Image.new("RGBA", (16,16))
                    down1.paste(ImageOps.mirror(down3), (1, 0))

        canvas = Image.new('RGBA', (128, 128), (255, 255, 255, 0))

        canvas.paste( down1, ((32 - down1.size[0]) // 2  +0, 32 - 2 - down1.size[1]) )
        canvas.paste( down2, ((32 - down2.size[0]) // 2 +32, 32 - 2 - down2.size[1]) )
        canvas.paste( down3, ((32 - down3.size[0]) // 2 +64, 32 - 2 - down3.size[1]) )
        canvas.paste( down2, ((32 - down2.size[0]) // 2 +96, 32 - 2 - down2.size[1]) )

        canvas.paste( left1, ((32 - left1.size[0]) // 2  +0, 32 - 2 - left1.size[1] +32) )
        canvas.paste( left2, ((32 - left2.size[0]) // 2 +32, 32 - 2 - left2.size[1] +32) )
        canvas.paste( left1, ((32 - left1.size[0]) // 2 +64, 32 - 2 - left1.size[1] +32) )
        canvas.paste( left2, ((32 - left2.size[0]) // 2 +96, 32 - 2 - left2.size[1] +32) )

        canvas.paste( right1, ((32 - right1.size[0]) // 2  +0, 32 - 2 - right1.size[1] +64) )
        canvas.paste( right2, ((32 - right2.size[0]) // 2 +32, 32 - 2 - right2.size[1] +64) )
        canvas.paste( right1, ((32 - right1.size[0]) // 2 +64, 32 - 2 - right1.size[1] +64) )
        canvas.paste( right2, ((32 - right2.size[0]) // 2 +96, 32 - 2 - right2.size[1] +64) )

        canvas.paste( up1, ((32 - up1.size[0]) // 2  +0, 32 - 2 - up1.size[1] +96) )
        canvas.paste( up2, ((32 - up2.size[0]) // 2 +32, 32 - 2 - up2.size[1] +96) )
        canvas.paste( up3, ((32 - up3.size[0]) // 2 +64, 32 - 2 - up3.size[1] +96) )
        canvas.paste( up2, ((32 - up2.size[0]) // 2 +96, 32 - 2 - up2.size[1] +96) )

        if '-b-s' in modifier:
            canvas = add_sparkles(canvas)
        
        dex = name_to_dex[directory]
        if dex >= 649:
            dex = name_to_dex[directory.split('_')[0]]

        canvas.save(f'output/sprites/followsprites/{dex}{modifier}.png')
    
    print(f'Created overworld sprites for {directory}')

def get_form(directory: str) -> str:

    if 'unown' in directory:
        split = directory.split('_')
        if len(split) > 2:
            return '-26' if 'exclamation' in directory else '-27'
        else:
            val = '-' + str(ord(split[1]) - 97)
            return val if val != '-0' else ''

    match directory:
        case 'castform_sunny':
            return '-1'
        case 'castform_rainy':
            return '-2'
        case 'castform_snowy':
            return '-3'
        case 'deoxys_attack':
            return '-1'
        case 'deoxys_defense':
            return '-2'
        case 'deoxys_speed':
            return '-3'
        case 'burmy_sandy':
            return '-1'
        case 'burmy_sandy':
            return '-2'
        case 'wormadam_sandy':
            return '-1'
        case 'wormadam_trash':
            return '-2'
        case 'cherrim_sunny':
            return '-1'
        case 'shellos_east':
            return '-1'
        case 'gastrodon_east':
            return '-1'
        case 'rotom_heat':
            return '-1'
        case 'rotom_wash':
            return '-2'
        case 'rotom_frost':
            return '-3'
        case 'rotom_fan':
            return '-4'
        case 'rotom_mow':
            return '-5'
        case 'giratina_origin':
            return '-1'
        case 'shaymin_sky':
            return '-1'
        case 'basculin_blue':
            return '-1'
        case 'darmanitan_zen':
            return '-1'
        case 'deerling_summer':
            return '-1'
        case 'deerling_fall':
            return '-2'
        case 'deerling_winter':
            return '-3'
        case 'sawsbuck_summer':
            return '-1'
        case 'sawsbuck_winter':
            return '-2'
        case 'sawsbuck_winter':
            return '-3'
        case 'meloetta_pirouette':
            return '-1'
        case 'genesect_douse':
            return '-1'
        case 'genesect_shock':
            return '-2'
        case 'genesect_burn':
            return '-3'
        case 'genesect_chill':
            return '-4'
        case _:
            return ''

def add_sparkles(image: Image):
    sparkle = Image.open('resources/sparkles.png')
    image.paste(sparkle, (0,0), sparkle)
    return image

def get_center_of_mass(image: Image):
    data = image.getcolors()
    color_list = []
    for color in data:
        color_list.append(color)

    colors = [rgb for rgb in color_list if (rgb[1] != (255, 255, 255, 0) and rgb[1] != (255, 255, 255, 255) and rgb[1] != (0, 0, 0, 255) and rgb[1] != (0, 0, 0, 0))]
    
    if len(colors) > 1:
        if colors[0][0] > colors[1][0]:
            most_color = colors[0][1]
        else:
            most_color = colors[1][1]
    else:
        most_color = colors[0][1]

    immat = image.load()
    (x, y) = image.size
    m = np.zeros((x, y))

    for i in range(x):
        for j in range(y):
            m[i, j] = (immat[i, j] == most_color)
    
    m = m / np.sum(np.sum(m))

    dx = np.sum(m, 1)
    return np.sum(dx * np.arange(x))

def create_monster_icon(directory: str, shiny=False, size=1):
    # Size: 0 = 16x16 (Small) | 1 = 26x26 (Medium + Blurry) | 2 = 32x32 (Large)

    # include 'icon' in files. should only be in egg
    icon_files = [ f.name for f in os.scandir(f'./sprites/{directory}') if 'overworld' in f.name or 'icon' in f.name ]
    file = ''
    if 'icon.png' in icon_files:
        file = 'icon.png'
    elif shiny and 'overworld-shiny.png' in icon_files:
        file = 'overworld-shiny.png'
    elif not shiny and 'overworld.png' in icon_files:
        file = 'overworld.png'
    else:
        return    

    monster_img = Image.open(f'sprites/{directory}/{file}')

    w, h = monster_img.size

    frame_num = w//h
    frames = []
    for i in range(0, frame_num):
        frames.append(monster_img.crop((h * i, 0, h * (i + 1), h)))

    one_frame_exceptions = ['egg', 'egg_manaphy', 'krabby', 'kingler']

    if directory in one_frame_exceptions:
        icon_img = frames[0]
    else:
        icon_img = frames[5]

    if size == 1:
        icon_img = icon_img.resize((26, 26), resample=Image.BICUBIC)
    elif size == 2:
        icon_img = icon_img.resize((32, 32), resample=Image.NEAREST)
        
    icon_img = icon_img.crop(icon_img.getbbox())
    w, h = icon_img.size

    canvas = Image.new('RGBA', (36, 36), (255, 255, 255, 0))
    # -1 in the height calculation to make room for the alpha red outline.
    canvas.paste( icon_img, ((36 - w) // 2 , 36 - 1 - h) )

    canvas.save(f'output/sprites/monstericons/{name_to_dex[directory]}-0.png')
    print(f'Created monster icon for {directory}')

if __name__ == '__main__':
    if not os.path.exists('output/sprites/battlesprites'):
        os.makedirs('output/sprites/battlesprites')
    if not os.path.exists('output/sprites/followsprites'):
        os.makedirs('output/sprites/followsprites')
    if not os.path.exists('output/sprites/monstericons'):
        os.makedirs('output/sprites/monstericons')

    dirs = [ f.name for f in os.scandir('./sprites') if f.is_dir() ]

    for dir in dirs:
        try:
            create_front_sprite(dir)
            create_back_sprite(dir)

            if dir in mirror_exclusions:
                create_overworld_sprite(dir, False)
            else:
                create_overworld_sprite(dir)
            
            create_monster_icon(dir)

        except Exception:
            traceback.print_exc()

    shutil.copyfile('resources/atlasdata.txt', 'output/sprites/followsprites/atlasdata.txt')
    print('Added atlas file for followersprites')
