import tkinter as tk
from window import GomokuWindow
from game import Gomoku
import sys


def main():
    # g = Gomoku()
    # g.play()
    root = tk.Tk()
    ex = GomokuWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()
