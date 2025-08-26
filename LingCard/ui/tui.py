# LingCard/ui/tui.py
from blessed import Terminal

class TUI:
    def __init__(self):
        self.term = Terminal()

    def select_from_list(self, prompt: str, options: list, game_state=None) -> int:
        """提供一个可交互的选择列表，返回选择的索引"""
        if not options: return -1
        
        current_selection = 0
        with self.term.cbreak(), self.term.hidden_cursor():
            while True:
                if game_state:
                    from .renderer import draw_board, draw_selection
                    draw_board(self.term, game_state)
                    draw_selection(self.term, prompt, options, current_selection)
                else:
                    print(self.term.clear)
                    print(prompt)
                    for i, option in enumerate(options):
                        if i == current_selection: print(self.term.reverse(f"> {option}"))
                        else: print(f"  {option}")

                inp = self.term.inkey()
                if inp.code == self.term.KEY_UP:
                    current_selection = (current_selection - 1) % len(options)
                elif inp.code == self.term.KEY_DOWN:
                    current_selection = (current_selection + 1) % len(options)
                elif inp.code == self.term.KEY_ENTER:
                    return current_selection
                elif inp.name == "KEY_ESCAPE":
                    return -1 # 返回-1表示取消
    
    def show_message(self, message: str, duration: float = 2.0):
        print(self.term.clear)
        print(self.term.center(message))
        self.term.inkey(timeout=duration)

    # --- 新增方法 ---
    def render_and_show_message(self, game_state, message: str, duration: float = 2.0):
        """先渲染游戏面板，再在底部显示消息"""
        from .renderer import draw_board
        draw_board(self.term, game_state)
        
        # 在屏幕底部显示消息
        with self.term.location(y=self.term.height - 1):
             print(self.term.center(message))
        
        self.term.inkey(timeout=duration)
    # ----------------
        
    def confirm(self, prompt: str) -> bool:
        choice = self.select_from_list(prompt, ["是", "否"])
        return choice == 0