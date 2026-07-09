# grill-me-lunch 🍜

> 用 grill-me 决策树逻辑帮你决定今天午饭吃什么，接入美团和大众点评，自动推荐。
>
> 饭搭子可能会离职，但 AI 饭搭子永远不会。

## 快速体验

```bash
git clone https://github.com/HardenGale/grill-me-lunch.git
cd grill-me-lunch

# 直接测试（Mock 模式，无需 API 密钥）
python test.py

# 交互式推荐
bash scripts/grill-lunch.sh
```

## 安装为 Claude Code Skill

```bash
git clone https://github.com/HardenGale/grill-me-lunch.git ~/.claude/skills/grill-me-lunch
```

## 场景模式

| 命令 | 场景 | 策略 |
|------|------|------|
| `bash scripts/grill-lunch.sh` | 默认模式 | 交互式拷问，预算 ¥40 |
| `bash scripts/grill-lunch.sh boss` | 老板请客 | 预算 ¥200，推高端 |
| `bash scripts/grill-lunch.sh broke` | 月底吃土 | 预算 ¥15，极限省钱 |
| `bash scripts/grill-lunch.sh diet` | 减肥中 | 低卡优先 |
| `bash scripts/grill-lunch.sh date` | 约会 | 氛围感，避雷优先 |
| `bash scripts/grill-lunch.sh solo` | 一人食 | 独食友好 |
| `bash scripts/grill-lunch.sh team` | 团建 | 品类覆盖广 |

## 工作原理

```
场景识别 → 基础约束（预算/时间/天气）→ 偏好遍历（菜系/忌口/辣度/油度）
→ 方案权衡（约束冲突时 2-3 个 Trade-off）→ 执行（美团 + 大众点评双源搜索）
```

## 配置真实 API（可选）

编辑 `.env` 文件填入密钥：

```bash
# 美团开发者平台 (developer.meituan.com)
MEITUAN_DEVELOPER_ID=你的开发者ID
MEITUAN_SIGN_KEY=你的签名密钥

# 大众点评开放平台 (open.dianping.com)
DIANPING_API_KEY=你的API密钥

# 关闭 Mock 模式
GRILL_MOCK_MODE=false
```

未配置密钥时自动使用高质量 Mock 数据，功能完全可用。

## 项目结构

```
grill-me-lunch/
├── SKILL.md                    # Claude Code Skill 核心指令
├── scripts/
│   ├── grill-lunch.sh          # 主入口（交互式午饭决策）
│   ├── crawl-meituan.py        # 美团搜索（真实 API + Mock）
│   ├── crawl-dianping.py       # 大众点评搜索（真实 API + Mock）
│   └── reminder.sh             # 工作日 11:50 提醒
├── config/
│   ├── food-rules.yaml         # 饮食规则引擎
│   └── scene-presets.yaml      # 6 个场景预设
├── test.py                     # 功能测试
└── .env                        # API 密钥配置
```

## Roadmap

| 阶段 | 计划 | 状态 |
|------|------|------|
| v0.1 | 决策引擎 + Mock 搜索 + 6 场景模式 | ✅ 完成 |
| v0.2 | 接入美团开放平台真实 API | 🚧 对接中 |
| v0.3 | 接入大众点评真实 API | 🚧 对接中 |
| v1.0 | 发布到 npm：`npx grill-me-lunch` | 📝 待办 |
| v1.1 | 饿了么 + 小红书探店 | 📝 待办 |

## License

MIT
