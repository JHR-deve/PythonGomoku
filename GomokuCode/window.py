import tkinter as tk
from tkinter import messagebox
import traceback
from game import Gomoku


def run_with_exc(f):
    """游戏运行出现错误时，用messagebox把错误信息显示出来"""

    def call(window, *args, **kwargs):
        try:
            return f(window, *args, **kwargs)
        except Exception:
            exc_info = traceback.format_exc()
            messagebox.showerror('错误信息', exc_info)
    return call


class GomokuWindow:

    def __init__(self, root):
        self.root = root
        self.init_ui()  # 初始化游戏界面
        self.g = Gomoku()  # 初始化游戏内容

        self.last_pos = (-1, -1)
        self.res = 0  # 记录那边获得了胜利
        self.operate_status = 0  # 游戏操作状态。0为游戏中（可操作），1为游戏结束闪烁过程中（不可操作）
        self.flash_cnt = 0  # 游戏结束之前闪烁了多少次
        self.flash_pieces = ((-1, -1), )  # 哪些棋子需要闪烁

    def init_ui(self):
        """初始化游戏界面"""
        # 1. 确定游戏界面的标题和大小
        self.root.title('五子棋')
        self.root.geometry('650x650')
        self.root.resizable(False, False)
        
        # 2. 创建画布
        self.canvas = tk.Canvas(self.root, width=650, height=650, bg='#D2B48C')
        self.canvas.pack()
        
        # 3. 绑定鼠标事件
        self.canvas.bind('<Motion>', self.mouse_move_event)
        self.canvas.bind('<Button-1>', self.mouse_press_event)
        
        # 4. 绘制初始棋盘
        self.draw_board()

    def draw_board(self):
        """绘制棋盘和棋子"""
        self.canvas.delete('all')  # 清空画布
        
        # 绘制棋盘线
        for x in range(15):
            self.canvas.create_line(40 * (x + 1), 40, 40 * (x + 1), 600, width=2)
        for y in range(15):
            self.canvas.create_line(40, 40 * (y + 1), 600, 40 * (y + 1), width=2)
        
        # 绘制棋盘中的黑点
        key_points = [(4, 4), (12, 4), (4, 12), (12, 12), (8, 8)]
        for t in key_points:
            self.canvas.create_oval(40 * t[0] - 5, 40 * t[1] - 5, 
                                   40 * t[0] + 5, 40 * t[1] + 5, fill='black')
        
        # 绘制棋子
        if hasattr(self, 'g'):
            for x in range(15):
                for y in range(15):
                    if self.g.g_map[x][y] == 1:  # 黑棋
                        if self.flash_cnt % 2 == 1 and (x, y) in self.flash_pieces:
                            continue
                        self.canvas.create_oval(40 * (x + 1) - 15, 40 * (y + 1) - 15,
                                              40 * (x + 1) + 15, 40 * (y + 1) + 15,
                                              fill='black', outline='gray')
                    elif self.g.g_map[x][y] == 2:  # 白棋
                        if self.flash_cnt % 2 == 1 and (x, y) in self.flash_pieces:
                            continue
                        self.canvas.create_oval(40 * (x + 1) - 15, 40 * (y + 1) - 15,
                                              40 * (x + 1) + 15, 40 * (y + 1) + 15,
                                              fill='white', outline='gray')

    @run_with_exc
    def mouse_move_event(self, event):
        """鼠标移动事件"""
        mouse_x = event.x
        mouse_y = event.y
        
        if 25 <= mouse_x <= 615 and 25 <= mouse_y <= 615 and \
           (mouse_x % 40 <= 15 or mouse_x % 40 >= 25) and \
           (mouse_y % 40 <= 15 or mouse_y % 40 >= 25):
            game_x = int((mouse_x + 15) // 40) - 1
            game_y = int((mouse_y + 15) // 40) - 1
            self.canvas.config(cursor='hand2')
        else:
            game_x = -1
            game_y = -1
            self.canvas.config(cursor='')
        
        self.last_pos = (game_x, game_y)

    @run_with_exc
    def mouse_press_event(self, event):
        """鼠标点击事件"""
        if not (hasattr(self, 'operate_status') and self.operate_status == 0):
            return
        
        mouse_x = event.x
        mouse_y = event.y
        
        if (mouse_x % 40 <= 15 or mouse_x % 40 >= 25) and \
           (mouse_y % 40 <= 15 or mouse_y % 40 >= 25):
            game_x = int((mouse_x + 15) // 40) - 1
            game_y = int((mouse_y + 15) // 40) - 1
        else:
            return
        
        self.g.move_1step(True, game_x, game_y)
        
        # 判断游戏结果
        res, self.flash_pieces = self.g.game_result(show=True)
        if res != 0:
            self.draw_board()
            self.game_restart(res)
            return
        
        # 电脑下一步
        self.g.ai_play_1step()
        res, self.flash_pieces = self.g.game_result(show=True)
        if res != 0:
            self.draw_board()
            self.game_restart(res)
            return
        
        self.draw_board()

    @run_with_exc
    def end_flash(self):
        """游戏结束时的闪烁操作"""
        if self.flash_cnt <= 5:
            self.flash_cnt += 1
            self.draw_board()
            self.root.after(300, self.end_flash)
        else:
            # 显示游戏结束的信息
            if self.res == 1:
                messagebox.showinfo('游戏结束', '玩家获胜!')
            elif self.res == 2:
                messagebox.showinfo('游戏结束', '电脑获胜!')
            elif self.res == 3:
                messagebox.showinfo('游戏结束', '平局!')
            
            # 游戏重新开始
            self.res = 0
            self.operate_status = 0
            self.flash_cnt = 0
            self.g = Gomoku()
            self.draw_board()

    def game_restart(self, res):
        """游戏结束"""
        self.res = res
        self.operate_status = 1
        self.end_flash()
