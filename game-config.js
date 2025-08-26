// 游戏配置文件 - JavaScript格式
// 这个文件包含所有游戏角色、技能、行动卡和队伍效果的配置

window.GameConfig = {
    characters: {
        cafe: {
            name: "Cafe",
            display_name: "Cafe",
            max_hp: 15,
            description: "每回合第一次造成伤害时伤害加1",
            avatar: "https://q1.qlogo.cn/g?b=qq&nk=3074917151&s=100",
            skills: [
                {
                    name: "首击强化",
                    type: "passive",
                    trigger: "first_damage_dealt",
                    effect: "damage_bonus",
                    value: 1,
                    description: "每回合第一次造成伤害时伤害+1"
                }
            ]
        },
        xinhe: {
            name: "xinhe",
            display_name: "星河",
            max_hp: 15,
            description: "每回合不使用技能时抽取一个行动卡",
            avatar: "https://q1.qlogo.cn/g?b=qq&nk=1070754640&s=100",
            skills: [
                {
                    name: "静谧抽卡",
                    type: "passive",
                    trigger: "turn_end_no_skill",
                    effect: "draw_card",
                    value: 1,
                    description: "每回合不使用技能时抽取1张行动卡"
                }
            ]
        },
        yangguang: {
            name: "yangguang",
            display_name: "阳光",
            max_hp: 15,
            description: "对方回合没有使用攻击卡时，下回合额外抽取2张卡",
            avatar: "https://q1.qlogo.cn/g?b=qq&nk=1834437956&s=100",
            skills: [
                {
                    name: "和平奖励",
                    type: "passive",
                    trigger: "opponent_no_attack",
                    effect: "draw_card",
                    value: 2,
                    description: "对方上回合未使用攻击卡时，本回合额外抽取2张卡"
                }
            ]
        },
        liuli: {
            name: "liuli",
            display_name: "琉璃",
            max_hp: 15,
            description: "受到攻击时进行1-6随机判定，6时免疫并反击2点",
            avatar: "https://q1.qlogo.cn/g?b=qq&nk=3148403704&s=100",
            skills: [
                {
                    name: "幸运反击",
                    type: "passive",
                    trigger: "take_damage",
                    effect: "lucky_counter",
                    value: {
                        dice_range: [1, 6],
                        lucky_number: 6,
                        counter_damage: 2
                    },
                    description: "受到攻击时1-6随机判定，6时免疫攻击并反击2点伤害"
                }
            ]
        },
        jun: {
            name: "jun",
            display_name: "俊",
            max_hp: 15,
            description: "可以帮队友承受伤害（每回合一次），前两次伤害减1",
            avatar: "https://q1.qlogo.cn/g?b=qq&nk=1413599052&s=100",
            skills: [
                {
                    name: "护盾守护",
                    type: "passive",
                    trigger: "teammate_take_damage",
                    effect: "damage_redirect",
                    value: 1,
                    description: "可以代替队友承受伤害，每回合限一次"
                },
                {
                    name: "坚韧减伤",
                    type: "passive",
                    trigger: "take_damage",
                    effect: "damage_reduction",
                    value: {
                        max_times: 2,
                        reduction: 1
                    },
                    description: "每回合前两次受到的伤害减少1点"
                }
            ]
        }
    },

    action_cards: {
        attack: {
            name: "attack",
            display_name: "攻击",
            description: "减少对方3点生命值",
            target_type: "enemy",
            effect_type: "damage",
            base_value: 3,
            quantity: 10
        },
        heal: {
            name: "heal",
            display_name: "回血",
            description: "增加自身2点生命值",
            target_type: "ally",
            effect_type: "heal",
            base_value: 2,
            quantity: 10
        },
        defend: {
            name: "defense",
            display_name: "防御",
            description: "下一次受到伤害减少1点",
            target_type: "ally",
            effect_type: "defense",
            base_value: 1,
            quantity: 10
        }
    },

    team_effects: {
        jun_liuli: {
            name: "俊琉璃组合",
            characters: ["jun", "liuli"],
            effect: "first_attack_bonus",
            value: 1,
            description: "每回合第一次攻击伤害+1"
        },
        cafe_xinhe: {
            name: "Cafe星河组合",
            characters: ["cafe", "xinhe"],
            effect: "extra_draw",
            value: 2,
            description: "每回合额外抽取2张卡"
        },
        yangguang_liuli: {
            name: "阳光琉璃组合",
            characters: ["yangguang", "liuli"],
            effect: "first_damage_immunity",
            value: 1,
            description: "免除每回合第一次受到的伤害"
        }
    }
};
