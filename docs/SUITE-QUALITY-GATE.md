# Codex 法律插件套件质量门槛

本市场的 12 个插件均提供内部 `quality-gate` 技能。它不是用户入口；高频实质技能在形成法律判断、外部草稿或不可逆动作建议前加载它，并继续适用各自 `PRACTICE.md` 的领域规则。

## 通用门槛

每个插件必须做到：

1. 读取本地实务画像，确认用户角色、适用法域、上报或监督路径。
2. 分离用户提供事实、已读取原文、推断与待核事项，不以缺失事实作确定结论。
3. 对法规、案例、登记状态和期限标注实际来源及必要的时效核验状态。
4. 对发送、签署、提交、发布、付款、立案、删除、安装或对外承诺等动作设置有权人员确认门槛。

## 代表性回归入口

| 插件 | 主入口 | 门槛重点 |
|---|---|---|
| `commercial-legal` | `commercial-legal:review` | 合同分类、代表方、公共部门权限与修改建议 |
| `corporate-legal` | `corporate-legal:tabular-review` | 原文溯源、交易阈值、交割/决议动作 |
| `employment-legal` | `employment-legal:termination-review` | 用工地口径、证据、解除后果 |
| `privacy-legal` | `privacy-legal:use-case-triage` | 处理角色、数据流、PIA 触发 |
| `product-legal` | `product-legal:launch-review` | PRD 事实、宣传证据、上线决定 |
| `regulatory-legal` | `regulatory-legal:reg-feed-watcher` | 生效规则与草案分离、官方来源 |
| `ai-governance-legal` | `ai-governance-legal:use-case-triage` | 系统事实、数据、正式审批边界 |
| `litigation-legal` | `litigation-legal:matter-intake` | 卷宗事实、期限、提交/送达 |
| `law-student` | `law-student:case-brief` | 原文引用、教学用途、学术诚信 |
| `legal-clinic` | `legal-clinic:client-intake` | 指导监督、当事人材料、期限 |
| `legal-builder-hub` | `legal-builder-hub:skills-qa` | 代码权限、法源时效、安装批准 |
| `ip-legal` | `ip-legal:infringement-triage` | 权利状态、初筛边界、发函/下架 |

## 版本与兼容

- `PRACTICE.md` 继续位于 `~/.codex/plugins/config/claude-for-legal-zh/<插件>/PRACTICE.md`。
- 已有用户画像无须迁移；技能在读取画像后叠加新的质量门槛。
- `.claude-plugin/` 文件仍为 legacy compatibility；Codex 以 `.codex-plugin/plugin.json` 和 repo-local marketplace 为准。
