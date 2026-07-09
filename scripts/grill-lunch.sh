#!/bin/bash
# ===========================================
# grill-me-lunch：AI 午饭决策引擎
# ===========================================
# 用法：./grill-lunch.sh [scene]
# 场景：boss | broke | diet | date | solo | team
# ===========================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# ---- 加载 .env ----
if [ -f "$PROJECT_DIR/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$PROJECT_DIR/.env"
  set +a
fi

# ---- 默认值 ----
SCENE="${1:-default}"
GRILL_LAT="${GRILL_LAT:-31.2304}"
GRILL_LNG="${GRILL_LNG:-121.4737}"
GRILL_CITY="${GRILL_CITY:-上海}"
MOCK_MODE="${GRILL_MOCK_MODE:-true}"

# ---- Python 选择 ----
if command -v python3 &>/dev/null; then
  PYTHON=python3
else
  PYTHON=python
fi

# ---- 颜色 ----
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ---- 头部 ----
echo ""
echo -e "${BOLD}🍜 grill-me-lunch${NC}"
echo "========================================="
echo ""

# ---- 场景预设 ----
case "$SCENE" in
  boss)
    echo -e "💼 ${BOLD}老板请客模式${NC} — 预算放开，推高端！"
    PRESET_BUDGET=200
    PRESET_MIN_RATING=4.5
    PRESET_PRIORITY="rating"
    ;;
  broke)
    echo -e "💸 ${BOLD}月底吃土模式${NC} — 极限省钱，吃饱就行！"
    PRESET_BUDGET=15
    PRESET_MIN_RATING=3.5
    PRESET_PRIORITY="price"
    ;;
  diet)
    echo -e "🥗 ${BOLD}减肥中${NC} — 低卡优先，管住嘴！"
    PRESET_BUDGET=50
    PRESET_MIN_RATING=4.0
    PRESET_PRIORITY="calories"
    ;;
  date)
    echo -e "💕 ${BOLD}约会模式${NC} — 氛围感拉满，避雷贴士已加载！"
    PRESET_BUDGET=150
    PRESET_MIN_RATING=4.5
    PRESET_PRIORITY="atmosphere"
    ;;
  solo)
    echo -e "🧍 ${BOLD}一人食${NC} — 自在最重要，小店也有惊喜！"
    PRESET_BUDGET=40
    PRESET_MIN_RATING=4.0
    PRESET_PRIORITY="solo_friendly"
    ;;
  team)
    echo -e "👥 ${BOLD}团建模式${NC} — 品类覆盖广，众口可调！"
    PRESET_BUDGET=80
    PRESET_MIN_RATING=4.0
    PRESET_PRIORITY="variety"
    ;;
  *)
    echo -e "🎯 ${BOLD}默认模式${NC} — 开始午饭拷问！"
    PRESET_BUDGET=40
    PRESET_MIN_RATING=4.0
    PRESET_PRIORITY="balanced"
    ;;
esac

echo ""
echo -e "${CYAN}--- 第一轮：基础约束 ---${NC}"

# 如果场景已预设预算，跳过基础问题
if [ "$SCENE" = "default" ]; then
  read -r -p "预算上限（元）[默认 40]：" BUDGET
  BUDGET="${BUDGET:-$PRESET_BUDGET}"
  read -r -p "可用时间（分钟）[默认 60]：" TIME
  TIME="${TIME:-60}"
  read -r -p "外卖还是堂食？[外卖/堂食，默认外卖]：" DINING
  DINING="${DINING:-外卖}"
  read -r -p "当前天气？[晴/雨/热/冷，默认晴]：" WEATHER
  WEATHER="${WEATHER:-晴}"
else
  BUDGET="$PRESET_BUDGET"
  TIME=60
  DINING="外卖"
  WEATHER="晴"
  echo "  预算: ¥${BUDGET} | 时间: ${TIME}min | ${DINING}"
fi

echo ""
echo -e "${CYAN}--- 第二轮：偏好遍历 ---${NC}"
read -r -p "想吃什么菜系？[中餐/日料/韩式/泰式/越式/西餐/沙拉/随便]：" CUISINE
CUISINE="${CUISINE:-随便}"
read -r -p "有忌口吗？[无/不吃辣/不吃海鲜/素食]：" AVOID
AVOID="${AVOID:-无}"
read -r -p "下午需要高强度脑力劳动吗？[是/否，默认否]：" BRAIN
BRAIN="${BRAIN:-否}"

echo ""
echo -e "${CYAN}--- 第三轮：方案权衡 ---${NC}"
echo "正在分析约束冲突..."

# 构建搜索关键词
if [ "$CUISINE" = "随便" ] || [ -z "$CUISINE" ]; then
  KEYWORD="午餐"
else
  KEYWORD="$CUISINE"
fi

# 智能调整
if [ "$WEATHER" = "热" ] && [ "$BRAIN" = "是" ]; then
  KEYWORD="$KEYWORD 凉面 酸辣"
  echo -e "  ${YELLOW}⚡ 高温 + 脑力劳动 → 排除重油和汤面，推荐凉面/酸辣${NC}"
elif [ "$BRAIN" = "是" ]; then
  KEYWORD="$KEYWORD 沙拉 高蛋白"
  echo -e "  ${YELLOW}⚡ 脑力劳动需求 → 优先低GI高蛋白${NC}"
elif [ "$WEATHER" = "热" ]; then
  KEYWORD="$KEYWORD 凉面 酸辣"
  echo -e "  ${YELLOW}⚡ 高温天气 → 推荐清爽开胃${NC}"
fi

if [ "$SCENE" = "diet" ]; then
  KEYWORD="沙拉 $KEYWORD 低卡"
fi

if [ "$AVOID" = "不吃辣" ]; then
  KEYWORD="$KEYWORD -辣 -麻辣 -川菜"
fi

echo ""
echo -e "${GREEN}--- 第四轮：执行 ---${NC}"
echo "  关键字: $KEYWORD"
echo "  预算: ¥$BUDGET | 评分 ≥$PRESET_MIN_RATING"
echo ""

# 并行调用美团和大众点评
echo "🍜 美团外卖推荐："
echo "-------------------"
$PYTHON "$SCRIPT_DIR/crawl-meituan.py" \
  "$KEYWORD" "$GRILL_LAT" "$GRILL_LNG" \
  "$BUDGET" "$PRESET_MIN_RATING" "$TIME" 2>&1 || echo "  ⚠️ 美团搜索失败"

echo ""
echo "📝 大众点评推荐："
echo "-------------------"
$PYTHON "$SCRIPT_DIR/crawl-dianping.py" \
  "$KEYWORD" "$GRILL_CITY" "$PRESET_MIN_RATING" 2>&1 || echo "  ⚠️ 点评搜索失败"

echo ""
echo "========================================="
echo -e "${GREEN}✅ 决策完成！上面就是今天的午饭推荐 🍜${NC}"
echo ""
echo "💡 快捷命令："
echo "   /lunch        — 默认模式"
echo "   /lunch-boss   — 老板请客"
echo "   /lunch-broke  — 月底吃土"
echo "   /lunch-diet   — 减肥中"
echo "   /lunch-date   — 约会"
echo "   /lunch-solo   — 一人食"
echo "   /lunch-team   — 团建"
