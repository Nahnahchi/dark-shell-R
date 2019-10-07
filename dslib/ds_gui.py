from dslib.ds_process import DSRProcess
from os.path import join
from os import getenv, makedirs
from tkinter import Tk, Label, StringVar, BooleanVar, Spinbox, Button, Entry, Checkbutton, LabelFrame
from threading import Thread
from time import sleep
from pickle import dump, load, UnpicklingError


save_dir = join(getenv("APPDATA"), "DarkShell", "save")
try:
    makedirs(save_dir)
except FileExistsError:
    pass


class DSRGraphicsGUI(Tk):

    SAVE_FILE = join(save_dir, "graphics")
    SAVED_DATA = {
        "override f": False,
        "sync br": True,
        "sync co": True,
        "brightness r": 1.000,
        "brightness g": 1.000,
        "brightness b": 1.000,
        "contrast r": 1.500,
        "contrast g": 1.500,
        "contrast b": 1.500,
        "saturation": 1.000,
        "hue": 0.000
    }

    def __init__(self, process: DSRProcess):

        super(DSRGraphicsGUI, self).__init__()

        try:
            saved = load(open(DSRGraphicsGUI.SAVE_FILE, "rb"))
        except (UnpicklingError, FileNotFoundError):
            saved = DSRGraphicsGUI.SAVED_DATA

        self.process = process

        self.title("GraphicsGUI")
        self.resizable(False, False)

        render = LabelFrame(self, text="Render")
        render.pack(fill="both")

        self.draw_map = BooleanVar()
        self.draw_map.set(True)
        Checkbutton(render, text="Map", var=self.draw_map,
                    command=self.set_draw_map).grid(row=0, column=0, sticky="W")

        self.draw_creatures = BooleanVar()
        self.draw_creatures.set(True)
        Checkbutton(render, text="Creatures", var=self.draw_creatures,
                    command=self.set_draw_creatures).grid(row=1, column=0, sticky="W")

        self.draw_objects = BooleanVar()
        self.draw_objects.set(True)
        Checkbutton(render, text="Objects", var=self.draw_objects,
                    command=self.set_draw_objects).grid(row=2, column=0, sticky="W")

        self.draw_sfx = BooleanVar()
        self.draw_sfx.set(True)
        Checkbutton(render, text="SFX", var=self.draw_sfx,
                    command=self.set_draw_sfx).grid(row=3, column=0, sticky="W")

        self.draw_cutscenes = BooleanVar()
        self.draw_cutscenes.set(True)
        Checkbutton(render, text="Cutscenes", var=self.draw_cutscenes,
                    command=self.set_draw_cutscenes).grid(row=4, column=0, sticky="W")

        filter_ = LabelFrame(self, text="Filter")
        filter_.pack()
        self.override_filter = BooleanVar()
        self.override_filter.set(saved["override f"])
        Checkbutton(filter_, text="Override Filter", var=self.override_filter,
                    command=self.set_override_filter).grid(row=0, column=0, sticky="W")

        Label(filter_, text="Brightness (RGB)").grid(row=1, column=0, sticky="W")
        self.sync_brightness = BooleanVar()
        self.sync_brightness.set(saved["sync br"])
        Checkbutton(filter_, text="Synchronize", var=self.sync_brightness).grid(row=1, column=1, sticky="W")

        self.brightness_r = StringVar()
        self.brightness_r.set(saved["brightness r"])
        box_br_r = Spinbox(filter_, from_=-1000, to=1000, format="%.3f", textvariable=self.brightness_r, width=15,
                           command=self.set_brightness_r)
        box_br_r.grid(row=2, column=0, sticky="W")
        box_br_r.bind("<Return>", self.set_brightness_r)

        self.brightness_g = StringVar()
        self.brightness_g.set(saved["brightness g"])
        box_br_g = Spinbox(filter_, from_=-1000, to=1000, format="%.3f", textvariable=self.brightness_g, width=15,
                           command=self.set_brightness_g)
        box_br_g.grid(row=2, column=1, sticky="W")
        box_br_g.bind("<Return>", self.set_brightness_g)

        self.brightness_b = StringVar()
        self.brightness_b.set(saved["brightness b"])
        box_br_b = Spinbox(filter_, from_=-1000, to=1000, format="%.3f", textvariable=self.brightness_b, width=15,
                           command=self.set_brightness_b)
        box_br_b.grid(row=2, column=2, sticky="W")
        box_br_b.bind("<Return>", self.set_brightness_b)

        Label(filter_, text="Contrast (RGB)").grid(row=3, column=0, sticky="W")
        self.sync_contrast = BooleanVar()
        self.sync_contrast.set(saved["sync co"])
        Checkbutton(filter_, text="Synchronize", var=self.sync_contrast).grid(row=3, column=1, sticky="W")

        self.contrast_r = StringVar()
        self.contrast_r.set(saved["contrast r"])
        box_co_r = Spinbox(filter_, from_=-1000, to=1000, format="%.3f", textvariable=self.contrast_r, width=15,
                           command=self.set_contrast_r)
        box_co_r.grid(row=4, column=0, sticky="W")
        box_co_r.bind("<Return>", self.set_contrast_r)

        self.contrast_g = StringVar()
        self.contrast_g.set(saved["contrast g"])
        box_co_g = Spinbox(filter_, from_=-1000, to=1000, format="%.3f", textvariable=self.contrast_g, width=15,
                           command=self.set_contrast_g)
        box_co_g.grid(row=4, column=1, sticky="W")
        box_co_g.bind("<Return>", self.set_contrast_g)

        self.contrast_b = StringVar()
        self.contrast_b.set(saved["contrast b"])
        box_co_b = Spinbox(filter_, from_=-1000, to=1000, format="%.3f", textvariable=self.contrast_b, width=15,
                           command=self.set_contrast_b)
        box_co_b.grid(row=4, column=2, sticky="W")
        box_co_b.bind("<Return>", self.set_contrast_b)

        Label(filter_, text="Saturation").grid(row=5, column=0, sticky="W")
        Label(filter_, text="Hue").grid(row=5, column=2, sticky="W")
        self.saturation = StringVar()
        self.saturation.set(saved["saturation"])
        box_sat = Spinbox(filter_, from_=-1000, to=1000, format="%.3f", textvariable=self.saturation, width=15,
                          command=self.set_saturation)
        box_sat.grid(row=6, column=0, sticky="W")
        box_sat.bind("<Return>", self.set_saturation)
        self.hue = StringVar()
        self.hue.set(saved["hue"])
        box_hue = Spinbox(filter_, from_=-1000, to=1000, format="%.3f", textvariable=self.hue, width=15,
                          command=self.set_hue)
        box_hue.grid(row=6, column=2, sticky="W")
        box_hue.bind("<Return>", self.set_hue)

        if saved["override f"]:
            self.set_override_filter()

    def save_state(self):
        DSRGraphicsGUI.SAVED_DATA["override f"] = self.override_filter.get()
        DSRGraphicsGUI.SAVED_DATA["sync br"] = self.sync_brightness.get()
        DSRGraphicsGUI.SAVED_DATA["sync co"] = self.sync_contrast.get()
        DSRGraphicsGUI.SAVED_DATA["brightness r"] = self.brightness_r.get()
        DSRGraphicsGUI.SAVED_DATA["contrast r"] = self.contrast_r.get()
        DSRGraphicsGUI.SAVED_DATA["brightness g"] = self.brightness_g.get()
        DSRGraphicsGUI.SAVED_DATA["contrast g"] = self.contrast_g.get()
        DSRGraphicsGUI.SAVED_DATA["brightness b"] = self.brightness_b.get()
        DSRGraphicsGUI.SAVED_DATA["contrast b"] = self.contrast_b.get()
        DSRGraphicsGUI.SAVED_DATA["saturation"] = self.saturation.get()
        DSRGraphicsGUI.SAVED_DATA["hue"] = self.hue.get()
        dump(DSRGraphicsGUI.SAVED_DATA, open(DSRGraphicsGUI.SAVE_FILE, "wb"))

    def set_override_filter(self):
        self.process.override_filter(self.override_filter.get())
        if self.override_filter.get():
            self.set_brightness_r(), self.set_contrast_r()
            self.set_brightness_g(), self.set_contrast_g()
            self.set_brightness_b(), self.set_contrast_b()
            self.set_saturation(), self.set_hue()
        self.save_state()

    def set_brightness_r(self, *e):
        if self.sync_brightness.get():
            self.brightness_b.set(self.brightness_r.get())
            self.brightness_g.set(self.brightness_r.get())
        self.process.set_brightness(
            float(self.brightness_r.get()),
            float(self.brightness_g.get()),
            float(self.brightness_b.get())
        )
        self.save_state()

    def set_brightness_g(self, *e):
        if self.sync_brightness.get():
            self.brightness_b.set(self.brightness_g.get())
            self.brightness_r.set(self.brightness_g.get())
        self.process.set_brightness(
            float(self.brightness_r.get()),
            float(self.brightness_g.get()),
            float(self.brightness_b.get())
        )
        self.save_state()

    def set_brightness_b(self, *e):
        if self.sync_brightness.get():
            self.brightness_r.set(self.brightness_b.get())
            self.brightness_g.set(self.brightness_b.get())
        self.process.set_brightness(
            float(self.brightness_r.get()),
            float(self.brightness_g.get()),
            float(self.brightness_b.get())
        )
        self.save_state()

    def set_contrast_r(self, *e):
        if self.sync_contrast.get():
            self.contrast_g.set(self.contrast_r.get())
            self.contrast_b.set(self.contrast_r.get())
        self.process.set_contrast(
            float(self.contrast_r.get()),
            float(self.contrast_g.get()),
            float(self.contrast_b.get())
        )
        self.save_state()

    def set_contrast_g(self, *e):
        if self.sync_contrast.get():
            self.contrast_r.set(self.contrast_g.get())
            self.contrast_b.set(self.contrast_g.get())
        self.process.set_contrast(
            float(self.contrast_r.get()),
            float(self.contrast_g.get()),
            float(self.contrast_b.get())
        )
        self.save_state()

    def set_contrast_b(self, *e):
        if self.sync_contrast.get():
            self.contrast_g.set(self.contrast_b.get())
            self.contrast_r.set(self.contrast_b.get())
        self.process.set_contrast(
            float(self.contrast_r.get()),
            float(self.contrast_g.get()),
            float(self.contrast_b.get())
        )
        self.save_state()

    def set_saturation(self, *e):
        self.process.set_saturation(float(self.saturation.get()))
        self.save_state()

    def set_hue(self, *e):
        self.process.set_hue(float(self.hue.get()))
        self.save_state()

    def set_draw_map(self):
        self.process.draw_map(self.draw_map.get())

    def set_draw_creatures(self):
        self.process.draw_creatures(self.draw_creatures.get())

    def set_draw_objects(self):
        self.process.draw_objects(self.draw_objects.get())

    def set_draw_sfx(self):
        self.process.draw_sfx(self.draw_sfx.get())

    def set_draw_cutscenes(self):
        self.process.draw_cutscenes(self.draw_cutscenes.get())


class DSRPositionGUI(Tk):

    def __init__(self, process: DSRProcess):

        super(DSRPositionGUI, self).__init__()

        self.process = process
        self.exit_flag = False

        self.title("PosGUI")
        self.protocol("WM_DELETE_WINDOW", self.on_quit)
        self.resizable(False, False)

        Label(self, text="current").grid(column=2, row=2)
        Label(self, text="stable").grid(column=3, row=2)
        Label(self, text="stored").grid(column=4, row=2)
        Label(self, text="X").grid(column=1, row=3)
        Label(self, text="Y").grid(column=1, row=4)
        Label(self, text="Z").grid(column=1, row=5)
        Label(self, text="α").grid(column=1, row=6)

        self.x_current = StringVar()
        Entry(self, width=10, state="readonly", textvariable=self.x_current).grid(column=2, row=3)
        self.x_stable = StringVar()
        Entry(self, width=10, state="readonly", textvariable=self.x_stable).grid(column=3, row=3)
        self.x_stored = StringVar()
        self.x_stored.set(process.get_pos_stable()[0])
        Spinbox(self, from_=-1000, to=1000, format="%.3f", width=10, textvariable=self.x_stored).grid(column=4, row=3)

        self.y_current = StringVar()
        Entry(self, width=10, state="readonly", textvariable=self.y_current).grid(column=2, row=4)
        self.y_stable = StringVar()
        Entry(self, width=10, state="readonly", textvariable=self.y_stable).grid(column=3, row=4)
        self.y_stored = StringVar()
        self.y_stored.set(process.get_pos_stable()[1])
        Spinbox(self, from_=-1000, to=1000, format="%.3f", width=10, textvariable=self.y_stored).grid(column=4, row=4)

        self.z_current = StringVar()
        Entry(self, width=10, state="readonly", textvariable=self.z_current).grid(column=2, row=5)
        self.z_stable = StringVar()
        Entry(self, width=10, state="readonly", textvariable=self.z_stable).grid(column=3, row=5)
        self.z_stored = StringVar()
        self.z_stored.set(process.get_pos_stable()[2])
        Spinbox(self, from_=-1000, to=1000, format="%.3f", width=10, textvariable=self.z_stored).grid(column=4, row=5)

        self.a_current = StringVar()
        Entry(self, width=10, state="readonly", textvariable=self.a_current).grid(column=2, row=6)
        self.a_stable = StringVar()
        Entry(self, width=10, state="readonly", textvariable=self.a_stable).grid(column=3, row=6)
        self.a_stored = StringVar()
        self.a_stored.set(process.get_pos_stable()[3])
        Spinbox(self, from_=-360, to=360, format="%.3f", width=10, textvariable=self.a_stored).grid(column=4, row=6)

        Button(self, width=7, text="store", command=self.store).grid(column=2, row=7)
        Button(self, width=7, text="restore", command=self.restore).grid(column=4, row=7)

        Thread(target=self.update).start()

    def update(self):
        while not self.exit_flag:
            self.x_current.set("%.3f" % self.process.get_pos()[0])
            self.x_stable.set("%.3f" % self.process.get_pos_stable()[0])
            self.y_current.set("%.3f" % self.process.get_pos()[1])
            self.y_stable.set("%.3f" % self.process.get_pos_stable()[1])
            self.z_current.set("%.3f" % self.process.get_pos()[2])
            self.z_stable.set("%.3f" % self.process.get_pos_stable()[2])
            self.a_current.set("%.3f" % self.process.get_pos()[3])
            self.a_stable.set("%.3f" % self.process.get_pos_stable()[3])
            sleep(0.2)

    def store(self):
        self.x_stored.set(self.x_current.get())
        self.y_stored.set(self.y_current.get())
        self.z_stored.set(self.z_current.get())
        self.a_stored.set(self.a_current.get())

    def restore(self):
        try:
            self.process.jump_pos(
                float(self.x_stored.get()),
                float(self.y_stored.get()),
                float(self.z_stored.get()),
                float(self.a_stored.get())
            )
        except ValueError as e:
            print(e)

    def on_quit(self):
        self.exit_flag = True
        self.destroy()
