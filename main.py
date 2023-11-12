#!/usr/bin/python3
from datetime import datetime
from enum import Enum, auto
import glob
import os
import pathlib
import numpy as np
import pygubu
from GUI import GuiApp, initSetting
from PIL import ImageTk, Image
import cv2
from tkinterdnd2 import DND_FILES
from tkinter import filedialog

class ColorType(Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return count

    COLOR = 0
    GRAY = 1
    BINARY = 2

class mainwindow(GuiApp):
    def __init__(self, master=None):
        super().__init__()
        self.setting = initSetting(master=self.mainwindow)
        self.setting.mainwindow.title("Setting")
        self.setting.mainwindow.protocol("WM_DELETE_WINDOW", self.setting.mainwindow.withdraw)
        
        self.imageCV:cv2.Mat = None
        self.imageTempCV:cv2.Mat = None
        self.imagePIL:ImageTk.PhotoImage = None
        self.imageTempPIL:ImageTk.PhotoImage = None
        self.image:int = None
        self.imageTemp:int = None
        
        self.mainCanvas.drop_target_register(DND_FILES)
        self.mainCanvas.dnd_bind('<<Drop>>', self.loadImage)
        self.canvas_2.drop_target_register(DND_FILES)
        self.canvas_2.dnd_bind('<<Drop>>', self.loadTempImage)
        
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        
        self.left_top_x = 0
        self.right_bottom_x = 1280
        self.left_top_y = 0
        self.right_bottom_y = 720
        self.mainCanvas.bind("<Button-1>", self.on_button_press)
        self.mainCanvas.bind("<B1-Motion>", self.on_drag)
        self.mainCanvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.saveSelectArea.configure(command=self.saveRectArea)
        
        self._threshold.set(0.80)
        self._BinaryThreshold.set(128)
        self.rbColor.configure(command=self.img_color_setting)
        self.rbGray.configure(command=self.img_color_setting)
        self.rbBin.configure(command=self.img_color_setting)
        self.rectStart:list|None = None
        self.rectEnd:list|None = None
        self.aspectRatio = 16/9
        self.pathImage:str = None
        self.pathTempImage:str = None
        self.entryCommandShow.configure(state="readonly")
        
        commandGenerations:list = self.get_cfg_files("./cfg") # ["PokeCon.", "SWCon."]
        self.cbCommand.configure(values=commandGenerations)
        self.cbCommand.set(commandGenerations[0])
        self.found = []
        self._threshold.trace("w", self.callTemplateMatching)
        
        # self.openSetting.configure(command=self.)
        self.getLatest.configure(command=self.changePreview)
        self.cbAutoBin.configure(command=self.switchBinaryState)

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
        self.resourceRootPath:str = os.path.dirname(__file__)
        self.ImageDirectoryPath:str = os.path.dirname(__file__)
    
    def on_button_press(self, event):
        # delete all previous rectangles
        self.mainCanvas.delete("drawn_rectangle")
        # save mouse drag start position
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.mainCanvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='green',width=2,  tags="drawn_rectangle")

    def on_drag(self, event):
        # update rectangle as mouse is dragged
        # make sure coordinates do not go beyond canvas boundaries
        self.end_x = min(max(event.x, 0), 640)
        self.end_y = min(max(event.y, 0), 360)
        self.mainCanvas.coords(self.rect, self.start_x, self.start_y, self.end_x, self.end_y)

    def on_button_release(self, event):
        
        self.left_top_x = min(self.start_x, self.end_x) * 2
        self.right_bottom_x = max(self.start_x, self.end_x) * 2
        self.left_top_y = min(self.start_y, self.end_y) * 2
        self.right_bottom_y = max(self.start_y, self.end_y) * 2
        self.template_matching()
        pass
    
    def reshowSetting(self):
        self.setting.mainwindow.deiconify()
    
    def setImgDir(self):
        if self.ImageDirectoryPath == "":
            init_dir = os.path.abspath(os.path.dirname(__file__))
        else:
            init_dir = self.ImageDirectoryPath
        self.ImageDirectoryPath = filedialog.askdirectory(initialdir=init_dir)
        self.setting.pathImgDir.set(self.ImageDirectoryPath)
    
    def setResourceRoot(self):
        if self.resourceRootPath == "":
            init_dir = os.path.abspath(os.path.dirname(__file__))
        else:
            init_dir = self.resourceRootPath
        self.resourceRootPath = filedialog.askdirectory(initialdir=init_dir)
        self.setting.pathRescRoot.set(self.resourceRootPath)
    
    def applySetting(self):
        self.ImageDirectoryPath = self.setting.pathImgDir.get()
        self.resourceRootPath = self.setting.pathRescRoot.get()
        self.setting.mainwindow.withdraw()
    
    def callTemplateMatching(self, *event):
        self.template_matching()

    def getLatestPNG(self):
        if self.ImageDirectoryPath =="":
            print(f"Set Directory First.")
        else:
            _ = self.get_latest_png_file(self.ImageDirectoryPath)
            if _ == "":
                return
            else:
                self.pathImage = _
            self.changePreview()
            
    def loadTemplateImage(self):
        if self.resourceRootPath == "":
            init_dir = os.path.abspath(os.path.dirname(__file__))
        else:
            init_dir = self.resourceRootPath
        _ = filedialog.askopenfilename(initialdir=init_dir, filetypes=[("png","*.png")])
        if _ == "":
            return
        else:
            self.pathTempImage = _
        
        self.changePreview()
        

    def loadImage(self, event):
        _path:str = str(event.data)
        if _path.endswith(".png"):
            try:
                self.pathImage = _path
                self.changePreview()
                return True
            except Exception as e:
                print(e)
                return False
        
    def loadTempImage(self, event):
        _path:str = str(event.data)
        if _path.endswith(".png"):
            try:
                self.pathTempImage = _path
                self.changePreview()                
                return True
            except Exception as e:
                print(e)
                return False
    
    def switchBinaryState(self, *event):
        if self.useAutoOtsu.get():
            self.sbBinary.configure(state="disable")
            self.sliderBinaryTh.configure(state="disable")
        else:
            self.sbBinary.configure(state="normal")
            self.sliderBinaryTh.configure(state="normal")
            

    def run(self):
        self.setting.mainwindow.withdraw()
        self.mainwindow.mainloop()

    def img_color_setting(self):
        match ColorType(self.colorMode.get()):
            case ColorType.COLOR:
                self.colorMode.set(ColorType.COLOR.value)
                self.pixmap_mode = "Color"
                print("change to Color mode")
                self.cbAutoBin.configure(state="disable")
                self.sbBinary.configure(state="disable")
                self.sliderBinaryTh.configure(state="disable")
            case ColorType.GRAY:
                self.colorMode.set(ColorType.GRAY.value)
                self.pixmap_mode = "Gray Scale"
                print("change to Gray-scale mode")
                self.cbAutoBin.configure(state="disable")
                self.sbBinary.configure(state="disable")
                self.sliderBinaryTh.configure(state="disable")
            case ColorType.BINARY:
                self.colorMode.set(ColorType.BINARY.value)
                self.pixmap_mode = "Binarization"
                print("change to Binary mode")
                self.cbAutoBin.configure(state="normal")
                self.sbBinary.configure(state="normal")
                self.sliderBinaryTh.configure(state="normal")
        self.changePreview()

    def changePreview(self):
        if self.pathImage is None:
            updateImage = False
        else:
            updateImage = True
            _imageCV = cv2.imread(self.pathImage)
            
        if self.pathTempImage is None:
            updateTempImage = False
        else:            
            updateTempImage = True
            _imageTemp = cv2.imread(self.pathTempImage)
            
            
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
                    self.threshold, self.imageCV = cv2.threshold(self.imageCV, 0, 255, cv2.THRESH_OTSU)
                    self._BinaryThreshold.set(int(self.threshold))
                    self.imagePIL = Image.fromarray(self.imageCV)
                else:
                    self.threshold = self._BinaryThreshold.get()
                    self.threshold, self.imageCV = cv2.threshold(self.imageCV, self.threshold, 255, cv2.THRESH_BINARY)
                    self.imagePIL = Image.fromarray(self.imageCV)
            if updateTempImage:
                # template 
                # [TODO] Since the target and the template are different files, the threshold determined by Otsu's method may vary.
                self.imageTempCV = cv2.cvtColor(_imageTemp, cv2.COLOR_BGR2GRAY)
                if self.useAutoOtsu.get():
                    self.threshold, self.imageTempCV = cv2.threshold(self.imageTempCV, 0, 255, cv2.THRESH_OTSU)
                    self.imageTempPIL = Image.fromarray(self.imageTempCV)
                else:
                    self.threshold = self._BinaryThreshold.get()
                    self.threshold, self.imageTempCV = cv2.threshold(self.imageTempCV, self.threshold, 255, cv2.THRESH_BINARY)
                    self.imageTempPIL = Image.fromarray(self.imageTempCV)

        
        if updateImage:
            w = self.imagePIL.width
            h = self.imagePIL.height
            self.aspectRatio = w/h
            if self.aspectRatio > 16/9:
                multiply = 640/w
            else:
                multiply = 360/h
            self.imagePIL = self.imagePIL.resize((int(w*multiply),int(h*multiply)))
            
            self.imagePIL = ImageTk.PhotoImage(self.imagePIL)
            # print(self.imagePIL.width())
            
            
            # ラベルに画像を指定
            if self.image is None:
                self.image = self.mainCanvas.create_image(0,0,image=self.imagePIL, anchor="nw")
            else:
                self.mainCanvas.itemconfig(self.image, image=self.imagePIL)
            
        
        if updateTempImage:
            w = self.imageTempPIL.width
            h = self.imageTempPIL.height
            ar = w/h
            if ar > 16/9:
                multiply = 352/w
            else:
                multiply = 198/h
                
            
            self.imageTempPIL = self.imageTempPIL.resize((int(w*multiply),int(h*multiply)))            
            self.imageTempPIL = ImageTk.PhotoImage(self.imageTempPIL)
            
            if self.imageTemp is None:
                self.imageTemp = self.canvas_2.create_image((352-self.imageTempPIL.width())/2,
                                                            (198-self.imageTempPIL.height())/2,
                                                            image=self.imageTempPIL, anchor="nw")
            else:
                self.canvas_2.itemconfig(self.imageTemp, image=self.imageTempPIL)
                self.canvas_2.coords(self.imageTemp,
                                     (352-self.imageTempPIL.width())/2,
                                     (198-self.imageTempPIL.height())/2)
            
            
            self.TVlabelTempSize.set(f"{w}x{h}")

        self.template_matching()
    
    def template_matching(self):
        if self.image is None or self.imageTemp is None:
            return
        src = self.imageCV

        src_w = 1280
        src_h = 720
        
        if self.rect is not None:
            # Calculate the selected region coordinates
            src = src[self.left_top_y:self.right_bottom_y, self.left_top_x:self.right_bottom_x]
            src_w = self.right_bottom_x - self.left_top_x
            src_h = self.right_bottom_y - self.left_top_y
            

        _template = self.imageTempCV

        w, h = _template.shape[1], _template.shape[0]
        if w > src_w or h > src_h:
            print("テンプレート画像が選択範囲より大きいため画像認識できません")
            return

        method = cv2.TM_CCOEFF_NORMED
        res = cv2.matchTemplate(src, _template, method)

        positions = np.where(res >= self._threshold.get())
        scores = res[positions]
        boxes = []
        for y, x in zip(*positions):
            boxes.append([self.left_top_x + x, self.left_top_y + y,
                          self.left_top_x + x + w - 1, self.left_top_y + y + h - 1])
        boxes = np.array(boxes)
        boxes = self.non_max_suppression(boxes, scores, overlap_thresh=0.8)

        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        self.matchAccuracy.set(round(max_val, 2))
        self.matchCoodinate.set(str(max_loc))
        
        for _ in self.found:
            self.mainCanvas.delete(_)
            
        self.found = []
        for i in range(box_n := len(boxes)):
            # self.debug(boxes[i])
            _h, _j, _n, _m = boxes[i]
            found_rect = self.mainCanvas.create_rectangle(_h // 2, _j // 2, _h // 2 + w // 2, _j // 2 + h // 2, outline='red', width=1)
            self.found.append(found_rect)
        self.matchCount.set(box_n)
        
        self.convert()
        
    def convert(self):        
        with open(f"./cfg/{self.commandStyle.get()}", 'r') as file:
            data = file.read()
            data = data.replace("%TEMPPATH%", f'"{str(os.path.relpath(self.pathTempImage, self.resourceRootPath))}"')
            data = data.replace("%THRESHOLD%", str(self._threshold.get()))
            data = data.replace("%USE_GRAY%", str(False) if self.pixmap_mode== "Color" else str(True) if self.pixmap_mode== "Gray Scale" else str(True))
            data = data.replace("%SHOW_VALUE%", str(True))
            data = data.replace("%AREA%", str([self.left_top_x, self.left_top_y,self.right_bottom_x,self.right_bottom_y]))
            data = data.replace("%TEMP_AREA%", str([]))
            self.generatedCommand.set(data)
        pass
    
    def saveRectArea(self):
        try:
            img = self.imageCV[self.left_top_y:self.right_bottom_y, self.left_top_x:self.right_bottom_x]
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            result, n = cv2.imencode(".png", img)

            if result:
                filename = "./screenshot/SS_" + datetime.now().strftime("%Y%m%d%H%M%S") + '.png'
                with open(filename, mode="w+b") as f:
                    n.tofile(f)
                return True
            else:
                return False
        except Exception as e:
            print(e)
        return False        
    
    @staticmethod
    def get_latest_png_file(directory: str) -> str:
        # ディレクトリ内のすべての .png ファイルのリストを取得
        list_of_files = glob.glob(os.path.join(directory, '*.png')) 
        if list_of_files == []:
            return ""
        # 最新のファイルを取得
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file
    
    @staticmethod
    def get_cfg_files(directory):
        return [f for f in os.listdir(directory) if f.endswith('.cfg')]
    
    @staticmethod
    def non_max_suppression(boxes: np.ndarray, scores: np.ndarray, overlap_thresh: float) -> np.ndarray:
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
        return boxes[selected].astype("int")
    


if __name__ == "__main__":
    app = mainwindow()
    app.run()

