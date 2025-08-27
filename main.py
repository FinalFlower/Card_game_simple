# main.py
from LingCard.game_manager import GameManager

def main():
    """游戏主入口"""
    try:
        game_manager = GameManager()
        game_manager.run()
    except KeyboardInterrupt:
        print("\n\n感谢游玩，再见！")
    except Exception as e:
        # 在生产环境中，这里应该记录日志
        print(f"\n游戏遇到一个无法恢复的错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()  
    