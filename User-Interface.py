import Tkinter as tk
import multiprocessing
import detection

e = multiprocessing.Event()
p = None


def CallBackStart():
    global p
    p = multiprocessing.Process(target=detection.start_action, args=(e,))
    p.start()


def CallBackStop():
    global e,p
    e.set()
    p.join()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Gesture Controller")
    root.wm_attributes("-topmost",1)
    root.geometry("-100-100")
    stop = tk.Button(root, text="stop", command= CallBackStop)
    start = tk.Button(root, text="start", command = CallBackStart)
    start.pack()
    stop.pack()
    root.mainloop()
