# LingCard/ui/tui.py
from blessed import Terminal
import time

class TUI:
    def __init__(self):
        self.term = Terminal()
        
    def clear_screen(self):
        """完全清理屏幕"""
        print(self.term.home + self.term.clear, end='', flush=True)
        
    def safe_print(self, text, x=None, y=None, end='\n'):
        """安全的打印函数，处理中文字符宽度问题"""
        if x is not None and y is not None:
            with self.term.location(x=x, y=y):
                print(text, end=end, flush=True)
        else:
            print(text, end=end, flush=True)
    
    def get_text_width(self, text):
        """获取文本在终端中的实际宽度（中文字符占两个位置）"""
        width = 0
        for char in text:
            # 中文字符、日文、韩文等东亚字符占两个宽度
            if ord(char) >= 0x4e00 and ord(char) <= 0x9fff:  # 中文汉字范围
                width += 2
            elif ord(char) >= 0x3400 and ord(char) <= 0x4dbf:  # 中文扩展A
                width += 2
            elif ord(char) >= 0x20000 and ord(char) <= 0x2a6df:  # 中文扩展B
                width += 2
            elif ord(char) >= 0xff00 and ord(char) <= 0xffef:  # 全角字符
                width += 2
            else:
                width += 1
        return width

    def select_from_list(self, prompt: str, options: list, game_state=None) -> int:
        """提供一个可交互的选择列表，返回选择的索引"""
        if not options: 
            return -1
        
        current_selection = 0
        with self.term.cbreak(), self.term.hidden_cursor():
            while True:
                # 完全清理屏幕
                self.clear_screen()
                
                if game_state:
                    from .renderer import draw_board, draw_selection
                    # 获取布局信息
                    layout_info = draw_board(self.term, game_state)
                    draw_selection(self.term, prompt, options, current_selection, layout_info)
                else:
                    # 简单模式：只显示选择列表
                    print(prompt)
                    print()  # 空行
                    
                    for i, option in enumerate(options):
                        if i == current_selection:
                            # 使用更明显的选中标记
                            self.safe_print(self.term.black_on_white(f"> {option}"))
                        else:
                            self.safe_print(f"  {option}")
                
                # 处理用户输入
                inp = self.term.inkey()
                if inp.code == self.term.KEY_UP:
                    current_selection = (current_selection - 1) % len(options)
                elif inp.code == self.term.KEY_DOWN:
                    current_selection = (current_selection + 1) % len(options)
                elif inp.code == self.term.KEY_ENTER:
                    return current_selection
                elif inp.name == "KEY_ESCAPE":
                    return -1  # 返回-1表示取消
    
    def show_message(self, message: str, duration: float = 2.0):
        """显示消息，自动居中并处理中文字符"""
        self.clear_screen()
        
        # 计算屏幕中心位置
        message_width = self.get_text_width(message)
        center_x = max(0, (self.term.width - message_width) // 2)
        center_y = self.term.height // 2
        
        self.safe_print(message, x=center_x, y=center_y)
        time.sleep(duration)

    def render_and_show_message(self, game_state, message: str, duration: float = 2.0):
        """先渲染游戏面板，再在底部显示消息（适应左右分栏布局）"""
        from .renderer import draw_board
        
        # 清理屏幕并绘制游戏面板
        self.clear_screen()
        layout_info = draw_board(self.term, game_state)
        
        # 在左侧区域显示消息
        message_width = self.get_text_width(message)
        main_width = layout_info.get('main_width', self.term.width)
        
        # 计算消息在左侧区域的居中位置
        center_x = max(0, (main_width - message_width) // 2)
        
        # 根据实际布局计算消息位置
        if layout_info['available_lines'] >= 2:
            # 有足够空间，在底部显示
            message_y = layout_info['used_lines'] + 1
        else:
            # 空间不足，在屏幕最底部显示
            message_y = max(0, self.term.height - 2)
        
        # 截断过长的消息
        if message_width > main_width:
            message = message[:main_width-3] + "..."
            center_x = 0
        
        self.safe_print(message, x=center_x, y=message_y)
        time.sleep(duration)
        
    def confirm(self, prompt: str) -> bool:
        choice = self.select_from_list(prompt, ["是", "否"])
        return choice == 0