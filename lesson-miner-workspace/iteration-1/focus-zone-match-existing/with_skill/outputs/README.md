# Lesson-Miner Skill Test: Focus Zone + Existing Project

## Scenario Summary

**Context**: User is in the "专注区" (Focus Zone), NOT in a project directory
**User Input**: "做饭智能体又出问题了，飞书 webhook 调用返回 400 错误。更新 pitfalls。"
**Existing Projects**: 做饭智能体, web-content-extraction-practice, 标签智能体

## Workflow Execution

```
┌─────────────────────────────────────────────────────────────────┐
│  TRIGGER                                                        │
│  User says: "做饭智能体...更新 pitfalls"                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Context Detection                                      │
│  ─────────────────────────────────────                          │
│  Current directory: 00 专注区/                                   │
│  Detected: FOCUS ZONE                                           │
│  Action: Need to extract project from dialog                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Project Extraction                                     │
│  ─────────────────────────────────────                          │
│  Extracted keyword: "做饭智能体"                                 │
│  Match type: EXISTING PROJECT                                   │
│  Confidence: HIGH (exact match)                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: List Existing Projects                                 │
│  ─────────────────────────────────────                          │
│  1. 做饭智能体  ← MATCH                                         │
│  2. web-content-extraction-practice                             │
│  3. 标签智能体                                                  │
│  4. [新建项目]                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: User Confirmation Dialog                               │
│  ─────────────────────────────────────                          │
│                                                                 │
│  [lesson-miner] 检测到你在专注区。根据对话内容，你提到的项目    │
│                是：做饭智能体                                    │
│                                                                 │
│  已有项目列表:                                                  │
│    1. 做饭智能体                                                │
│    2. web-content-extraction-practice                           │
│    3. 标签智能体                                                │
│    4. [新建项目]                                                │
│                                                                 │
│  > 请选择项目 (1-4): 1                                          │
│  > 确认将卡点记录到 '做饭智能体'? (y/n): y                      │
│                                                                 │
│  Result: CONFIRMED                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: Interactive Lesson Capture                             │
│  ─────────────────────────────────────                          │
│  卡点标题: 飞书 webhook 调用返回 400 错误                       │
│  现象: 调用飞书 webhook 发送消息时返回 400 Bad Request          │
│  根因: webhook URL 中的 key 参数过期或被重置                   │
│  解决方案: 重新复制 webhook URL → 更新环境变量 → 重启服务      │
│  检测信号: 看到 webhook 调用返回 400，且消息未送达             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: Update PITFALLS.md                                     │
│  ─────────────────────────────────────                          │
│  Target: zh-CN/01 你的项目/做饭智能体/PITFALLS.md               │
│  Operation: APPEND                                              │
│  Content: New pitfall entry (313 characters)                    │
│  Status: SUCCESS                                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  RESULT                                                         │
│  ─────────────────────────────────────                          │
│  ✓ Document updated: PITFALLS.md                                │
│  ✓ Pitfalls recorded: 1                                         │
│  ✓ Project: 做饭智能体                                          │
│  ✓ Total time: ~2 minutes                                       │
└─────────────────────────────────────────────────────────────────┘
```

## Key Features Demonstrated

### 1. Location Awareness
- Skill correctly detected user is in focus zone (not project directory)
- Triggered focus zone workflow (extract from dialog)

### 2. Project Name Extraction
- Extracted "做饭智能体" from natural language input
- Matched against existing projects
- Found exact match

### 3. Interactive Confirmation
- Listed all 3 existing projects
- Highlighted matched project
- Requested explicit user confirmation
- Provided option to create new project

### 4. Structured Lesson Capture
- Captured 4 dimensions: phenomenon, root cause, solution, detection signal
- Used interactive Q&A format
- Timestamped entry

### 5. Document Management
- Appended to existing PITFALLS.md
- Maintained document structure
- Updated changelog

## Output Files

| File | Description |
|------|-------------|
| `simulation_state.json` | Complete state machine trace |
| `confirmation_dialog.txt` | User interaction transcript |
| `pitfalls_update_preview.md` | Generated PITFALLS.md content |
| `summary_report.txt` | Executive summary |

## Test Result: PASSED ✓

All workflow steps executed correctly:
- Context detection ✓
- Project extraction ✓
- Project listing ✓
- User confirmation ✓
- Interactive capture ✓
- Document update ✓
