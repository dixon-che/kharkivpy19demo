#!/usr/bin/env python3

import sys
import wx 
import datetime
import wx.lib.buttons as buttons
import os
import requests
import json
import pyinsane2


PROGRESSION_INDICATOR = ['|', '/', '-', '\\']

URL_SEND_CODE = "http://0.0.0.0/scanner_status/"


def send_code(code):
    response = requests.get(url=URL_SEND_CODE, data=code)


def scan():
    devices = pyinsane2.get_devices()

    if (len(devices) <= 0):
        wx.MessageBox('Scanner device not found', 'Error', wx.OK | wx.ICON_WARNING)
        sys.exit(1)

    device = devices[0]
    #pyinsane2.set_scanner_opt(device, 'source', ['Auto', 'FlatBed'])
    pyinsane2.set_scanner_opt(device, 'resolution', [300])
    try:
        pyinsane2.maximize_scan_area(device)
    except Exception as exc:
        print("Failed to maximize scan area: {}".format(exc))
    pyinsane2.set_scanner_opt(device, 'mode', ['Color'])
    scan_session = device.scan(multiple=False)

    try:
        i = -1
        while True:
            i += 1
            i %= len(PROGRESSION_INDICATOR)
            sys.stdout.write("\b%s" % PROGRESSION_INDICATOR[i])
            sys.stdout.flush()
            scan_session.scan.read()
    except EOFError:
        print("Scan compleated!")

    FOLDER = os.getcwd()
    FOLDER_SCAN = os.path.join(FOLDER, '..', 'ui')
    os.chdir(FOLDER_SCAN)
    img = scan_session.images[0]
    img.save("KharkivPy19.jpg", "JPEG")
    os.chdir(FOLDER)


class ScanerWindow(wx.Frame):

    def __init__(self, parent, title):
        super().__init__(parent, title=title, pos=(100, 100), style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        #wx.Frame.__init__(self, parent, title=title, pos=(100, 100), style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        button_scan = wx.Button(panel, label="Scan")
        button_scan.Bind(wx.EVT_BUTTON, self.onButton_scan)
        sizer.Add(button_scan, 0 , wx.EXPAND|wx.ALIGN_CENTER)        
                
        panel.SetSizer(sizer)
                
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.Show(True)
     
 
    def onButton_scan(self, event):
        pyinsane2.init()
        try:
            scan()
        finally:
            pyinsane2.exit()
        wx.MessageBox('Scan comleated', 'Ok!', wx.OK)
                
    def OnClose(self, event):
        #send_code({'code': 42})
        self.Destroy()

if __name__ == "__main__":
    app = wx.App(False)
    frame = ScanerWindow(None, "Скан")
    app.MainLoop()
