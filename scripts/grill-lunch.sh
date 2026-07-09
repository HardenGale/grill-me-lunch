#!/bin/bash
# grill-me-lunch 入口脚本
# 用法：./grill-lunch.sh [scene]
# 场景：boss | broke | diet | date | solo | team

SCENE="${1:-default}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🍜 grill-me-lunch | 场景: ${SCENE}"
echo "========================================="
echo ""
echo "正在加载决策引擎..."
echo ""

# 根据场景读取预设参数
case "$SCENE" in
  boss)
    echo "💼 老板请客模式 — 预算放开，推高端！"
    ;;
  broke)
    echo "💸 月底吃土模式 — 极限省钱，吃饱就行！"
    ;;
  diet)
    echo "🥗 减肥中 — 低卡优先，管住嘴！"
    ;;
  date)
    echo "💕 约会模式 — 氛围感拉满，避雷贴士已加载！"
    ;;
  solo)
    echo "🧍 一人食 — 自在最重要，小店也有惊喜！"
    ;;
  team)
    echo "👥 团建模式 — 品类覆盖广，众口可调！"
    ;;
  *)
    echo "🎯 默认模式 — 开始午饭拷问！"
    ;;
esac

echo ""
echo "--- 第一轮：基础约束 ---"
read -p "预算上限（元）：" BUDGET
read -p "可用时间（分钟）：" TIME
read -p "外卖还是堂食？[外卖/堂食]：" DINING_TYPE
read -p "当前天气：[晴/雨/热/冷]：" WEATHER

echo ""
echo "--- 第二轮：偏好遍历 ---"
read -p "想吃什么菜系？[中餐/日料/韩式/泰式/越式/西餐/随便]：" CUISINE
read -p "有忌口吗？[无/不吃辣/不吃海鲜/素食/其他]：" AVOID
read -p "辣度偏好？[不辣/微辣/中辣/重辣]：" SPICY
read -p "油度偏好？[清淡/适中/无所谓]：" OILY
read -p "下午需要高强度脑力劳动吗？[是/否]：" BRAIN_WORK

echo ""
echo "--- 第三轮：方案权衡 ---"
echo "正在分析约束冲突..."
echo ""

# 构建搜索关键词
if [ "$CUISINE" = "随便" ] || [ -z "$CUISINE" ]; then
  KEYWORD="午餐"
else
  KEYWORD="$CUISINE"
fi

# 根据天气和脑力劳动调整
if [ "$WEATHER" = "热" ] && [ "$BRAIN_WORK" = "是" ]; then
  KEYWORD="$KEYWORD 酸辣 低油"
  echo "⚡ 检测到【高温 + 脑力劳动】，已排除重油和汤面类"
elif [ "$BRAIN_WORK" = "是" ]; then
  KEYWORD="$KEYWORD 低GI"
  echo "⚡ 检测到【脑力劳动需求】，已优先低GI方案"
fi

echo ""
echo "--- 第四轮：执行 ---"
echo "🔍 正在搜索美团 + 大众点评..."
echo "   关键字: $KEYWORD"
echo "   预算: ¥$BUDGET"
echo "   时间: ${TIME}min"
echo ""

# 调用 Python 脚本搜索真实数据
if command -v python3 &> /dev/null; then
  PYTHON=python3
else
  PYTHON=python
fi

# 默认坐标（上海，可在配置中修改）
LAT="${GRILL_LAT:-31.2304}"
LNG="${GRILL_LNG:-121.4737}"
CITY="${GRILL_CITY:-上海}"

echo "🍜 推荐结果："
echo ""

# 并行调用美团和大众点评
$PYTHON "$SCRIPT_DIR/crawl-meituan.py" "$KEYWORD" "$LAT" "$LNG" "$BUDGET" "4.0" "$TIME" &
MEITUAN_PID=$!

$PYTHON "$SCRIPT_DIR/crawl-dianping.py" "$KEYWORD" "$CITY" "4.0" &
DIANPING_PID=$!

wait $MEITUAN_PID
wait $DIANPING_PID

echo ""
echo "========================================="
echo "✅ 决策完成。上面就是你的午饭推荐！"
echo "💡 下次直接运行 /lunch 或 /lunch-$SCENE"
