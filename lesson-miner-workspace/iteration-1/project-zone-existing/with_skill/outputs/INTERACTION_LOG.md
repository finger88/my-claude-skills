# lesson-miner 技能执行记录

## 场景设定
- **当前位置**: zh-CN/01 你的项目/做饭智能体/
- **已有状态**: PITFALLS.md 包含 2 个卡点
- **用户输入**: "刚才解决了一个飞书API字段格式的问题，返回的数据里有个字段应该是数组但实际是字符串。记录踩坑。"

---

## 执行流程

### Step 1: 触发检测
- **触发词匹配**: "记录踩坑" ✅
- **技能启动**: lesson-miner

### Step 2: 位置感知
```
[lesson-miner] 检测到你在项目区: 做饭智能体
             当前已有 PITFALLS.md，包含 2 个卡点
             确认在此项目记录？还是切换到其他项目？
             > 确认（当前项目）
```

### Step 3: 项目确认
- **当前项目**: 做饭智能体
- **项目类型**: 已有项目（追加模式）
- **用户确认**: ✅ 继续在此项目记录

### Step 4: 交互式录入（第3个卡点）

#### 4.1 现象捕获
```
[lesson-miner] 现象？
             > 调用飞书 API 获取数据后解析报错，预期是数组但实际返回字符串
```

#### 4.2 根因分析
```
[lesson-miner] 根因？
             > 飞书 API 文档声明字段类型为 array，但实际返回序列化后的 JSON 字符串
```

#### 4.3 解决方案
```
[lesson-miner] 解决方案？
             > 1. 接收字段后先判断类型
             > 2. 如果是字符串，使用 JSON.parse() 或 json.loads() 反序列化
             > 3. 添加类型容错处理，兼容两种格式
```

#### 4.4 检测信号
```
[lesson-miner] 检测信号？（如何快速识别这个问题）
             > 解析 API 响应时出现 "not iterable" / "has no attribute" 类错误 + 检查字段实际类型与文档不符
```

### Step 5: 录入确认
```
[lesson-miner] 录入信息预览：

             ### 3. 飞书 API 字段格式与文档不符（数组 vs 字符串）

             | 维度 | 内容 |
             |------|------|
             | **现象** | 调用飞书 API 获取数据后解析报错，预期是数组但实际返回字符串 |
             | **根因** | 飞书 API 文档声明字段类型为 array，但实际返回序列化后的 JSON 字符串 |
             | **解决方案** | 1. 接收字段后先判断类型<br>2. 如果是字符串，使用 JSON.parse() 或 json.loads() 反序列化<br>3. 添加类型容错处理，兼容两种格式 |
             | **检测信号** | 解析 API 响应时出现 "not iterable" / "has no attribute" 类错误 + 检查字段实际类型与文档不符 |

             确认追加到 PITFALLS.md？
             > 确认
```

### Step 6: 文档更新
- **操作**: 追加第3个卡点到 PITFALLS.md
- **更新内容**:
  - 添加卡点 #3
  - 更新最佳实践（添加 DO/DON'T 各2条）
  - 更新更新日志（添加 2025-03-25 条目）

### Step 7: 决策树更新
```
[lesson-miner] 是否更新决策树？
             > 是

[lesson-miner] 已生成新的决策树节点：

             看到 API 返回数据解析错误？
               ├─ 是 → 检查字段类型是否与文档一致（特别是数组 vs 字符串）
               └─ 否 → 继续判断...
```

### Step 8: 完成总结
```
[lesson-miner] 完成！
             - 已追加第3个卡点
             - 已更新决策树
             - 文档位置: zh-CN/01 你的项目/做饭智能体/PITFALLS.md
```

---

## 状态变化

### Before
- 卡点数量: 2
- 决策树节点: 2
- 最佳实践: 3 DO / 3 DON'T

### After
- 卡点数量: 3 ✅
- 决策树节点: 3 ✅
- 最佳实践: 5 DO / 5 DON'T ✅

---

## 文件输出

所有输出文件已保存至:
```
C:\Users\HONOR\.claude\skills\lesson-miner-workspace\iteration-1\project-zone-existing\with_skill\outputs\
```

文件清单:
1. PITFALLS_BEFORE.md - 更新前状态（2个卡点）
2. PITFALLS_AFTER.md - 更新后状态（3个卡点）
3. DECISION_TREE_UPDATE.md - 决策树变更记录
4. INTERACTION_LOG.md - 本交互执行记录
