from blessed import Terminal

def get_text_width(text):
    """获取文本在终端中的实际宽度（中文字符占两个位置）"""
    if not text:
        return 0
    
    width = 0
    i = 0
    while i < len(text):
        char = text[i]
        # 跳过ANSI颜色控制序列
        if char == '\x1b' and i + 1 < len(text) and text[i + 1] == '[':
            # 查找ANSI序列的结束
            j = i + 2
            while j < len(text) and text[j] not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz':
                j += 1
            i = j + 1  # 跳过整个ANSI序列
            continue
        
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
        i += 1
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
    
    print(header + term.normal)  # 确保颜色重置
    lines_used = 1
    
    # 显示角色信息，每个角色一行
    for idx, char in enumerate(player.characters):
        # 基本信息（优先级最高）
        status = term.red("倒下") if not char.is_alive else term.green("存活")
        basic_info = f"  {idx+1}. {char.name} [{char.current_hp}/{char.max_hp} HP] {status}"
        
        # 防御信息
        defense = f" (防:{char.defense_buff})" if char.defense_buff > 0 else ""
        
        # 行动槽状态（次优先级）
        action_status = ""
        if hasattr(char, 'action_slot_manager'):
            slot_status = char.get_action_slot_status()
            total_slots = slot_status['total_slots']
            used_slots = slot_status['used_slots']
            
            # 生成行动槽显示字符串
            slot_icons = []
            for i in range(total_slots):
                if not char.is_alive:
                    slot_icons.append(term.black('●'))
                elif i < used_slots:
                    slot_icons.append(term.red('●'))
                else:
                    slot_icons.append(term.green('○'))
            
            slot_display = ''.join(slot_icons)
            action_status = f" [{slot_display}{term.normal}]"
        
        # 电能状态（最高优先级，不能被截断）
        energy_status = ""
        if hasattr(char, 'energy_system'):
            energy_info = char.get_energy_status()
            current_energy = energy_info['current_energy']
            energy_limit = energy_info['energy_limit']
            generation_level = energy_info['generation_level']
            
            # 电能显示颜色
            if not char.is_alive:
                energy_color = term.black
            elif current_energy >= energy_limit * 0.7:
                energy_color = term.green
            elif current_energy >= energy_limit * 0.3:
                energy_color = term.yellow
            else:
                energy_color = term.red
            
            energy_text = f"电能:{current_energy}/{energy_limit}"
            if generation_level > 0:
                energy_text += f" Lv{generation_level}"
            
            energy_status = f" {energy_color(energy_text)}{term.normal}"
        
        # 智能组合信息，确保重要信息不被截断
        char_info = smart_combine_char_info(
            basic_info, defense, action_status, energy_status, width, term
        )
        
        print(char_info + term.normal)  # 确保每行结束后重置颜色
        lines_used += 1
    
    return lines_used

def smart_combine_char_info(basic_info, defense, action_status, energy_status, width, term):
    """智能组合角色信息，确保重要信息不被截断"""
    # 电能信息和行动槽是最重要的，必须保留
    essential_info = basic_info + energy_status + action_status
    essential_width = get_text_width(essential_info)
    
    # 如果基本信息 + 重要信息能放下
    if essential_width <= width:
        # 尝试加入防御信息
        full_info = basic_info + defense + action_status + energy_status
        if get_text_width(full_info) <= width:
            return full_info
        else:
            return essential_info
    else:
        # 空间不足，需要缩短角色名字
        # 先缩短角色名字
        parts = basic_info.split(' ')
        if len(parts) >= 3:  # 编号、名字、HP信息
            char_name = parts[1]
            if len(char_name) > 4:  # 如果名字过长，缩短为2个字符+..
                short_name = char_name[:2] + ".."
                shortened_basic = basic_info.replace(char_name, short_name)
                test_info = shortened_basic + energy_status + action_status
                if get_text_width(test_info) <= width:
                    return test_info
        
        # 如果还是太长，只保留最关键的信息
        # 优先保留电能和生命值信息
        return basic_info[:width-len(energy_status)-3] + ".." + energy_status

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
    """绘制选择列表，适应左右分栏布局，确保在角色属性下方显示"""
    if layout_info is None:
        # 回退到旧的定位方式
        start_y = max(3, term.height - len(options) - 5)
        max_width = term.width
    else:
        # 使用新的分栏布局，确保在角色属性下方
        needed_lines = len(options) + 4  # 选项 + 提示 + 空行 + 缓冲
        max_width = layout_info.get('main_width', term.width)
        
        # 算出角色信息区域的结束位置
        base_start_y = layout_info['used_lines'] + 2  # 在角色信息后留出2行缓冲
        
        # 检查是否会超出屏幕范围
        max_possible_y = term.height - needed_lines - 2  # 预留底部空间
        
        if base_start_y <= max_possible_y:
            # 有足够空间，在角色信息下方显示
            start_y = base_start_y
        else:
            # 空间不足，在中间位置显示，但不要覆盖角色信息
            start_y = min(base_start_y, max(layout_info['used_lines'] + 1, max_possible_y))
    
    # 绘制选择菜单（只在左侧区域）
    with term.location(y=start_y):
        print("\n" + prompt + term.normal)  # 重置颜色
        print()  # 空行
        
        for i, option in enumerate(options):
            # 截断过长的选项文本
            display_option = option
            if get_text_width(display_option) > max_width - 4:  # 预留空间给前缀
                display_option = option[:max_width-7] + "..."
            
            if i == selected_index:
                print(term.black_on_white(f"> {display_option}") + term.normal)
            else:
                print(f"  {display_option}" + term.normal)