---
name: numina-ui-style
description: 通用前端 UI 设计规范 — 深色 sidebar + 拟态浅色内容区 + 科技感动态效果。适用于数据仪表盘、管理后台、分析平台等 Web 应用。基于 Next.js + Tailwind CSS。
tags: [ui, design-system, frontend, nextjs, tailwindcss, neumorphism, dashboard]
---

# Numina UI 设计规范

深色 sidebar 提供视觉锚点，浅色内容区使用 Neumorphism（拟态）风格营造物理层级感，叠加 subtle 科技感动态效果增加界面活力。

## 配色系统

### 内容区（浅色拟态背景）

| Token | 色值 | 用途 |
|---|---|---|
| `--background` | `#e8ecf1` | 页面背景 |
| `--card` | `#e8ecf1` | 卡片/面板背景 |
| `--foreground` | `#4a5568` | 主文字 |
| `--muted-foreground` | `#718096` | 次要文字 |
| `--primary` | `#4f46e5` | 主色调（靛蓝） |
| `--destructive` | `#ef4444` | 危险/删除/下跌色 |
| `--sw-up` | `#ef4444` | 上涨/正向（红） |
| `--sw-down` | `#22c55e` | 下跌/负向（绿） |

### Sidebar（深色）

| Token | 色值 | 用途 |
|---|---|---|
| `--sidebar-bg` | `#1e293b` | sidebar 背景 |
| `--sidebar-fg` | `#f1f5f9` | sidebar 主文字 |
| `--sidebar-muted` | `#94a3b8` | sidebar 次要文字 |
| `--sidebar-active-bg` | `#4f46e5` | 当前导航项背景 |
| `--sidebar-hover-bg` | `#334155` | 导航项 hover 背景 |

CSS 变量、keyframes、utility classes 已提取到 `components/globals.css`，可直接复制到 Next.js 项目。

## 组件规范摘要

### Card

- `border-0`，无 border
- `rounded-xl`（`--radius: 1rem`）
- `box-shadow: var(--neu-raised)`
- hover: `hover:-translate-y-0.5 transition-all duration-300`

### Button（主按钮）

- `bg-[#4f46e5] text-white hover:brightness-110`
- `rounded-xl`
- 阴影：`6px 6px 12px var(--neu-shadow-dark), -6px -6px 12px var(--neu-shadow-light)`
- 添加 `tech-btn-shimmer` 类实现 hover 白光扫过
- active: `active:scale-[0.97]`

### Input

- `border-0 rounded-xl`
- `box-shadow: var(--neu-pressed-sm)`（凹陷感）
- focus: `.numina-input:focus-visible` 叠加外圈 glow

### Loading / 加载

提供三种加载形态，均支持 `prefers-reduced-motion`：

**`NuminaLoading`** — 区块加载占位
- `variant="aurora"`：纯黑背景 + 多层半透明 RGB 渐变光晕流动（五彩斑斓的黑）
- `variant="soft"`：基于 `--card` 背景的柔和极光 shimmer，适合浅色内容区
- 默认带有一个轻量 spinner 和 `label` 文案

**`NuminaSkeleton`** — 骨架屏
- 使用 `.numina-skeleton` 类实现 shimmer 扫光 + 底层模糊极光
- 支持 `height` / `width` 快速控制尺寸

**`NuminaLoadingBar`** — 顶部/行内进度指示
- 纯黑底条 + 彩虹渐变光点循环滑动
- 适合页面级或组件级 loading 状态

```tsx
import { NuminaLoading, NuminaSkeleton, NuminaLoadingBar } from "@/components/ui";

// 全屏/区块加载
<NuminaLoading variant="aurora" label="数据加载中…" className="h-64" />

// 骨架屏列表
<div className="space-y-3">
  <NuminaSkeleton height="1.5rem" width="60%" />
  <NuminaSkeleton height="1rem" />
  <NuminaSkeleton height="1rem" width="80%" />
</div>

// 顶部 loading bar
<NuminaLoadingBar className="fixed top-0 left-0 right-0 z-50" />
```

### KPI Card / 数据卡片

- 同 Card 基础样式
- 数值添加 `tech-data-flicker` 类
- hover 叠加 radial-gradient 光晕层（`rgba(79,70,229,0.06)`）

### Sidebar 导航项

- 当前项：`background: var(--sidebar-active-bg)` + `animation: tech-glow-pulse 3s ease-in-out infinite`
- 当前项左侧发光条：`w-[3px] h-[60%] bg-gradient-to-b from-transparent via-[#4f46e5] to-transparent`

## 组件代码

组件源码位于 `~/.claude/skills/numina-ui-style/components/` 目录，可直接复制到 Next.js 项目的 `components/ui/` 中使用。

```bash
cp ~/.claude/skills/numina-ui-style/components/* ./components/ui/
```

| 文件 | 说明 |
|---|---|
| `numina-card.tsx` | 拟态卡片组件 |
| `numina-button.tsx` | 主按钮/危险按钮组件 |
| `numina-input.tsx` | 拟态输入框组件 |
| `numina-loading.tsx` | Loading / 骨架屏 / 进度条组件 |
| `index.ts` | 统一导出 |
| `globals.css` | CSS 变量 + keyframes + utility classes |

## 页面骨架

```tsx
<div className="min-h-screen bg-background text-foreground tech-bg-particles">
  <aside className="fixed left-0 top-0 z-50 h-full w-64 -translate-x-full bg-sidebar-bg text-sidebar-fg transition-transform md:translate-x-0 data-[open=true]:translate-x-0">
    {/* Sidebar nav */}
  </aside>
  <main className="p-4 md:ml-64 md:p-8">
    <NuminaCard>Content here</NuminaCard>
  </main>
</div>
```

## 关键原则

1. **WCAG 合规**：所有文字与背景对比度 ≥ 4.5:1，动画需支持 `prefers-reduced-motion`。
2. **border 全透明**：`--border: transparent`，拟态风格不靠 border 划分层级
3. **圆角统一**：全部使用 `rounded-xl`（16px）
4. **阴影分两套**：浅色区用 `#ffffff/#c5c9ce`，深色 sidebar 用 `rgba(0,0,0,0.4)/rgba(255,255,255,0.06)`
5. **科技效果要 subtle**：动画时长 2-4s，opacity 低（0.03-0.25），不抢主体内容视线
6. **响应式优先**：组件必须同时支持桌面 sidebar 和移动端 drawer。
7. **无 mock 数据**：数据为空时展示"暂无数据"，绝不使用假数据填充界面
