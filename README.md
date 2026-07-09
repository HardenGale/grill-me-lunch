# grill-me-lunch 🍜

> 用 grill-me 决策树逻辑帮你决定今天午饭吃什么，接入美团和大众点评，自动推荐并下单。
>
> 饭搭子可能会离职，但 AI 饭搭子永远不会。

## 安装

```bash
# 即将发布到 npm（开发中）
npx grill-me-lunch

# 当前：从 GitHub 直接使用
git clone https://github.com/HardenGale/grill-me-lunch.git ~/.claude/skills/grill-me-lunch
```

## 使用

在 Claude Code 中：

```
/lunch          # 开始午饭拷问
/lunch-boss     # 老板请客模式
/lunch-broke    # 月底吃土模式
/lunch-diet     # 减肥中
/lunch-date     # 约会模式
/lunch-solo     # 一人食
/lunch-team     # 团建模式
```

## 工作原理

1. **场景识别** — 根据命令切换预算/风格策略
2. **基础约束** — 预算、时间、堂食/外卖、天气
3. **偏好遍历** — 菜系 → 忌口 → 辣度 → 油度 → 碳水
4. **方案权衡** — 约束冲突时提供 2-3 个 Trade-off
5. **执行** — 调用美团/大众点评 API，返回 Top 3 推荐

## 平台接入

| 平台 | 状态 | 说明 |
|------|------|------|
| 美团外卖 | 🚧 对接中 | 需申请开放平台 API 权限 |
| 大众点评 | 🚧 对接中 | 需申请开放平台 API 权限 |
| 饿了么 | 📝 计划中 | v1.1 |
| 小红书 | 📝 计划中 | v1.1 探店笔记 |

## Roadmap

| 阶段 | 计划 | 状态 |
|------|------|------|
| v0.1 | 代码整理，上传 GitHub | 🚧 开发中 |
| v0.2 | 补全 API 对接文档 | 📝 待办 |
| v0.3 | 支持场景模式 | 📝 待办 |
| v1.0 | 发布 npm | 📝 待办 |

## License

MIT
