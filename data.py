import sc2reader
from sc2reader import events

# 数据处理与清洗

def process_replay_data(replay):
    """处理回放数据，生成结构化JSON快照"""
    fps = replay.game_fps
    snapshot = {
        "timestamp": [],
        "player_state": {},
        "unit_events": [],
        "combat_events": [],
        "operation_patterns": []
    }

    # 玩家状态初始化
    for player in replay.players:
        snapshot["player_state"][player.name] = {
            "resources": {"minerals": [], "vespene": []},
            "population": {"current": [], "max": []},
            "tech_level": 0,
            "key_buildings": []
        }

    # 时间序列切片（15秒窗口）
    time_slices = [t for t in range(0, replay.length.seconds, 15)]

    # 填充数据快照
    for time_point in time_slices:
        frame = time_point * fps
        time_entry = {"time": time_point, "frame": frame}
        snapshot["timestamp"].append(time_entry)

        # 获取当前时间点状态
        for event in replay.events:
            if event.frame > frame:
                break

            # 资源状态处理
            if isinstance(event, sc2reader.events.tracker.PlayerStatsEvent):
                player = event.player.name
                snapshot["player_state"][player]["resources"]["minerals"].append({
                    "time": time_point, "value": event.minerals_current
                })
                # 处理瓦斯资源
                snapshot["player_state"][player]["resources"]["vespene"].append({
                    "time": time_point, "value": event.vespene_current
                })
                # 处理当前人口
                snapshot["player_state"][player]["population"]["current"].append({
                    "time": time_point, "value": event.food_used
                })
                # 处理最大人口
                snapshot["player_state"][player]["population"]["max"].append({
                    "time": time_point, "value": event.food_made
                })

            # 单位事件处理
            elif isinstance(event, sc2reader.events.tracker.UnitBornEvent):
                snapshot["unit_events"].append({
                    "time": time_point,
                    "player": event.unit.owner.name,
                    "unit_type": event.unit.name,
                    "event": "born"
                })

            # 作战事件处理
            elif isinstance(event, sc2reader.events.tracker.UnitDiedEvent):
                snapshot["combat_events"].append({
                    "time": time_point,
                    "location": (event.x, event.y),
                    "unit_type": event.unit.name,
                    "killer": event.killer.name if event.killer else None
                })

    operation_sequences = extract_operation_sequences(replay)
    ngram_patterns = analyze_with_ngram(operation_sequences, n=3)

    # 将操作模式转化为战术描述
    for player, patterns in ngram_patterns.items():
        for pattern, count in patterns.items():
            tactical_meaning = map_pattern_to_tactic(pattern)
            snapshot["operation_patterns"].append({
                "player": player,
                "pattern": pattern,
                "tactic": tactical_meaning,
                "count": count
            })

    return snapshot


def extract_operation_sequences(replay):
    """提取玩家操作序列"""
    operation_sequences = {}
    for player in replay.players:
        operation_sequences[player.name] = []

    for event in replay.events:
        if hasattr(event, 'player') and event.player:
            player_name = event.player.name
            # 识别不同类型的操作事件
            if isinstance(event, events.game.SelectionEvent):
                # 选择事件，记录选择的快捷键
                if event.control_group:
                    operation = f"ctrl+{event.control_group}"
                    operation_sequences[player_name].append(operation)
            elif isinstance(event, events.game.CommandEvent):
                # 命令事件，记录命令类型
                operation = event.name.lower()
                operation_sequences[player_name].append(operation)
            elif isinstance(event, events.game.CameraEvent):
                # 镜头移动事件
                operation = "camera_move"
                operation_sequences[player_name].append(operation)

    return operation_sequences


def analyze_with_ngram(sequences, n=3):
    """使用N-gram分析操作序列"""
    ngram_results = {}
    # 遍历每个玩家的操作序列
    for player, operations in sequences.items():
        ngram_counts = {}
        # 生成 N-gram
        for i in range(len(operations) - n + 1):
            ngram = tuple(operations[i:i + n])
            if ngram in ngram_counts:
                ngram_counts[ngram] += 1
            else:
                ngram_counts[ngram] = 1
        ngram_results[player] = ngram_counts
    return ngram_results


def map_pattern_to_tactic(pattern):
    """将操作模式映射为战术描述"""
    # 示例逻辑
    if "ctrl+1" in pattern and "a-move" in pattern:
        return "编队1主力部队推进"
    elif "rapid_scv_production" in pattern:
        return "经济优先策略"
    return "未识别战术"

