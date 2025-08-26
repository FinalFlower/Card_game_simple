from blessed import Terminal

def draw_board(term: Terminal, game_state):
    """在终端绘制整个游戏界面"""
    print(term.home + term.clear)
    
    # 顶部信息
    player = game_state.get_current_player()
    print(term.center(f"第 {game_state.current_round} 轮 - 玩家 {player.id} 的回合"))
    print("-" * term.width)

    # 对手信息 (顶部)
    opponent = game_state.get_opponent_player()
    draw_player_info(term, opponent, is_opponent=True)
    
    print("\n" + "=" * term.width + "\n")
    
    # 我方信息 (底部)
    draw_player_info(term, player, is_opponent=False)
    
    # 游戏日志
    print("-" * term.width)
    print("游戏日志:")
    for log_msg in game_state.log:
        print(f"> {log_msg}")

def draw_player_info(term: Terminal, player, is_opponent: bool):
    side = "对手" if is_opponent else "我方"
    print(f"{side} (玩家 {player.id}) - 手牌: {len(player.hand)} | 牌库: {len(player.deck)} | 弃牌堆: {len(player.discard_pile)}")
    
    char_displays = []
    for char in player.characters:
        status = term.red("倒下") if not char.is_alive else term.green("存活")
        defense = f"{term.blue(f' (防:{char.defense_buff})')}" if char.defense_buff > 0 else ""
        display = f"  {char.name} [{char.current_hp}/{char.max_hp} HP] {status}{defense}"
        char_displays.append(display)
    
    print(" | ".join(char_displays))

def draw_selection(term: Terminal, prompt: str, options: list, selected_index: int):
    """绘制一个选择列表"""
    print(term.move_y(term.height - len(options) - 2))
    print(prompt)
    for i, option in enumerate(options):
        if i == selected_index:
            print(term.black_on_white(f"> {option}"))
        else:
            print(f"  {option}")