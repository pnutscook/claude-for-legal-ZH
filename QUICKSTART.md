# 快速入门

**60 秒**即可让 Codex 发现这套法律插件。

## 在 Codex 中安装

1. 克隆或下载本仓库到本地。

2. 在 Codex 配置中加入本地 marketplace。编辑 `~/.codex/config.toml`，加入：

   ```toml
   [marketplaces.claude-for-legal-zh-codex]
   source_type = "local"
   source = "/absolute/path/to/claude-for-legal-ZH"
   ```

   `source` 指向本仓库根目录；Codex 会读取其中的 `.agents/plugins/marketplace.json`。

3. 重启 Codex，在插件列表中安装你需要的插件，例如 `commercial-legal`、`privacy-legal` 或 `litigation-legal`。

4. 运行初始化设置。快速入门 2 分钟，完整设置 10-15 分钟。

   ```text
   commercial-legal:cold-start-interview
   ```

5. 连接法律检索工具。没有连接检索工具时，引用的法规和案例将被标注为“未验证”。本插件已预配置 yuandian（元典）MCP 连接器用于案例检索和法规检索；也可以手动配置其他中国法律检索工具。

每个插件在生成法律判断、对外草稿或具有法律后果的下一步建议前都会加载内部质量门槛：核对实践画像、区分事实与待核事项、标注实际来源，并把发送、签署、提交等动作留给有权人员确认。

## 我应该安装哪个插件？

| 你的角色 | 安装 | 首次命令 |
|---|---|---|
| 数据合规/隐私律师/DPO | `privacy-legal` | `privacy-legal:use-case-triage` |
| 商事/合同律师/法务（含服务、委托、评估或公共部门背景合同） | `commercial-legal` | `commercial-legal:review` |
| 公司/并购律师 | `corporate-legal` | `corporate-legal:diligence-issue-extraction` |
| 劳动法律师/HR 法务 | `employment-legal` | `employment-legal:wage-hour-qa` |
| 产品/业务法务 | `product-legal` | `product-legal:is-this-a-problem` |
| 知识产权律师/专利代理师 | `ip-legal` | `ip-legal:clearance` |
| 诉讼/仲裁律师（法务或律所） | `litigation-legal` | `litigation-legal:matter-intake` |
| 合规/监管法务 | `regulatory-legal` | `regulatory-legal:reg-feed-watcher` |
| AI 治理负责人 | `ai-governance-legal` | `ai-governance-legal:use-case-triage` |
| 法学院法律诊所指导老师 | `legal-clinic` | `legal-clinic:cold-start-interview` |
| 法学院学生/法考生 | `law-student` | `law-student:cold-start-interview` |
| 法律运营/寻找新技能 | `legal-builder-hub` | `legal-builder-hub:registry-browser` |

## 你安装的是什么

每个插件通过初始化面试了解你的实务方式，写入实践画像文件（`~/.codex/plugins/config/claude-for-legal-zh/<插件名>/PRACTICE.md`），每个技能都从中读取。画像属于你：可以直接编辑、重新运行设置，或让技能更新它。

**所有输出均为律师审查草稿。** 插件会标记其不确定的内容，按来源标注引用，并对不可逆操作设置门槛。律师审查、核实并承担责任。插件让审查更快，但不能替代审查。

## 旧 Claude 兼容

仓库保留 `.claude-plugin/` 作为 legacy compatibility。Codex 默认读取 `.agents/plugins/marketplace.json` 和各插件的 `.codex-plugin/plugin.json`。冷启动技能会在需要时自动迁移旧 Claude 画像到 Codex 的 `PRACTICE.md`。

## 遇到问题？

- **插件列表没有出现**：确认 `source` 指向仓库根目录，并重启 Codex。
- **提示“请先运行设置”**：先运行对应插件的 `cold-start-interview`。
- **引用标注为 `[需验证]`**：连接检索工具。没有连接时，每条引用都来自模型训练数据或本地参考材料，依赖前需要核实。
- **无法读取文件**：将文件放到当前工作区，或在请求中明确提供文件路径/文本内容。
- **插件不做某件事**：运行 `legal-builder-hub:related-skills-surfacer` 找更匹配的技能，或查看插件 README 中的“本插件不做什么”。
