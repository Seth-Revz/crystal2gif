import customtkinter
import os
import shutil
import traceback
from PIL import ImageTk
from zipfile import ZipFile

import script

def set_icon():
    app.iconphoto(False, ImageTk.PhotoImage(file='resources/icon.png'))

def remove_previous_sprites():
    if os.path.exists('output'):
        shutil.rmtree("output")

def create_function():
    no_checks = True
    remove_previous_sprites()

    front_sprites_bool = front_sprites_check_var.get()
    back_sprites_bool = back_sprites_check_var.get()
    overworld_sprites_bool = overworld_sprites_check_var.get()
    icon_sprites_bool = icon_sprites_check_var.get()

    if front_sprites_bool:
        progress_label.configure(text='Creating Front Sprites')
        front_sprites()
        progress_label.configure(text='Done!')
        no_checks = False

    if back_sprites_bool:
        progress_label.configure(text='Creating Back Sprites')
        back_sprites()
        progress_label.configure(text='Done!')
        no_checks = False

    if overworld_sprites_bool:
        progress_label.configure(text='Creating Overworld Sprites')
        overworld_sprites(mirror=mirror_overworld_sprites_check_var.get())
        progress_label.configure(text='Done!')
        no_checks = False
    
    if icon_sprites_bool:
        progress_label.configure(text='Creating Monster Icons')
        monster_icons(shiny=shiny_icon_sprites_check_var.get())
        progress_label.configure(text='Done!')
        no_checks = False

    app.update()

    if not no_checks:
        progress_label.configure(text='Done!\nCreating Mod File')
        with ZipFile('output/Revz Gen 2.zip', 'w') as zip_object:
            for folder_name, sub_folders, file_names in os.walk('output/sprites'):
                for filename in file_names:
                    file_path = os.path.join(folder_name, filename)
                    zip_object.write(file_path, file_path.split('/', 1)[1])
                    app.update()

            zip_object.write('resources/icon.png', 'icon.png')
            zip_object.write('resources/info.xml', 'info.xml')

        if os.path.exists('output/Revz Gen 2.zip'):
            progress_label.configure(text='Done!\n`Revz Gen 2.zip` created')
        else:
            progress_label.configure(text='Error while creating mod file. D:')

def icon_checkbox_function():
    if not icon_sprites_check_var.get():
        shiny_icon_sprites_checkbox.deselect()
        shiny_icon_sprites_checkbox.configure(state=customtkinter.DISABLED)
    else:
        shiny_icon_sprites_checkbox.configure(state=customtkinter.NORMAL)

def overworld_checkbox_function():
    if not overworld_sprites_check_var.get():
        mirror_overworld_sprites_checkbox.deselect()
        mirror_overworld_sprites_checkbox.configure(state=customtkinter.DISABLED)
    else:
        mirror_overworld_sprites_checkbox.configure(state=customtkinter.NORMAL)

def mirrored_checkbox_function():
    pass

def front_sprites():
    if not os.path.exists('output/sprites/battlesprites'):
        os.makedirs('output/sprites/battlesprites')

    dirs = [ f.name for f in os.scandir('./sprites') if f.is_dir() ]
    progressbar._determinate_speed = 1 / len(dirs) * 50
    progressbar.set(0)

    for dir in dirs:
        app.update()
        progressbar.step()
        
        try:
            script.create_front_sprite(dir, 0, True)
            # print(f'Created front battle sprites for {dir.capitalize()}')
        except Exception:
            traceback.print_exc()

def back_sprites():
    if not os.path.exists('output/sprites/battlesprites'):
        os.makedirs('output/sprites/battlesprites')

    dirs = [ f.name for f in os.scandir('./sprites') if f.is_dir() ]
    progressbar._determinate_speed = 1 / len(dirs) * 50
    progressbar.set(0)

    for dir in dirs:
        app.update()
        progressbar.step()
        
        try:
            script.create_back_sprite(dir, 0, True)
            # print(f'Created back battle sprites for {dir.capitalize()}')
        except Exception:
            traceback.print_exc()

def overworld_sprites(mirror=False):
    if not os.path.exists('output/sprites/followsprites'):
        os.makedirs('output/sprites/followsprites')

    dirs = [ f.name for f in os.scandir('./sprites') if f.is_dir() ]
    progressbar._determinate_speed = 1 / len(dirs) * 50
    progressbar.set(0)

    for dir in dirs:
        app.update()
        progressbar.step()

        try:
            if dir in script.mirror_exclusions:
                script.create_overworld_sprite(dir, False)
            else:
                script.create_overworld_sprite(dir, mirror=mirror)
            # print(f'Created overworld sprites for {dir.capitalize()}')
        except Exception:
            traceback.print_exc()
    
    shutil.copyfile('resources/atlasdata.txt', 'output/sprites/followsprites/atlasdata.txt')
    print('Added atlas file for overworld sprites')

def monster_icons(shiny=False):
    if not os.path.exists('output/sprites/monstericons'):
        os.makedirs('output/sprites/monstericons')

    dirs = [ f.name for f in os.scandir('./sprites') if f.is_dir() ]
    progressbar._determinate_speed = 1 / len(dirs) * 50
    progressbar.set(0)

    for dir in dirs:
        app.update()
        progressbar.step()
        
        try:
            script.create_monster_icon(dir, shiny=shiny)
            # print(f'Created monster icon for {dir.capitalize()}')
        except Exception:
            traceback.print_exc()

if __name__ == '__main__':
    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")

    app = customtkinter.CTk()
    sw = int(app.winfo_screenwidth() * 1.5)
    sh = int(app.winfo_screenheight() * 1.5)
    w = 260
    h = 300

    app.geometry(f'{w}x{h}+{(sw // 2) - (int(w * 1.5) // 2)}+{(sh // 2) - (int(h * 1.5) // 2)}')
    app.title('Mod Creator')
    app.resizable(False, False)
    app.after(185, func=set_icon)
    app.after(200, func=set_icon)

    front_sprites_check_var = customtkinter.BooleanVar(value=True)
    front_sprites_checkbox = customtkinter.CTkCheckBox(app, text="Front Sprites", variable=front_sprites_check_var, onvalue=True, offvalue=False, corner_radius=7)
    front_sprites_checkbox.place(relx=.25, rely=.08, anchor=customtkinter.W)

    back_sprites_check_var = customtkinter.BooleanVar(value=True)
    back_sprites_checkbox = customtkinter.CTkCheckBox(app, text="Back Sprites", variable=back_sprites_check_var, onvalue=True, offvalue=False, corner_radius=7)
    back_sprites_checkbox.place(relx=.25, rely=.19, anchor=customtkinter.W)

    overworld_sprites_check_var = customtkinter.BooleanVar(value=True)
    overworld_sprites_checkbox = customtkinter.CTkCheckBox(app, text="Overworld Sprites", variable=overworld_sprites_check_var, command=overworld_checkbox_function, onvalue=True, offvalue=False, corner_radius=7)
    overworld_sprites_checkbox.place(relx=.25, rely=.30, anchor=customtkinter.W)

    mirror_overworld_sprites_check_var = customtkinter.BooleanVar(value=True)
    mirror_overworld_sprites_checkbox = customtkinter.CTkCheckBox(app, text="Mirrored Sprites", variable=mirror_overworld_sprites_check_var, command=mirrored_checkbox_function, onvalue=True, offvalue=False, corner_radius=7)
    mirror_overworld_sprites_checkbox.place(relx=.3, rely=.40, anchor=customtkinter.W)

    icon_sprites_check_var = customtkinter.BooleanVar(value=True)
    icon_sprites_checkbox = customtkinter.CTkCheckBox(app, text="Monster Icons", variable=icon_sprites_check_var, command=icon_checkbox_function, onvalue=True, offvalue=False, corner_radius=7)
    icon_sprites_checkbox.place(relx=.25, rely=.51, anchor=customtkinter.W)

    shiny_icon_sprites_check_var = customtkinter.BooleanVar(value=False)
    shiny_icon_sprites_checkbox = customtkinter.CTkCheckBox(app, text="Shiny Icons", variable=shiny_icon_sprites_check_var, onvalue=True, offvalue=False, corner_radius=7)
    shiny_icon_sprites_checkbox.place(relx=.3, rely=.61, anchor=customtkinter.W)

    create_button = customtkinter.CTkButton(master=app, text="Create Mod", command=create_function, corner_radius=7)
    create_button.place(relx=.5, rely=.75, anchor=customtkinter.CENTER)

    progressbar = customtkinter.CTkProgressBar(app, orientation="horizontal", mode='determinate')
    progressbar.set(0)
    progressbar.place(relx=.5, rely=.85, anchor=customtkinter.CENTER)

    progress_label = customtkinter.CTkLabel(master=app, text='')
    progress_label.place(relx=.5, rely=.92, anchor=customtkinter.CENTER)

    app.mainloop()