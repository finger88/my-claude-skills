# Skills 迭代计划

**创建日期**: 2026-03-04
**用途**: 记录 skills 生态系统的改进方向和待实施功能

---

## 📚 核心原则：Skill 层级结构

skill-manager 必须时刻谨记的指导原则：

### Skill 的核心构成要素

| 组成部分 | 功能描述 | 必要性 | 典型内容 |
|---------|---------|--------|---------|
| **SKILL.md** | 核心配置文件，包含元信息和指令 | 必需 | 技能名称、描述、触发条件、执行步骤 |
| **references/** | 参考资料文件夹 | 可选 | 品牌规范、平台要求、格式模板等 |
| **scripts/** | 可执行脚本文件夹 | 可选 | API调用代码、自动化工具脚本 |
| **assets/** | 资源文件文件夹 | 可选 | 图片素材、logo、模板文件 |

### 三层渐进式披露机制

```
┌─────────────────────────────────────────┐
│ 元信息层（始终加载）                      │
│ - 技能名称和描述                          │
│ - 作为AI识别技能的"目录"                  │
│ - 仅占用少量Token                         │
│ 示例：秋之创意：根据品牌风格生成促销海报   │
└─────────────────────────────────────────┘
              ↓ 触发时加载
┌─────────────────────────────────────────┐
│ 指令层（按需加载）                        │
│ - 仅当AI判断需要调用该技能时加载          │
│ - 包含具体执行步骤、品牌要求、输出格式     │
│ - 避免无关信息干扰                        │
└─────────────────────────────────────────┘
              ↓ 任务需要时加载
┌─────────────────────────────────────────┐
│ 资源层（条件加载）                        │
│ - references/（参考资料）                 │
│ - scripts/（脚本，仅执行不读取）          │
│ - assets/（资源文件）                     │
│ 关键优化：脚本文件仅执行不读取，节省Token │
└─────────────────────────────────────────┘
```

---

## 🎯 待实施迭代

### 1. 渐进式披露优化

**目标**: 将 skill-manager 按照三层渐进式披露机制进行重构

**当前问题**:
- SKILL.md 文件较大（9.6 KB），包含大量详细说明
- 所有功能详解都在指令层，Token 效率不高
- 未充分利用 references/ 目录实现资源层

**改进方向**:

**元信息层（SKILL.md frontmatter）**:
- 保持简洁的 name 和 description
- description 包含清晰的触发条件

**指令层（SKILL.md body）**:
- 只保留核心执行流程（< 150 行）
- 简要说明 6 个核心功能
- 快速参考表
- 指向 references/ 的链接

**资源层（references/）**:
- `references/functions/list.md` - 列出技能功能详解
- `references/functions/evaluate.md` - 评估技能功能详解
- `references/functions/optimize.md` - 优化技能功能详解
- `references/functions/backup.md` - 备份技能功能详解
- `references/functions/rollback.md` - 回退技能功能详解
- `references/functions/log.md` - 记录日志功能详解
- `references/best-practices.md` - Anthropic 最佳实践清单
- `references/templates.md` - 输出格式模板

**重构后结构**:
```
skill-manager/
├── SKILL.md                    # 元信息 + 简要指令（< 150 行）
└── references/
    ├── functions/              # 功能详解（资源层）
    │   ├── list.md
    │   ├── evaluate.md
    │   ├── optimize.md
    │   ├── backup.md
    │   ├── rollback.md
    │   └── log.md
    ├── best-practices.md       # 评估标准
    └── templates.md            # 输出模板
```

---

### 2. 记录文档格式优化

**目标**: 统一和优化生成的记录文档格式

**当前问题**:
- `skills修改日志.md` 格式不够统一
- 评估报告格式可能不一致
- 缺少清晰的视觉层次

**改进方向**:

**统一日志格式**:
```markdown
### 2026-03-04 10:00 | skill-name

| 项目 | 内容 |
|------|------|
| 修改类型 | 🔧 优化 / 🐛 修复 / ✨ 新增 / 📦 备份 |
| 影响范围 | SKILL.md, references/ |
| Token 变化 | 200 行 → 120 行 (-40%) |

**修改内容**:
- [x] 具体修改点 1
- [x] 具体修改点 2

**验证结果**: ✅ 全部通过 / ⚠️ 部分通过 / ❌ 失败
```

**统一评估报告格式**:
```markdown
## 📊 评估报告: skill-name

### 层级结构检查
| 层级 | 状态 | 说明 |
|------|------|------|
| 元信息层 | ✅ | name, description 完整 |
| 指令层 | ⚠️ | 150 行 → 建议拆分 |
| 资源层 | ❌ | 缺少 references/ |

### Token 效率分析
- SKILL.md: 200 行（建议 < 150）
- references/: 0 个文件（建议拆分）
- 优化潜力: 40% Token 可节省

### 改进建议
- [ ] P0: 拆分详细内容到 references/
- [ ] P1: 补充 "Use when..." 触发条件
- [ ] P2: 添加输出格式模板
```

---

### 3. 双备份机制：本地 + Git

**目标**: 建立本地备份和 Git 版本管理的双备份机制

**备份策略**:

#### 本地备份（现有机制）
- 位置: `D:\my tool\skills log\backups\`
- 格式: `YYYYMMDD-skill-name-vX.Y/`
- 用途: 快速回退、误操作恢复
- 触发: 每次修改前自动备份
- 保留: 按需清理旧备份

#### Git 版本管理（新增）
- 仓库: `my-claude-skills`
- 用途: 长期版本追踪、跨设备同步、分享协作
- 触发: 每次完成迭代后手动提交
- 保留: 永久保存所有版本历史

**Git 仓库结构**:
```
my-claude-skills/
├── README.md                    # 仓库说明
├── skills/                      # 所有 skills
│   ├── skill-manager/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── daily-review/
│   │   ├── SKILL.md
│   │   └── scripts/
│   ├── weekly-review/
│   └── ...
├── docs/                        # 文档
│   ├── skills评估与修改建议.md
│   ├── skills修改日志.md
│   └── skills迭代计划.md
└── .github/
    └── workflows/
        └── validate.yml         # 自动验证 SKILL.md 格式
```

**工作流程**:
```
修改 skill
    ↓
本地备份（自动）
    ↓
验证通过
    ↓
记录日志
    ↓
Git commit（手动）
    ↓
Git push 到 my-claude-skills
```

**同步脚本**（待实现）:
- `scripts/sync-to-git.sh` - 将本地 skills 同步到 Git repo
- `scripts/sync-from-git.sh` - 从 Git repo 恢复到本地
- `scripts/validate-skill.sh` - 验证 SKILL.md 格式

**版本管理策略**:
- 每个 skill 在 YAML frontmatter 中标注版本号
- 使用语义化版本号（v1.0.0, v1.1.0, v2.0.0）
- 重大更新使用 Git tag 标记
- 编写 CHANGELOG.md 记录变更历史

---

## 📅 实施优先级

| 优先级 | 迭代项 | 预计工作量 | 依赖 |
|--------|--------|-----------|------|
| P0 | 渐进式披露优化 | 2-3 小时 | 无 |
| P1 | 记录文档格式优化 | 1-2 小时 | 无 |
| P2 | Git 版本管理设置 | 2-3 小时 | 前两项完成后 |

**建议顺序**:
1. **渐进式披露优化** - 让 skill-manager 符合三层结构原则
2. **记录文档格式优化** - 统一输出格式，提升可读性
3. **Git 版本管理** - 建立长期管理机制，连接到 my-claude-skills 仓库

---

## 📝 实施检查清单

### 渐进式披露优化
- [x] 创建 references/ 目录结构
- [x] 拆分 6 个功能详解到独立文件
- [x] 精简 SKILL.md 到 < 150 行（实际 103 行，-65%）
- [x] 验证三层加载机制正常工作
- [x] 更新文档引用链接

### 记录文档格式优化（部分完成）
- [x] 设计统一的日志模板（已内嵌在 references/functions/log.md）
- [x] 设计统一的评估报告模板（已内嵌在 references/functions/evaluate.md）
- [ ] 更新现有日志格式（历史记录保持原样，新记录遵循模板）
- [ ] 添加视觉层次（表格、emoji）
- [ ] 编写格式规范文档
- **备注**: P2 实施时需验证日志记录功能可正常跑通

### Git 版本管理
- [x] 初始化 my-claude-skills 仓库结构
- [x] ~~编写同步脚本~~ → 改用 Junction 方案，无需同步脚本
- [x] 迁移所有 skills 到 Git（16 个 skills + docs/）
- [ ] 为每个 skill 添加版本号（后续逐步补充）
- [ ] 设置 GitHub Actions 验证（后续按需）
- [x] 编写 README 和使用说明
- [x] 首次 commit 和 push
- [x] Junction 迁移：16 个 skill 目录全部改为指向 Git 仓库的 Junction
- [x] 验证 Junction 读写正常（Claude Code + Git 均透明访问）

---

## 🎯 成功标准

**渐进式披露优化完成标志**:
- SKILL.md < 150 行
- references/ 包含所有详细内容
- Token 使用减少 40% 以上

**记录文档格式优化完成标志**:
- 所有日志使用统一格式
- 评估报告清晰易读
- 视觉层次分明

**Git 版本管理完成标志**:
- my-claude-skills 仓库正常运行
- ~~本地和 Git 双备份机制建立~~ → Junction 方案实现单一数据源
- ~~同步脚本可用~~ → Junction 无需同步
- 版本号和 CHANGELOG 规范

---

## 📌 备注

- 本文档随迭代进展持续更新
- 每次迭代完成后记录实施经验
- 遇到问题及时调整方案
- 保持与 Anthropic 最佳实践同步
