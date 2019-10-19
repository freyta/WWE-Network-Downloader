from tkinter import *
import tkinter as tk
import wwe
import json, shlex
from subprocess import call, Popen, PIPE
import subprocess
import threading

def make_safe_filename(s):
    def safe_char(c):
        if c.isalnum():
            return c
        else:
            return "_"
    return "".join(safe_char(c) for c in s).rstrip("_")


class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.username = ""
        self.password = ""
        self.url = ""

    def download_thread(self):
        threading.Thread(target=self.download_video()).start()



    def download_video(self):

        url = self.url.get()
        if url is "":
            window.output.insert(END,"No URL found\n")
            return

        if self.username.get() is "":
            window.output.insert(END,"Please enter your username\n")
            return

        if self.password.get() is "":
            window.output.insert(END,"Please enter password\n")
            return

        account = wwe.wwe_network(self.username.get(),self.password.get())
        if 'https://watch.wwe.com/episode/' in url:
            url = url.replace('https://watch.wwe.com/episode/','')
        else:
            window.output.insert(END,"Unknown video URL.\nFormat required is \"https://watch.wwe.com/episode/Power-Pro-Wrestling-11585\"")
            return

        account.login()
        window.output.insert(END,"Logged in\n")
        window.update() #Update GUI

        # Get the video JSON which tells us the hls url link
        video_link = account.get_video_info(url)
        window.output.insert(END,"Got the video details\n")
        window.update() #Update GUI


        # Set the Filename
        if(self.filename.get() == "video.mp4"):
            title = make_safe_filename(video_link[1])
        else:
            title = self.filename.get()
        print(title)
        # Grab the m3u8
        stream_url = account.m3u8_stream(video_link[0])
        window.output.insert(END,"Grabbed the m3u8 file\n")
        window.update() #Update GUI

        # Print out the m3u8
        account.down(stream_url)

        cmd = "youtube-dl --verbose --hls-prefer-native --fixup never --add-header User-Agent:\"WWE/4.0.13 (Linux;Android 9) ExoPlayerLib/2.9.3\" \"{}\" -o {}.mp4".format(stream_url, title)
        args = shlex.split(cmd)
        #subprocess.call("youtube-dl --verbose --hls-prefer-native --fixup never --add-header User-Agent:\"WWE/4.0.13 (Linux;Android 9) ExoPlayerLib/2.9.3\" \"{}\" -o {}.mp4".format(stream_url, "Raw-102103"), shell=True)
        self.popen = subprocess.Popen(args, stdout=subprocess.PIPE, bufsize=1)

        lines_iterator = iter(self.popen.stdout.readline, b"")

        # poll() return None if the process has not terminated
        # otherwise poll() returns the process's exit code
        while self.popen.poll() is None:
            for line in lines_iterator:
                window.output.insert(END, line.decode("utf-8"))
                window.update() #Update GUI

    def build_widgets(self):
        # Text labels
        lbl_1 = Label(window, text="Email:")
        lbl_1.grid(row=0, column=0)

        lbl_2 = Label(window, text="Password:", padx=5)
        lbl_2.grid(row=1, column=0)
        lbl_3 = Label(window, text="URL:", padx=5, pady=30)
        lbl_3.grid(row=3, column=0)
        lbl_4 = Label(window, text="Filename:", padx=5)
        lbl_4.grid(row=2, column=0)


        # Input Fields
        self.username = Entry(self, width=30)
        self.username.grid(row=0, column=1)

        self.password = Entry(self, width=30, show="*")
        self.password.grid(row=1, column=1)

        self.filename = Entry(self, width=30)
        self.filename.insert(END,"video.mp4")
        self.filename.grid(row=2, column=1)

        self.url = Entry(self, width=70)
        self.url.insert(END,"https://watch.wwe.com/episode/Power-Pro-Wrestling-11585")
        self.url.grid(row=3, column=1, columnspan=2)

        self.output = Text(self, width=70, padx=5)
        self.output.grid(row=5, column=0, columnspan=3)

        download_btn = Button(window, text="Download!", pady= 15, padx= 15, command=self.download_thread)
        download_btn.grid(row=4, column=1)


if __name__ == "__main__":
    window = MainApp()
    window.title("WWE Network 2.0 Downloader")
    window.geometry('600x650')
    window.build_widgets()
    window.mainloop()
