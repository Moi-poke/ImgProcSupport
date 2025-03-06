#!/usr/bin/python3

# from datetime import datetime
from enum import Enum
# import glob

# import logging

import os
import pathlib
from typing import Any, Optional
import numpy as np

import toml
from GUI import GuiApp, initSetting
from PIL import ImageTk, Image
import cv2
from tkinterdnd2 import DND_FILES
from tkinter import filedialog, messagebox

import sys
from loguru import logger

BASE_PATH: pathlib.Path = pathlib.Path(sys.argv[0]).parent



class ColorType(Enum):
    # @staticmethod
    # def _generate_next_value_(name, start, count, last_values):
    #     return count

    COLOR = 0
    GRAY = 1
    BINARY = 2


class mainwindow(GuiApp):
    def __init__(self, master: Optional[Any] = None) -> None:
        super().__init__()

        # Setting window initialization
        self.setting = initSetting(master=self.mainwindow)
        self.setting.mainwindow.title("Setting")
        self.setting.mainwindow.protocol(
            "WM_DELETE_WINDOW", self.setting.mainwindow.withdraw
        )

        # Image and canvas initialization
        self.imageCV: cv2.Mat = None
        self.imageTempCV: cv2.Mat = None
        self.imagePIL: ImageTk.PhotoImage = None
        self.imageTempPIL: ImageTk.PhotoImage = None
        self.image: int | None = None
        self.imageTemp: int | None = None

        # Drag and drop settings for mainCanvas and canvas_2
        self.mainCanvas.drop_target_register(DND_FILES)
        self.mainCanvas.dnd_bind("<<Drop>>", self.loadImage)
        self.canvas_2.drop_target_register(DND_FILES)
        self.canvas_2.dnd_bind("<<Drop>>", self.loadTempImage)


        # Rectangle drawing settings
        self.rect: Any = None
        self.start_x: Optional[int] = None
        self.start_y: Optional[int] = None
        self.end_x: Optional[int] = None
        self.end_y: Optional[int] = None
        self.left_top_x: int = 0
        self.right_bottom_x: int = 1280
        self.left_top_y: int = 0
        self.right_bottom_y: int = 720
        self.mainCanvas.bind("<Button-1>", self.on_button_press)
        self.mainCanvas.bind("<Button-3>", self.on_right_button_press)
        self.mainCanvas.bind("<B1-Motion>", self.on_drag)
        self.mainCanvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.saveSelectArea.configure(command=self.saveRectArea)

        # Threshold and color mode settings
        self._threshold.set(0.80)
        self._BinaryThreshold.set(128)
        self.rbColor.configure(command=self.img_color_setting)
        self.rbGray.configure(command=self.img_color_setting)
        self.rbBin.configure(command=self.img_color_setting)

        # Other settings
        self.rectStart: list | None = None
        self.rectEnd: list | None = None
        self.aspectRatio = 16 / 9
        self.pathImage: str | None = None
        self._pathImage: str | None = None
        self.pathTempImage: str | None = None
        self.entryCommandShow.configure(state="readonly")
        commandGenerations: list = self.get_cfg_files(f"{BASE_PATH}/cfg/command")
        self.cbCommand.configure(values=commandGenerations)
        self.cbCommand.set(commandGenerations[0])
        self.found: list = []
        self._threshold.trace("w", self.callTemplateMatching)
        self._BinaryThreshold.trace("w", self.callTemplateMatching)
        self.img_color_setting()
        self.openSetting.configure(command=self.reshowSetting)
        self.getLatest.configure(command=self.getLatestPNG)
        self.loadTemplate.configure(command=self.loadTemplateImage)
        self.setting.mainwindow.attributes("-topmost", True)
        self.setting.ButtonSetImgDir.configure(command=self.setImgDir)
        self.setting.ButtonSetResourceRoot.configure(command=self.setResourceRoot)
        self.setting.buttonOK.configure(command=self.applySetting)
        self.setting.entryImgDir.configure(state="readonly")
        self.setting.entryRescRoot.configure(state="readonly")
        self.setting.cbLanguage.configure(state="readonly")
        self.setting.cbLanguage.configure(
            values=[
                # f[:-5] for f in os.listdir(f"{BASE_PATH}/lang") if f.endswith(".toml")
                f.stem
                for f in pathlib.Path(f"{BASE_PATH}/lang").iterdir()
                if f.suffix == ".toml"
            ]
        )
        self.resourceRootPath: pathlib.Path = BASE_PATH
        self.ImageDirectoryPath: pathlib.Path = BASE_PATH
        self.mainwindow.protocol("WM_DELETE_WINDOW", self._close)
        self.setConfig()
        self.loadImage()
        self.loadTempImage()

        self.setting.pathImgDir.set(str(self.ImageDirectoryPath))
        self.setting.pathRescRoot.set(str(self.resourceRootPath))

    # Function to close the application
    def _close(self) -> None:
        try:
            self.saveMainConfig()
            self.mainwindow.destroy()
        except Exception as e:
            logger.exception(e)

    # Function to set the configuration
    def setConfig(self) -> None:
        self.loadMainConfig()
        self.setLanguage()

    # Function to load the main configuration
    def loadMainConfig(self) -> None:
        try:
            path = "./cfg/main.toml"
            # ディレクトリが存在しない場合は作成
            # if not os.path.exists(log_dir):
            if not pathlib.Path(path).exists():
                logger.debug("Config file not found. Generate config.")
                self.saveMainConfig(path)
            with open(path, "r", encoding="utf-8") as f:
                config = toml.load(f)
                self.setting.lang.set(config.get("lang", "./NOEXIST"))
                self.setLanguage(config.get("lang", "./NOEXIST"))
                self.commandStyle.set(config.get("command", "./NOEXIST"))

                # if os.path.exists(p := config.get("lastImage", "./NOEXIST")):
                if pathlib.Path(p := config.get("lastImage", "./NOEXIST")).exists():
                    self.pathImage = p
                # if os.path.exists(pt := config.get("lastTemplateImage", "./NOEXIST")):

                if pathlib.Path(
                    pt := config.get("lastTemplateImage", "./NOEXIST")
                ).exists():
                    self.pathTempImage = pt

                # if os.path.exists(p := config.get("ImageDirectoryPath", "./NOEXIST")):
                if pathlib.Path(
                    p := config.get("ImageDirectoryPath", "./NOEXIST")
                ).exists():
                    self.ImageDirectoryPath = pathlib.Path(p)

                if pathlib.Path(
                    p := config.get("resourceRootPath", "./NOEXIST")
                ).exists():
                    self.resourceRootPath = pathlib.Path(p)

                self.changePreview()
                # self.template_matching()

        except Exception as e:
            logger.exception(e)

    # Function to save the main configuration
    def saveMainConfig(self, path: str | None = None) -> None:
        if path is None:
            path = "./cfg/main.toml"
        d = {
            "lang": self.setting.lang.get(),
            "command": self.commandStyle.get(),
            "lastImage": self.pathImage,
            "lastTemplateImage": self.pathTempImage,
            "ImageDirectoryPath": self.setting.pathImgDir.get(),
            "resourceRootPath": self.setting.pathRescRoot.get(),
        }
        with open(path, "w", encoding="utf-8") as f:
            toml.dump(d, f)

    # Function to set the language
    def setLanguage(self, lang: str | None = None) -> None:
        try:
            if lang is None:
                path = f"./lang/{self.setting.lang.get()}.toml"
            else:
                path = f"./lang/{lang}.toml"
            with open(path, "r", encoding="utf-8") as f:
                config = toml.load(f)
                self.TVAccuracy.set(config["Accuracy"])
                self.TVCoodinate.set(config["Coodinate"])
                self.TVcount.set(config["count"])
                self.TVgetLatest.set(config["getLatest"])
                self.TVlabelMode.set(config["labelMode"])
                self.TVlabelTempSize.set(config["labelTempSize"])
                self.TVloadTemplate.set(config["loadTemplate"])
                self.TVopenSetting.set(config["openSetting"])
                self.TVsaveSelectArea.set(config["saveSelectArea"])
                self.TVThreshold.set(config["Threshold"])
                # 保存したファイルをtemplateとして読み込むかユーザーに確認する
                self.text_saveTemplate: str = config["saveTemplate"]
                self.text_loadImageError: str = config["loadImageError"]
        except Exception as e:
            logger.exception(e)

    # Function to handle button press event
    def on_button_press(self, event: Any) -> None:
        # delete all previous rectangles
        self.mainCanvas.delete("drawn_rectangle")
        # save mouse drag start position
        self.start_x = min(event.x, self.imagePIL.width())
        self.start_y = min(event.y, self.imagePIL.height())
        self.end_x = min(max(event.x, 0), 640, self.imagePIL.width())
        self.end_y = min(max(event.y, 0), 360, self.imagePIL.height())
        self.rect = self.mainCanvas.create_rectangle(
            self.start_x,
            self.start_y,
            self.start_x,
            self.start_y,
            outline="green",
            width=2,
            tags="drawn_rectangle",
        )

    # Function to handle drag event
    def on_drag(self, event: Any) -> None:
        # update rectangle as mouse is dragged
        # make sure coordinates do not go beyond canvas boundaries
        self.end_x = min(max(event.x, 0), 640, self.imagePIL.width())
        self.end_y = min(max(event.y, 0), 360, self.imagePIL.height())
        self.mainCanvas.coords(
            self.rect, self.start_x, self.start_y, self.end_x, self.end_y
        )

    # Function to handle button release event
    def on_button_release(self, event: Any) -> None:
        if (
            isinstance(self.start_x, int)
            and isinstance(self.end_x, int)
            and isinstance(self.start_y, int)
            and isinstance(self.end_y, int)
        ):
            try:
                self.left_top_x = min(self.start_x, self.end_x) * 2
                self.right_bottom_x = min(
                    max(self.start_x, self.end_x) * 2, self.imagePIL.width() * 2
                )
                self.left_top_y = min(self.start_y, self.end_y) * 2
                self.right_bottom_y = min(
                    max(self.start_y, self.end_y) * 2, self.imagePIL.height() * 2
                )
                self.template_matching()
            except Exception as e:
                logger.exception(e)

    # Function to handle right button press event
    def on_right_button_press(self, event: Any) -> None:
        self.mainCanvas.delete("drawn_rectangle")
        self.resetRect()
        self.template_matching()

    # Function to re-display the setting's toplevel that was withdrawn
    def reshowSetting(self) -> None:
        self.setting.mainwindow.deiconify()

    # Function to reset the rectangle
    def resetRect(self) -> None:
        if self.rect is not None:
            self.left_top_x = 0
            self.right_bottom_x = 1280
            self.left_top_y = 0
            self.right_bottom_y = 720
            self.mainCanvas.delete(self.rect)
            self.mainCanvas.delete("drawn_rectangle")
        else:
            return

    # Function to set the image directory
    def setImgDir(self) -> None:
        if self.ImageDirectoryPath == "":
            # init_dir = os.path.abspath(BASE_PATH)
            init_dir = pathlib.Path(BASE_PATH).absolute()
        else:
            init_dir = self.ImageDirectoryPath
            _ = filedialog.askdirectory(initialdir=str(init_dir))
            if _ == "":
                return
            else:
                self.ImageDirectoryPath = pathlib.Path(_)
        self.setting.pathImgDir.set(str(self.ImageDirectoryPath))

    # Function to set the resource root
    def setResourceRoot(self) -> None:
        if self.resourceRootPath == "":
            # init_dir = os.path.abspath(BASE_PATH)
            init_dir = pathlib.Path(BASE_PATH).absolute()
        else:
            init_dir = self.resourceRootPath
            _ = filedialog.askdirectory(initialdir=str(init_dir))
            if _ == "":
                return
            else:
                self.resourceRootPath = pathlib.Path(_)
        self.setting.pathRescRoot.set(str(self.resourceRootPath))

    # Function to apply the settings
    def applySetting(self) -> None:
        self.ImageDirectoryPath = pathlib.Path(self.setting.pathImgDir.get())
        self.resourceRootPath = pathlib.Path(self.setting.pathRescRoot.get())
        self.setLanguage()
        self.template_matching()
        self.setting.mainwindow.withdraw()

    # Function to call the template matching
    def callTemplateMatching(self, *event: Any) -> None:
        self.changePreview()

    # Function to get the latest PNG
    def getLatestPNG(self) -> None:
        if pathlib.Path(self.ImageDirectoryPath) == pathlib.Path(""):
            logger.warning("Set Directory First.")
        else:
            _ = self.get_latest_png_file(self.ImageDirectoryPath)
            if _ == "":
                return
            else:
                self.pathImage = _
                self.resetRect()

                self.changePreview()

    # Function to load the template image
    def loadTemplateImage(self) -> None:
        if self.resourceRootPath == pathlib.Path(""):
            # init_dir = os.path.abspath(BASE_PATH)
            init_dir = pathlib.Path(BASE_PATH).absolute()
        else:
            init_dir = self.resourceRootPath
        _ = filedialog.askopenfilename(
            initialdir=str(init_dir), filetypes=[("png", "*.png")]
        )
        if _ == "":
            return
        else:
            self.pathTempImage = _
            self.resetRect()

            self.changePreview()

    # Function to load the image
    def loadImage(self, event: Any = None) -> bool:
        if event is not None:
            logger.debug(f"Event data: {event.data}")
            _path: str = str(event.data)
            self.pathImage = _path
            self.resetRect()
            self.changePreview()
            return True
        else:
            try:
                self.resetRect()
                self.changePreview()
                return True
            except Exception:
                logger.exception("Caught an error: ", exc_info=True)
                return False

        # if _path.endswith(".png"):
        #     try:
        #         self.pathImage = _path
        #         # logger.debug(self.pathImage)
        #         self.resetRect()
        #         self.changePreview()
        #         return True
        #     except Exception:
        #         logger.exception("Caught an error: ", exc_info=True)
        #         return False

    # Function to load the template image
    def loadTempImage(self, event: Any = None) -> bool:
        if event is not None:
            logger.debug(f"Event data: {event.data}")
            _path: str = str(event.data)
            self.pathTempImage = _path
            self.resetRect()
            self.changePreview()
            return True
        else:
            try:
                self.resetRect()
                self.changePreview()
                return True
            except Exception:
                logger.exception("Caught an error: ", exc_info=True)
                return False
        # if _path.endswith(".png"):
        #     try:
        #         self.pathTempImage = _path
        #         self.resetRect()
        #         self.changePreview()
        #         return True
        #     except Exception:
        #         logger.exception("Caught an error: ", exc_info=True)
        #         return False

    # Function to switch binary state
    def switchBinaryState(self, *event: Any) -> None:
        if self.useAutoOtsu.get():
            self.sbBinary.configure(state="disable")
            self.sliderBinaryTh.configure(state="disable")
        else:
            self.sbBinary.configure(state="normal")
            self.sliderBinaryTh.configure(state="normal")
        self.changePreview()

    # Function to run the application
    def run(self) -> None:
        self.setting.mainwindow.withdraw()
        logger.debug("Start Mainloop")
        self.mainwindow.mainloop()

    def img_color_setting(self) -> None:
        match ColorType(self.colorMode.get()):
            case ColorType.COLOR:
                self.colorMode.set(ColorType.COLOR.value)
                self.pixmap_mode = "Color"
                logger.debug("change to Color mode")
                self.cbAutoBin.configure(state="disable")
                self.sbBinary.configure(state="disable")
                self.sliderBinaryTh.configure(state="disable")
            case ColorType.GRAY:
                self.colorMode.set(ColorType.GRAY.value)
                self.pixmap_mode = "Gray Scale"
                logger.debug("change to Gray-scale mode")
                self.cbAutoBin.configure(state="disable")
                self.sbBinary.configure(state="disable")
                self.sliderBinaryTh.configure(state="disable")
            case ColorType.BINARY:
                self.colorMode.set(ColorType.BINARY.value)
                self.pixmap_mode = "Binarization"
                logger.debug("change to Binary mode")
                self.cbAutoBin.configure(state="normal")
                self.sbBinary.configure(state="normal")
                self.sliderBinaryTh.configure(state="normal")
        self.changePreview()

    def changePreview(self) -> None:
        try:
            if self.pathImage is None:
                updateImage = False
            else:
                updateImage = True
                buf = np.fromfile(self.pathImage, np.uint8)
                _imageCV = cv2.imdecode(buf, cv2.IMREAD_UNCHANGED)
                if not (_imageCV.shape[0] == 720 and _imageCV.shape[1] == 1280):
                    messagebox.showwarning("Error", self.text_loadImageError)
                    logger.error(f"Image size is {_imageCV.shape}")
                    updateImage = False
                    self.pathImage = self._pathImage
                self._pathImage = self.pathImage

                # _imageCV = cv2.imread(self.pathImage)

            if self.pathTempImage is None:
                updateTempImage = False
            else:
                updateTempImage = True
                buf = np.fromfile(self.pathTempImage, np.uint8)
                _imageTemp = cv2.imdecode(buf, cv2.IMREAD_UNCHANGED)
                # _imageTemp = cv2.imread(self.pathTempImage)

            if not updateImage and not updateTempImage:
                return

            if self.pixmap_mode == "Color":
                if updateImage:
                    # target
                    self.imageCV = cv2.cvtColor(_imageCV, cv2.COLOR_BGR2RGB)
                    self.imagePIL = Image.fromarray(self.imageCV)
                if updateTempImage:
                    # template
                    self.imageTempCV = cv2.cvtColor(_imageTemp, cv2.COLOR_BGR2RGB)
                    self.imageTempPIL = Image.fromarray(self.imageTempCV)

            elif self.pixmap_mode == "Gray Scale":
                if updateImage:
                    # target
                    self.imageCV = cv2.cvtColor(_imageCV, cv2.COLOR_BGR2GRAY)
                    self.imagePIL = Image.fromarray(self.imageCV)
                if updateTempImage:
                    # template
                    self.imageTempCV = cv2.cvtColor(_imageTemp, cv2.COLOR_BGR2GRAY)
                    self.imageTempPIL = Image.fromarray(self.imageTempCV)

            elif self.pixmap_mode == "Binarization":
                if updateImage:
                    # target
                    self.imageCV = cv2.cvtColor(_imageCV, cv2.COLOR_BGR2GRAY)
                    if self.useAutoOtsu.get():
                        self.threshold, self.imageCV = cv2.threshold(
                            self.imageCV, 0, 255, cv2.THRESH_OTSU
                        )
                        self._BinaryThreshold.set(int(self.threshold))
                        self.imagePIL = Image.fromarray(self.imageCV)
                    else:
                        self.threshold = self._BinaryThreshold.get()
                        self.threshold, self.imageCV = cv2.threshold(
                            self.imageCV, self.threshold, 255, cv2.THRESH_BINARY
                        )
                        self.imagePIL = Image.fromarray(self.imageCV)
                if updateTempImage:
                    # template
                    # [TODO] Since the target and the template are different files, the threshold determined by Otsu's method may vary.
                    self.imageTempCV = cv2.cvtColor(_imageTemp, cv2.COLOR_BGR2GRAY)
                    # if self.useAutoOtsu.get():
                    #     self.threshold, self.imageTempCV = cv2.threshold(self.imageTempCV, 0, 255, cv2.THRESH_OTSU)
                    #     # self._BinaryThreshold.set(self.threshold)
                    #     self.imageTempPIL = Image.fromarray(self.imageTempCV)

                    # else:
                    self.threshold = self._BinaryThreshold.get()
                    self.threshold, self.imageTempCV = cv2.threshold(
                        self.imageTempCV, self.threshold, 255, cv2.THRESH_BINARY
                    )
                    self.imageTempPIL = Image.fromarray(self.imageTempCV)

            if updateImage:
                w = self.imagePIL.width
                h = self.imagePIL.height
                self.aspectRatio = w / h
                if self.aspectRatio > 16 / 9:
                    self.multiply = 640 / w
                else:
                    self.multiply = 360 / h
                self.imagePIL = self.imagePIL.resize(
                    (int(w * self.multiply), int(h * self.multiply))
                )

                self.imagePIL = ImageTk.PhotoImage(self.imagePIL)
                # logger.debug(self.imagePIL.width())

                # ラベルに画像を指定
                if self.image is None:
                    self.image = self.mainCanvas.create_image(
                        0, 0, image=self.imagePIL, anchor="nw"
                    )
                else:
                    self.mainCanvas.itemconfig(self.image, image=self.imagePIL)
                # if

            if updateTempImage:
                logger.debug("Updating the template image preview")
                w = self.imageTempPIL.width
                h = self.imageTempPIL.height
                ar = w / h
                if ar > 16 / 9:
                    multiply = 352 / w
                else:
                    multiply = 198 / h

                resized_image = self.imageTempPIL.resize(
                    (int(w * multiply), int(h * multiply))
                )
                self.imageTempPIL = ImageTk.PhotoImage(resized_image)

                if self.imageTemp is None:
                    self.imageTemp = self.canvas_2.create_image(
                        (352 - self.imageTempPIL.width()) / 2,
                        (198 - self.imageTempPIL.height()) / 2,
                        image=self.imageTempPIL,
                        anchor="nw",
                    )
                else:
                    self.canvas_2.itemconfig(self.imageTemp, image=self.imageTempPIL)
                    self.canvas_2.coords(
                        self.imageTemp,
                        (352 - self.imageTempPIL.width()) / 2,
                        (198 - self.imageTempPIL.height()) / 2,
                    )

                self.TVlabelTempSize.set(f"{w}x{h}")

            self.template_matching()
        except Exception as e:
            logger.exception("Caught an error: ", exc_info=True)
            self.generatedCommand.set(f"Error: {e}")

    def template_matching(self) -> None:
        if self.image is None or self.imageTemp is None:
            return
        src = self.imageCV

        src_w = 1280
        src_h = 720

        if self.rect is not None:
            # Calculate the selected region coordinates
            logger.debug(
                f"{self.multiply=}, {self.left_top_y // 2 // self.multiply}, {self.right_bottom_y // 2 // self.multiply}, {self.left_top_x // 2 // self.multiply}, {self.right_bottom_x // 2 // self.multiply}"
            )
            src = src[
                int(self.left_top_y // 2 // self.multiply) : int(
                    self.right_bottom_y // 2 // self.multiply
                ),
                int(self.left_top_x // 2 // self.multiply) : int(
                    self.right_bottom_x // 2 // self.multiply
                ),
            ]
            src_w = self.right_bottom_x - self.left_top_x
            src_h = self.right_bottom_y - self.left_top_y

        _template = self.imageTempCV

        w, h = _template.shape[1], _template.shape[0]
        if w > src_w or h > src_h:
            self.generatedCommand.set(
                "Error: Your selection is smaller than the template image"
            )
            for _ in self.found:
                self.mainCanvas.delete(_)
            return

        method = cv2.TM_CCOEFF_NORMED
        res = cv2.matchTemplate(src, _template, method)

        positions = np.where(res >= self._threshold.get())
        scores = res[positions]
        _boxes = []
        for y, x in zip(*positions):
            _boxes.append(
                [
                    self.left_top_x + x,
                    self.left_top_y + y,
                    self.left_top_x + x + w - 1,
                    self.left_top_y + y + h - 1,
                ]
            )
        __boxes = np.array(_boxes)
        boxes: np.ndarray = self.non_max_suppression(
            __boxes, scores, overlap_thresh=0.8
        )

        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        self.matchAccuracy.set(round(max_val, 2))
        self.matchCoodinate.set(str(max_loc))

        for _ in self.found:
            self.mainCanvas.delete(_)

        self.found = []
        for i in range(min(128, box_n := len(boxes))):
            # self.debug(boxes[i])
            _h, _j, _n, _m = boxes[i]
            found_rect = self.mainCanvas.create_rectangle(
                int(_h * self.multiply),
                int(_j * self.multiply),
                int((_h + w) * self.multiply),
                int((_j + h) * self.multiply),
                outline="red",
                width=1,
            )
            self.found.append(found_rect)
        self.matchCount.set(box_n)

        self.convert()

    def convert(self) -> None:
        if isinstance(self.pathTempImage, str):
            with open(
                f"./cfg/command/{self.commandStyle.get()}", "r", encoding="utf-8"
            ) as file:
                data = file.read()
                data = data.replace(
                    "%TEMPPATH%",
                    f'"{str(os.path.relpath(self.pathTempImage, self.resourceRootPath))}"',
                )
                data = data.replace("%THRESHOLD%", str(self._threshold.get()))
                data = data.replace(
                    "%USE_GRAY%",
                    str(False)
                    if self.pixmap_mode == "Color"
                    else str(True)
                    if self.pixmap_mode == "Gray Scale"
                    else str(True),
                )
                data = data.replace("%SHOW_VALUE%", str(True))
                data = data.replace(
                    "%AREA%",
                    str(
                        [
                            self.left_top_x,
                            self.left_top_y,
                            self.right_bottom_x,
                            self.right_bottom_y,
                        ]
                    ),
                )
                data = data.replace("%TEMP_AREA%", str([]))
                self.generatedCommand.set(data)
            pass

    def saveRectArea(self) -> bool:
        try:
            img = self.imageCV[
                self.left_top_y : self.right_bottom_y,
                self.left_top_x : self.right_bottom_x,
            ]
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            result, n = cv2.imencode(".png", img)

            if result:
                # filename = "./screenshot/SS_" + datetime.now().strftime("%Y%m%d%H%M%S") + '.png'
                filename = filedialog.asksaveasfilename(
                    filetypes=[("PNG", ".png")], defaultextension="png"
                )
                if filename == "":
                    return False
                with open(filename, mode="w+b") as f:
                    n.tofile(f)
                # 保存したファイルをtemplateとして読み込むかユーザーに確認する
                res = messagebox.askyesno(
                    "Save as template",
                    f"{self.text_saveTemplate}\n{filename}",
                    parent=self.mainwindow,
                )
                if res:
                    self.pathTempImage = filename
                    self.changePreview()
                return True
            else:
                return False
        except Exception:
            logger.exception("Caught an error: ", exc_info=True)
        return False

    @staticmethod
    def get_latest_png_file(directory: pathlib.Path) -> str:
        # ディレクトリ内のすべての .png ファイルのリストを取得
        # list_of_files = glob.glob(os.path.join(directory, "*.png"))
        # if list_of_files == []:
        #     return ""
        # 最新のファイルを取得
        # latest_file = max(list_of_files, key=os.path.getctime)

        # in pathlib
        latest_file = max(directory.glob("*.png"), key=lambda f: f.stat().st_birthtime)
        if latest_file == "":
            return ""
        return str(latest_file)

    @staticmethod
    def get_cfg_files(directory: str) -> list[str]:
        # return [f for f in os.listdir(directory) if f.endswith(".cfg")]
        return [
            str(f.name) for f in pathlib.Path(directory).iterdir() if f.suffix == ".cfg"
        ]

    @staticmethod
    def non_max_suppression(
        boxes: np.ndarray, scores: np.ndarray, overlap_thresh: float
    ) -> np.ndarray[Any, Any]:
        """
        https://pystyle.info/opencv-non-maximum-suppression/ を参考にしました。
        Non Maximum Suppression (NMS) を行う。

        Args:
            scores: 画像認識の結果(一致率)
            boxes: (N, 4) の numpy 配列。矩形の一覧。
            overlap_thresh: [0, 1] の実数。閾値。

        Returns:
            boxes : (M, 4) の numpy 配列。Non Maximum Suppression処理後の矩形の一覧。
        """
        if len(boxes) <= 1:
            return boxes

        # float 型に変換する。
        boxes = boxes.astype("float")

        # (NumBoxes, 4) の numpy 配列を x1, y1, x2, y2 の一覧を表す4つの (NumBoxes, 1) の numpy 配列に分割する。
        x1, y1, x2, y2 = np.squeeze(np.split(boxes, 4, axis=1))

        # 矩形の面積を計算する。
        area = (x2 - x1 + 1) * (y2 - y1 + 1)

        indices = np.argsort(scores)  # スコアを降順にソートしたインデックス一覧
        selected = []  # NMS により選択されたインデックス一覧

        # indices がなくなるまでループする。
        while len(indices) > 0:
            # indices は降順にソートされているので、最後の要素の値 (インデックス) が
            # 残っている中で最もスコアが高い。
            last = len(indices) - 1

            selected_index = indices[last]
            remaining_indices = indices[:last]
            selected.append(selected_index)

            # 選択した短形と残りの短形の共通部分の x1, y1, x2, y2 を計算する。
            i_x1 = np.maximum(x1[selected_index], x1[remaining_indices])
            i_y1 = np.maximum(y1[selected_index], y1[remaining_indices])
            i_x2 = np.minimum(x2[selected_index], x2[remaining_indices])
            i_y2 = np.minimum(y2[selected_index], y2[remaining_indices])

            # 選択した短形と残りの短形の共通部分の幅及び高さを計算する。
            # 共通部分がない場合は、幅や高さは負の値になるので、その場合、幅や高さは 0 とする。
            i_w = np.maximum(0, i_x2 - i_x1 + 1)
            i_h = np.maximum(0, i_y2 - i_y1 + 1)

            # 選択した短形と残りの短形の Overlap Ratio を計算する。
            overlap = (i_w * i_h) / area[remaining_indices]

            # 選択した短形及び Overlap Ratio が閾値以上の短形を indices から削除する。
            indices = np.delete(
                indices, np.concatenate(([last], np.where(overlap > overlap_thresh)[0]))
            )

        # 選択された短形の一覧を返す。
        ret: np.ndarray = boxes[selected].astype(np.int32)
        return ret


if __name__ == "__main__":
    # ログファイルを保存するディレクトリ
    # log_dir = BASE_PATH + "/log" # os でのパス指定
    log_dir = BASE_PATH / "log"
    # ディレクトリが存在しない場合は作成
    # if not os.path.exists(log_dir):
    if not pathlib.Path(log_dir).exists():
        # os.makedirs(log_dir)
        pathlib.Path(log_dir).mkdir(parents=True, exist_ok=True)
    # logger.add(log_dir + "/log.log", rotation="1024 KB", retention=5)
    logger.add(log_dir / "log.log", rotation="1024 KB", retention=5)
    app = mainwindow()
    app.run()
