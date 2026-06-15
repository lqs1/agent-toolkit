---
name: redteam-debate
description: Multi-round adversarial red-team vs blue-team debate skill. Use when asked to "red team", "devil's advocate", "debate", "evaluate", "assess", "critique", "对抗", "辩论", "评估", "红队", "挑毛病", or to stress-test an idea, plan, code, strategy, or decision. Orchestrates structured rounds of criticism and rebuttal with persistent state and continuation support.
allowed-tools: Read, Bash, Write, Edit
---

# 红队-蓝队-绿队 对抗辩论 Skill

通过结构化多轮对抗辩论，深度评估任何方案/想法/代码/策略。红队专门挑刺，蓝队逐条反驳，绿队最终出务实结论。支持状态保存和随时续轮。

## 核心流程

```
用户提出议题 → 红队首轮挑刺 → 蓝队逐条反驳 → 逐轮深入 → 绿队出结论 → 保存状态
                    ↑________________________________________________↓
                                            （可随时续轮）
```

## 三队角色

### 红队（Red Team）— 魔鬼代言人
- **使命**：从一切可能的角度找问题、挑毛病、找风险
- **视角**：技术可行性、成本、时间、安全、维护、用户体验、竞争、法律合规、团队能力
- **原则**：每个观点必须有**实际依据**，禁止空洞批评。要从用户场景、数据、先例出发
- **输出格式**：编号列表，每条包含「问题描述 + 为什么是个问题（基于实际）」

### 蓝队（Blue Team）— 辩护者
- **使命**：针对红队的每一条批评，给出最有力的反驳
- **视角**：已有方案、替代路径、风险可控性、收益足够大、先例成功
- **原则**：反驳必须**具体**，不能只说"不对"。要引用实际案例、数据、或提出可行规避方案
- **输出格式**：逐条对应红队编号，「反驳 + 实际支撑」

### 绿队（Green Team）— 务实评估
- **使命**：辩论结束后，给出最终是否可用、怎么修改的结论
- **视角**：落地成本 vs 收益、可执行性、优先级
- **输出**：
  - 可用 / 谨慎可用 / 不可用
  - 必须修改的点（按优先级排序）
  - 建议的下一步行动

## 执行步骤

### 1. 初始化辩论

当用户提出评估请求时：

1. 询问用户要进行多少轮（默认 2 轮，可随时调整）
2. 确认议题的具体内容（如果是代码/文件，先 Read 了解全貌）
3. 创建 debate state：
   ```bash
   python -c "
   import sys; sys.path.insert(0, '/Users/qslu/.claude/skills/redteam-debate')
   from debate_state import DebateState
   state = DebateState(topic='用户议题', max_rounds=5)
   print(state.save())
   "
   ```
4. 输出议题确认 + 辩论结构说明

### 2. 每轮辩论格式

每轮必须按以下结构输出：

```markdown
## 第 N 轮

### 红队 — 负面因素

1. **[类别]** 具体问题描述
   - 为什么是个问题：...
   - 实际影响：...

2. **[类别]** ...

### 蓝队 — 逐条反驳

1. **对应红队 #1**：反驳内容
   - 实际支撑/案例：...
   - 或者规避方案：...

2. **对应红队 #2**：...

### 本轮摘要
- 红队新提出 X 条问题
- 蓝队成功反驳 Y 条 / 未完全回应 Z 条
- 关键分歧点：...
```

### 3. 状态保存

**每轮结束后保存状态：**

使用后台 Bash 调用完成，不中断对话：

```bash
python -c "
import sys; sys.path.insert(0, '/Users/qslu/.claude/skills/redteam-debate')
from debate_state import DebateState
state = DebateState.load('/path/to/saved_debate.json')
state.add_round(
    red_points=['问题1', '问题2'],
    blue_rebuttals=['反驳1', '反驳2'],
    resolved=[True, False]  # 绿队判定：问题1已解决，问题2未解决
)
state.save()
"
```

保存完成后简要告知用户状态已记录即可，无需展开保存细节。

### 4. 续轮机制

辩论进行中，如果用户说「再来 N 轮」、「继续」、「续」等：

1. 加载已保存的 state（默认目录 `~/.claude/skills/redteam-debate/saved_debates/`，文件名包含议题和日期）。
2. 调用 `state.extend_rounds(N)`。
3. 继续从当前轮次开始。
4. 输出：「已延长 N 轮，当前第 X / Y 轮，继续辩论」。

**跨会话续轮**： debate state 以 JSON 文件形式保存在本地，不同会话可以通过读取同一个文件继续辩论。

### 5. 绿队最终评估

当达到设定轮数或用户说「结束」、「出结论」时：

1. 调用 `state.generate_verdict()` 输出自动评估（基于每轮 `resolved` 标记）。
2. **可选：运行 Arbiter 评分脚本** — 对未解决问题自动标注严重度、置信度和分类：
   ```bash
   python3 /Users/qslu/.claude/skills/redteam-debate/scripts/arbiter.py /path/to/saved_debate.json
   ```
   输出 Markdown 格式的结构化报告，按严重度排序，并给出 Top 3 建议行动。可作为绿队人工判定的参考输入。
3. **绿队人工判定每轮 resolved 标记，再给出最终务实结论。**
4. **将 resolved 标记和初步结论展示给用户，询问是否同意**：
   - 「以上对各项风险的判定是否准确？如不同意某条，请指出。」
5. **用户确认后询问是否满意**:
   - 「以上结论是否满意？如不满意，可以说『再来 N 轮』继续深入。」
6. **用户满意后，询问是否保存结果**：
   - 「是否将辩论结论保存到项目文档？（如保存到 docs/adrs/）」
   - 如果用户确认，将绿队结论写入项目的 `docs/adrs/` 或用户指定路径
   - 文件命名格式：`adr-{序号}-{topic}.md`
7. **保存后询问是否清理辩论过程**：
   - 「辩论过程文件（state JSON）是否删除？保留可后续续轮，删除可释放空间。」
   - 如用户确认删除，执行：`rm /path/to/saved_debate.json`

## 关键规则

| 规则 | 说明 |
|------|------|
| **基于实际** | 所有论点必须引用实际场景、数据、案例，禁止纯理论推演 |
| **逐条对应** | 蓝队反驳必须逐条对应红队编号，不能跳号 |
| **每轮保存** | 每轮结束必须调用 state.save() |
| **可续轮** | 用户可随时要求加轮，不能拒绝 |
| **状态可查** | 用户可随时问「当前第几轮」、「总结了哪些问题」 |
| **用户确认** | 每轮结束后可询问是否继续；最终结论后必须询问是否满意/保存/删除 |
| **最大 5 轮一轮输出** | 如果轮数 > 5，每 5 轮保存一次后询问是否继续，防止上下文过长 |

## 触发词

- 中文：红队、辩论、评估、挑毛病、对抗、审视、审查
- 英文：red team, devil's advocate, debate, evaluate, critique, stress-test
