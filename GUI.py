#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import (
    CTk,
    CTkButton,
    CTkCheckBox,
    CTkComboBox,
    CTkEntry,
    CTkFrame,
    CTkLabel,
    CTkRadioButton,
    CTkSlider,
    CTkCanvas,
    CTkToplevel)
from tkinterdnd2 import TkinterDnD, DND_ALL


class Tk(CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class GuiApp:
    def __init__(self, master=None):
        # build ui
        self.tmst = Tk(None)
        self.tmst.configure(relief="flat")
        self.tmst.resizable(False, False)
        self.tmst.title("Template Match Support Tool")
        self.mainFrame = CTkFrame(self.tmst)
        self.mainFrame.configure(height=360, width=640)
        self.canvasFrame = CTkFrame(self.mainFrame)
        self.canvasFrame.configure(fg_color="#000000", height=650, width=370)
        self.mainCanvas = tk.Canvas(self.canvasFrame)
        self.mainCanvas.configure(cursor="tcross", height=360, width=640)
        self.mainCanvas.grid(column=0, row=0)
        self.canvasFrame.grid(column=0, padx=10, pady=5, row=0, sticky="nsew")
        self.resultFrame = CTkFrame(self.mainFrame)
        self.resTh = CTkLabel(self.resultFrame)
        self.TVThreshold = tk.StringVar(value='Threshold')
        self.resTh.configure(text='Threshold', textvariable=self.TVThreshold)
        self.resTh.grid(column=0, padx=5, row=0, rowspan=2, sticky="ew")
        self.sbTh = ttk.Spinbox(self.resultFrame)
        self._threshold = tk.DoubleVar()
        self.sbTh.configure(
            from_=0,
            increment=0.01,
            textvariable=self._threshold,
            to=1,
            width=5)
        self.sbTh.grid(column=1, row=0, sticky="ew")
        self.labelCount = CTkLabel(self.resultFrame)
        self.TVcount = tk.StringVar(value='Count')
        self.labelCount.configure(text='Count', textvariable=self.TVcount)
        self.labelCount.grid(column=4, padx=5, row=0, sticky="ew")
        self.separator_1 = ttk.Separator(self.resultFrame)
        self.separator_1.configure(orient="horizontal")
        self.separator_1.grid(column=3, padx=5, row=0, sticky="nsew")
        self.entryCount = CTkEntry(self.resultFrame)
        self.matchCount = tk.IntVar()
        self.entryCount.configure(
            takefocus=False,
            textvariable=self.matchCount,
            width=75)
        self.entryCount.grid(column=5, row=0, sticky="ew")
        self.labelAccuracy = CTkLabel(self.resultFrame)
        self.TVAccuracy = tk.StringVar(value='Accuracy')
        self.labelAccuracy.configure(
            text='Accuracy', textvariable=self.TVAccuracy)
        self.labelAccuracy.grid(column=6, padx=5, row=0, sticky="ew")
        self.entryAccuracy = CTkEntry(self.resultFrame)
        self.matchAccuracy = tk.DoubleVar()
        self.entryAccuracy.configure(textvariable=self.matchAccuracy, width=75)
        self.entryAccuracy.grid(column=7, row=0, sticky="ew")
        self.labelCoodinate = CTkLabel(self.resultFrame)
        self.TVCoodinate = tk.StringVar(value='Coodinate')
        self.labelCoodinate.configure(
            text='Coodinate', textvariable=self.TVCoodinate)
        self.labelCoodinate.grid(column=8, padx=5, row=0, sticky="ew")
        self.entryCoodinate = CTkEntry(self.resultFrame)
        self.matchCoodinate = tk.StringVar()
        self.entryCoodinate.configure(
            textvariable=self.matchCoodinate, width=75)
        self.entryCoodinate.grid(column=9, row=0, sticky="ew")
        self.resultFrame.grid(column=0, pady=5, row=1, sticky="nsw")
        self.resultFrame.rowconfigure(0, weight=1)
        self.resultFrame.columnconfigure(0, weight=1)
        self.frameImgTemp = CTkFrame(self.mainFrame)
        self.loadFrame = CTkFrame(self.frameImgTemp)
        self.loadFrame.configure(width=640)
        self.openSetting = CTkButton(self.loadFrame, hover=True)
        self.TVopenSetting = tk.StringVar(value='Setting')
        self.openSetting.configure(
            text='Setting', textvariable=self.TVopenSetting)
        self.openSetting.grid(column=0, padx=5, row=0, sticky="nsew")
        self.getLatest = CTkButton(self.loadFrame, hover=True)
        self.TVgetLatest = tk.StringVar(value='Get Latest Image')
        self.getLatest.configure(
            text='Get Latest Image',
            textvariable=self.TVgetLatest)
        self.getLatest.grid(column=1, padx=5, row=0, sticky="nsew")
        self.saveSelectArea = CTkButton(self.loadFrame, hover=True)
        self.TVsaveSelectArea = tk.StringVar(value='Save Select Area')
        self.saveSelectArea.configure(
            text='Save Select Area',
            textvariable=self.TVsaveSelectArea)
        self.saveSelectArea.grid(column=3, padx=5, row=0, sticky="nsew")
        self.cbCommand = CTkComboBox(self.loadFrame)
        self.commandStyle = tk.StringVar()
        self.cbCommand.configure(variable=self.commandStyle)
        self.cbCommand.grid(column=4, row=0)
        self.loadFrame.grid(
            column=0,
            columnspan=2,
            pady=5,
            row=0,
            sticky="nsew")
        self.loadFrame.rowconfigure("all", weight=1)
        self.loadFrame.columnconfigure("all", weight=1)
        self.configFrame = CTkFrame(self.frameImgTemp)
        self.labelMode = CTkLabel(self.configFrame)
        self.TVlabelMode = tk.StringVar(value='Color Setting')
        self.labelMode.configure(
            state="disabled",
            takefocus=False,
            text='Color Setting',
            textvariable=self.TVlabelMode)
        self.labelMode.grid(column=0, columnspan=2, row=0, sticky="nsew")
        self.rbColor = CTkRadioButton(self.configFrame, value=0)
        self.colorMode = tk.IntVar(value=0)
        self.rbColor.configure(text='Color', variable=self.colorMode)
        self.rbColor.grid(
            column=0,
            columnspan=2,
            padx=5,
            pady=2,
            row=1,
            sticky="nsew")
        self.rbGray = CTkRadioButton(self.configFrame, value=1)
        self.rbGray.configure(text='Gray Scale', variable=self.colorMode)
        self.rbGray.grid(
            column=0,
            columnspan=2,
            padx=5,
            pady=2,
            row=2,
            sticky="nsew")
        self.rbBin = CTkRadioButton(self.configFrame, value=2)
        self.rbBin.configure(text='Binarization', variable=self.colorMode)
        self.rbBin.grid(
            column=0,
            columnspan=2,
            padx=5,
            pady=2,
            row=3,
            rowspan=3,
            sticky="nsew")
        self.cbAutoBin = CTkCheckBox(self.configFrame)
        self.useAutoOtsu = tk.BooleanVar()
        self.cbAutoBin.configure(text='Auto', variable=self.useAutoOtsu)
        self.cbAutoBin.grid(column=1, pady=2, row=3, sticky="e")
        self.sbBinary = ttk.Spinbox(self.configFrame)
        self._BinaryThreshold = tk.IntVar()
        self.sbBinary.configure(
            from_=0,
            increment=1,
            justify="center",
            textvariable=self._BinaryThreshold,
            to=255,
            width=15)
        self.sbBinary.grid(column=1, pady=2, row=4, sticky="e")
        self.sliderBinaryTh = CTkSlider(self.configFrame)
        self.sliderBinaryTh.configure(
            from_=0, to=255, variable=self._BinaryThreshold, width=100)
        self.sliderBinaryTh.grid(column=1, pady=2, row=5, sticky="e")
        self.configFrame.grid(column=0, columnspan=1, row=1, sticky="nsew")
        self.configFrame.grid_anchor("center")
        self.configFrame.rowconfigure(0, weight=1)
        self.configFrame.rowconfigure("all", weight=1)
        self.configFrame.columnconfigure(0, weight=1)
        self.configFrame.columnconfigure(1, weight=1)
        self.configFrame.columnconfigure("all", weight=1)
        self.imgTemp = CTkFrame(self.frameImgTemp)
        self.imgTemp.configure(height=198, width=352)
        self.canvas_2 = tk.Canvas(self.imgTemp)
        self.canvas_2.configure(height=198, width=352)
        self.canvas_2.grid(column=0, columnspan=2, row=0, sticky="nsew")
        self.loadTemplate = CTkButton(self.imgTemp, hover=True)
        self.TVloadTemplate = tk.StringVar(value='Load Template Image')
        self.loadTemplate.configure(
            text='Load Template Image',
            textvariable=self.TVloadTemplate,
            width=50)
        self.loadTemplate.grid(column=0, padx=5, row=1)
        self.labelTempSize = CTkLabel(self.imgTemp)
        self.TVlabelTempSize = tk.StringVar(value='Template is not set')
        self.labelTempSize.configure(
            text='Template is not set',
            textvariable=self.TVlabelTempSize)
        self.labelTempSize.grid(column=1, padx=10, row=1, sticky="ne")
        self.imgTemp.grid(column=1, columnspan=2, row=1, sticky="nsew")
        self.imgTemp.grid_anchor("e")
        self.frameImgTemp.grid(column=0, pady=5, row=2, sticky="nsew")
        self.frameImgTemp.grid_anchor("center")
        self.frameImgTemp.rowconfigure(0, weight=1)
        self.frameImgTemp.rowconfigure("all", weight=1)
        self.frameImgTemp.columnconfigure(0, weight=1)
        self.frameImgTemp.columnconfigure(1, weight=1)
        self.frameImgTemp.columnconfigure("all", weight=1)
        self.entryCommandShow = CTkEntry(self.mainFrame)
        self.generatedCommand = tk.StringVar(
            value='Command will be shown here')
        self.entryCommandShow.configure(
            justify="left",
            takefocus=False,
            textvariable=self.generatedCommand)
        _text_ = 'Command will be shown here'
        self.entryCommandShow.delete("0", "end")
        self.entryCommandShow.insert("0", _text_)
        self.entryCommandShow.grid(column=0, row=3, sticky="nsew")
        self.mainFrame.grid(column=0, row=0, sticky="nsew")
        self.mainFrame.rowconfigure("all", weight=1)
        self.mainFrame.columnconfigure("all", weight=1)

        # Main widget
        self.mainwindow = self.tmst


    def run(self):
        self.mainwindow.mainloop()



class initSetting:
    def __init__(self, master=None):
        # build ui
        self.ctktoplevel_1 = CTkToplevel(master)
        self.ctktoplevel_1.configure(width=500)
        self.ctktoplevel_1.resizable(False, False)
        self.ctktoplevel_1.title("Setting")
        self.labelSetting = CTkLabel(self.ctktoplevel_1)
        self.labelSetting.configure(text='Settings')
        self.labelSetting.grid(columnspan=3, row=0, sticky="nsew")
        self.labelImgDir = CTkLabel(self.ctktoplevel_1)
        self.labelImgDir.configure(text='Image Directory')
        self.labelImgDir.grid(column=0, row=1, sticky="nsew")
        self.entryImgDir = CTkEntry(self.ctktoplevel_1)
        self.pathImgDir = tk.StringVar()
        self.entryImgDir.configure(
            placeholder_text="Set the directory path.",
            takefocus=True,
            textvariable=self.pathImgDir,
            width=400)
        self.entryImgDir.grid(column=1, row=1, sticky="nsew")
        self.ButtonSetImgDir = CTkButton(self.ctktoplevel_1)
        self.ButtonSetImgDir.configure(text='...', width=30)
        self.ButtonSetImgDir.grid(column=2, row=1, sticky="nsew")
        self.labelRescRoot = CTkLabel(self.ctktoplevel_1)
        self.labelRescRoot.configure(text='Resource Root')
        self.labelRescRoot.grid(column=0, row=2)
        self.entryRescRoot = CTkEntry(self.ctktoplevel_1)
        self.pathRescRoot = tk.StringVar()
        self.entryRescRoot.configure(
            placeholder_text="Set the resource root path.",
            textvariable=self.pathRescRoot,
            width=400)
        self.entryRescRoot.grid(column=1, row=2, sticky="nsew")
        self.ButtonSetResourceRoot = CTkButton(self.ctktoplevel_1)
        self.ButtonSetResourceRoot.configure(text='...', width=30)
        self.ButtonSetResourceRoot.grid(column=2, row=2, sticky="nsew")
        self.labelLanguage = CTkLabel(self.ctktoplevel_1)
        self.TVlanguage = tk.StringVar(value='Language')
        self.labelLanguage.configure(
            text='Language', textvariable=self.TVlanguage)
        self.labelLanguage.grid(column=0, row=3)
        self.cbLanguage = CTkComboBox(self.ctktoplevel_1)
        self.lang = tk.StringVar()
        self.cbLanguage.configure(variable=self.lang)
        self.cbLanguage.grid(column=1, columnspan=2, row=3, sticky="nsew")
        self.buttonOK = CTkButton(self.ctktoplevel_1)
        self.buttonOK.configure(text='OK', width=50)
        self.buttonOK.grid(column=1, row=4)
        self.ctktoplevel_1.grid_anchor("center")
        self.ctktoplevel_1.columnconfigure(0, weight=1)
        self.ctktoplevel_1.columnconfigure(1, weight=2)
        self.ctktoplevel_1.columnconfigure(2, weight=1)

        # Main widget
        self.mainwindow = self.ctktoplevel_1

    def run(self):
        self.mainwindow.mainloop()

    def run(self):
        self.mainwindow.mainloop()

if __name__ == "__main__":
    app = initSetting()
    app.run()



if __name__ == "__main__":
    app = GuiApp()
    app.run()
