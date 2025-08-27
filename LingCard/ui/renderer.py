from blessed import Terminal

def get_text_width(text):
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

def safe_center_text(term: Terminal, text):
    """安全的文本居中函数"""
    text_width = get_text_width(text)
    padding = max(0, (term.width - text_width) // 2)
    return ' ' * padding + text

def draw_board(term: Terminal, game_state):
    """在终端绘制整个游戏界面，采用左右分栏布局"""
    print(term.home + term.clear, end='', flush=True)
    
    # 计算布局参数
    term_width = term.width
    term_height = term.height
    log_width = max(30, term_width // 3)  # 右侧日志区域宽度，最小30字符
    main_width = term_width - log_width - 1  # 左侧主内容区域宽度
    
    current_line = 0
    
    # 顶部信息
    player = game_state.get_current_player()
    header_text = f"第 {game_state.current_round} 轮 - 玩家 {player.id} 的回合"
    
    # 绘制顶部标题（跨越整个宽度）
    print(safe_center_text(term, header_text))
    current_line += 1
    print("-" * term_width)
    current_line += 1
    print()  # 空行
    current_line += 1

    # 对手信息 (左侧)
    opponent = game_state.get_opponent_player()
    opponent_lines = draw_player_info_left(term, opponent, is_opponent=True, width=main_width, start_line=current_line)
    current_line += opponent_lines
    
    # 分隔线
    print("=" * main_width + "|" + "=" * log_width)
    current_line += 1
    print()
    current_line += 1
    
    # 我方信息 (左侧)
    my_lines = draw_player_info_left(term, player, is_opponent=False, width=main_width, start_line=current_line)
    current_line += my_lines
    
    # 绘制右侧日志区域
    draw_log_sidebar(term, game_state, log_width, term_width - log_width, term_height - 3)
    
    return {
        'used_lines': current_line,
        'available_lines': term_height - current_line,
        'term_height': term_height,
        'main_width': main_width,
        'log_width': log_width
    }

def draw_player_info_left(term: Terminal, player, is_opponent: bool, width: int, start_line: int):
    """绘制左侧玩家信息，返回占用的行数"""
    side = "对手" if is_opponent else "我方"
    header = f"{side} (玩家 {player.id}) - 手牌: {len(player.hand)} | 牌库: {len(player.deck)} | 弃牌堆: {len(player.discard_pile)}"
    
    # 截断过长的标题
    if get_text_width(header) > width:
        header = header[:width-3] + "..."
    
    print(header)
    lines_used = 1
    
    # 显示角色信息，每个角色一行
    for i, char in enumerate(player.characters):
        status = term.red("倒下") if not char.is_alive else term.green("存活")
        defense = f" (防:{char.defense_buff})" if char.defense_buff > 0 else ""
        
        # 显示行动槽状态
        action_status = ""
        if hasattr(char, 'action_slot') and char.is_alive:
            if char.action_slot.can_use():
                action_status = f" {term.yellow('✓可行动')}"
            else:
                action_status = f" {term.red('✗已行动')}"
        
        char_info = f"  {i+1}. {char.name} [{char.current_hp}/{char.max_hp} HP] {status}{defense}{action_status}"
        
        # 截断过长的角色信息
        if get_text_width(char_info) > width:
            char_info = char_info[:width-3] + "..."
        
        print(char_info)
        lines_used += 1
    
    return lines_used

def wrap_text(text: str, width: int) -> list:
    """将文本按指定宽度进行换行，考虑中文字符宽度"""
    if width <= 0:
        return [text]
    
    lines = []
    current_line = ""
    current_width = 0
    
    for char in text:
        char_width = 2 if ord(char) >= 0x4e00 and ord(char) <= 0x9fff else 1
        
        if current_width + char_width > width and current_line:
            lines.append(current_line)
            current_line = char
            current_width = char_width
        else:
            current_line += char
            current_width += char_width
    
    if current_line:
        lines.append(current_line)
    
    return lines if lines else [""]

def draw_log_sidebar(term: Terminal, game_state, log_width: int, log_x: int, max_height: int):
    """在右侧绘制游戏日志侧边栏"""
    # 日志区域标题
    log_title = "游戏日志"
    title_padding = max(0, (log_width - get_text_width(log_title)) // 2)
    
    with term.location(x=log_x, y=3):  # 从第4行开始
        print(" " * title_padding + log_title)
    
    with term.location(x=log_x, y=4):
        print("-" * log_width)
    
    # 计算可用的日志显示行数
    available_log_lines = max_height - 6  # 预留标题和分隔线空间
    
    if available_log_lines <= 0:
        return
    
    # 处理游戏日志，进行换行
    wrapped_logs = []
    for log_msg in game_state.log:
        # 为每条日志添加前缀
        prefixed_msg = f"> {log_msg}"
        # 按日志区域宽度进行换行
        wrapped_lines = wrap_text(prefixed_msg, log_width)
        wrapped_logs.extend(wrapped_lines)
    
    # 保留最新的日志
    if len(wrapped_logs) > available_log_lines:
        wrapped_logs = wrapped_logs[-available_log_lines:]
        # 如果日志被截断，在顶部显示提示
        total_original_logs = len(game_state.log)
        with term.location(x=log_x, y=5):
            hint = f"(显示最新 {len(wrapped_logs)} 行日志)"
            if get_text_width(hint) > log_width:
                hint = hint[:log_width-3] + "..."
            print(hint)
        start_y = 6
    else:
        start_y = 5
    
    # 绘制日志内容
    for i, log_line in enumerate(wrapped_logs):
        y_pos = start_y + i
        if y_pos < max_height:
            with term.location(x=log_x, y=y_pos):
                # 确保不超出日志区域宽度
                if get_text_width(log_line) > log_width:
                    log_line = log_line[:log_width-3] + "..."
                print(log_line)

def draw_selection(term: Terminal, prompt: str, options: list, selected_index: int, layout_info=None):
    """绘制选择列表，适应左右分栏布局"""
    if layout_info is None:
        # 回退到旧的定位方式
        start_y = max(3, term.height - len(options) - 5)
        max_width = term.width
    else:
        # 使用新的分栏布局
        needed_lines = len(options) + 3  # 选项 + 提示 + 空行
        available_lines = layout_info['available_lines']
        max_width = layout_info.get('main_width', term.width)
        
        if needed_lines <= available_lines:
            # 有足够空间，在底部显示
            start_y = layout_info['used_lines'] + 1
        else:
            # 空间不足，在中间显示
            start_y = max(5, (term.height - needed_lines) // 2)
    
    # 绘制选择菜单（只在左侧区域）
    with term.location(y=start_y):
        print("\n" + prompt)
        print()  # 空行
        
        for i, option in enumerate(options):
            # 截断过长的选项文本
            display_option = option
            if get_text_width(display_option) > max_width - 4:  # 预留空间给前缀
                display_option = option[:max_width-7] + "..."
            
            if i == selected_index:
                print(term.black_on_white(f"> {display_option}"))
            else:
                print(f"  {display_option}")