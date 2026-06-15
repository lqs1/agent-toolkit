---
name: numina-ui-style
description: 通用前端 UI 设计规范 — 深色 sidebar + 拟态浅色内容区 + 科技感动态效果。适用于数据仪表盘、管理后台、分析平台等 Web 应用。基于 Next.js + Tailwind CSS。
tags: [ui, design-system, frontend, nextjs, tailwindcss, neumorphism, dashboard]
---

# Numina UI 设计规范

## 设计理念

深色 sidebar 提供视觉锚点，浅色内容区使用 Neumorphism（拟态）风格营造物理层级感，叠加 subtle 科技感动态效果增加界面活力。三者融合，打造专业且有现代感的仪表盘体验。

---

## 配色系统

### 内容区（浅色拟态背景）

| Token | 色值 | 用途 | WCAG 对比度* |
|---|---|---|---|
| `--background` | `#e8ecf1` | 页面背景 | 需与文字 ≥ 4.5:1 |
| `--card` | `#e8ecf1` | 卡片/面板背景 | 需与文字 ≥ 4.5:1 |
| `--foreground` | `#4a5568` | 主文字 | 在 `#e8ecf1` 上约 5.9:1 ✓ |
| `--muted-foreground` | `#718096` | 次要文字、placeholder | 在 `#e8ecf1` 上约 4.0:1 ✗ 建议 `#5a6b7d` |
| `--primary` | `#4f46e5` | 主色调（靛蓝） | 需与背景 ≥ 4.5:1 |
| `--destructive` | `#ef4444` | 危险/删除/下跌色 | 需与背景 ≥ 4.5:1 |
| `--sw-up` | `#ef4444` | 上涨/正向（红） | 可配置 |
| `--sw-down` | `#22c55e` | 下跌/负向（绿） | 可配置 |

\* 验收前用 [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/) 验证。

### Sidebar（深色）

| Token | 色值 | 用途 |
|---|---|---|
| `--sidebar-bg` | `#1e293b` | sidebar 背景 |
| `--sidebar-fg` | `#f1f5f9` | sidebar 主文字 |
| `--sidebar-muted` | `#94a3b8` | sidebar 次要文字 |
| `--sidebar-active-bg` | `#4f46e5` | 当前导航项背景 |
| `--sidebar-hover-bg` | `#334155` | 导航项 hover 背景 |

---

## CSS 变量完整定义

在 `globals.css` 或 Tailwind 主题中定义：

```css
:root {
  --background: #e8ecf1;
  --card: #e8ecf1;
  --foreground: #4a5568;
  --muted-foreground: #718096; /* 建议改为 #5a6b7d 以满足对比度 */
  --primary: #4f46e5;
  --destructive: #ef4444;
  --sw-up: #ef4444;
  --sw-down: #22c55e;
  --border: transparent;
  --radius: 1rem;

  --sidebar-bg: #1e293b;
  --sidebar-fg: #f1f5f9;
  --sidebar-muted: #94a3b8;
  --sidebar-active-bg: #4f46e5;
  --sidebar-hover-bg: #334155;
}
```

## 减少动效支持（Accessibility）

所有科技感动画必须响应 `prefers-reduced-motion`：

```css
@media (prefers-reduced-motion: reduce) {
  .tech-glow,
  .tech-glow-fast,
  .tech-data-flicker,
  .tech-shimmer-bg,
  .tech-bg-particles::after {
    animation: none !important;
  }

  .tech-btn-shimmer::before {
    display: none;
  }
}
```

对于无法完全消除的 pulse 效果，可退化为静态 `box-shadow`。

## 地域配色说明

默认 `--sw-up` 为红、`--sw-down` 为绿，符合中国/东亚市场习惯。面向欧美用户时覆盖为：

```css
[data-region="us"] {
  --sw-up: #22c55e;
  --sw-down: #ef4444;
}
```

### 内容区阴影（浅色背景 `#e8ecf1`）

```css
--neu-shadow-light: #ffffff;
--neu-shadow-dark: #c5c9ce;

/* 凸起卡片 */
--neu-raised: 8px 8px 16px var(--neu-shadow-dark), -8px -8px 16px var(--neu-shadow-light);
--neu-raised-sm: 4px 4px 8px var(--neu-shadow-dark), -4px -4px 8px var(--neu-shadow-light);

/* 凹陷输入框 */
--neu-pressed: inset 6px 6px 10px var(--neu-shadow-dark), inset -6px -6px 10px var(--neu-shadow-light);
--neu-pressed-sm: inset 3px 3px 6px var(--neu-shadow-dark), inset -3px -3px 6px var(--neu-shadow-light);
```

### Sidebar 阴影（深色背景 `#1e293b`）

```css
--sidebar-shadow-up: rgba(255,255,255,0.06);
--sidebar-shadow-down: rgba(0,0,0,0.4);

--sidebar-raised: 6px 6px 12px var(--sidebar-shadow-down), -6px -6px 12px var(--sidebar-shadow-up);
--sidebar-pressed: inset 4px 4px 8px var(--sidebar-shadow-down), inset -4px -4px 8px var(--sidebar-shadow-up);
```

---

## 科技感动态效果

### CSS Keyframes（放入 globals.css）

```css
@keyframes tech-glow-pulse {
  0%, 100% { box-shadow: 0 0 4px rgba(79, 70, 229, 0.3), 0 0 12px rgba(79, 70, 229, 0.15); }
  50% { box-shadow: 0 0 8px rgba(79, 70, 229, 0.5), 0 0 24px rgba(79, 70, 229, 0.25); }
}

@keyframes tech-shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

@keyframes tech-float {
  0%, 100% { transform: translateY(0) scale(1); opacity: 0.3; }
  50% { transform: translateY(-20px) scale(1.2); opacity: 0.6; }
}

@keyframes tech-data-flicker {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.85; }
}
```

### Utility Classes

```css
.tech-glow { animation: tech-glow-pulse 3s ease-in-out infinite; }
.tech-glow-fast { animation: tech-glow-pulse 1.5s ease-in-out infinite; }
.tech-data-flicker { animation: tech-data-flicker 4s ease-in-out infinite; }

.tech-shimmer-bg {
  background: linear-gradient(90deg, transparent 0%, rgba(79, 70, 229, 0.08) 50%, transparent 100%);
  background-size: 200% 100%;
  animation: tech-shimmer 2.5s infinite linear;
}

/* 按钮流光 hover */
.tech-btn-shimmer {
  position: relative;
  overflow: hidden;
}
.tech-btn-shimmer::before {
  content: "";
  position: absolute; top: 0; left: -100%;
  width: 100%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
  transition: left 0.5s ease;
}
.tech-btn-shimmer:hover::before { left: 100%; }

/* 背景浮动光点 */
.tech-bg-particles {
  position: relative; overflow: hidden;
}
.tech-bg-particles::after {
  content: "";
  position: absolute; inset: 0;
  background:
    radial-gradient(circle at 20% 30%, rgba(79, 70, 229, 0.06) 0%, transparent 40%),
    radial-gradient(circle at 80% 70%, rgba(139, 92, 246, 0.05) 0%, transparent 40%),
    radial-gradient(circle at 50% 50%, rgba(79, 70, 229, 0.03) 0%, transparent 50%);
  pointer-events: none; z-index: 0;
  animation: tech-float 8s ease-in-out infinite;
}
```

---

## 组件规范

### Card

- `border-0`，无 border
- `rounded-xl`（`--radius: 1rem`）
- `box-shadow: var(--neu-raised)`
- hover: `hover:-translate-y-0.5 transition-all duration-300`
- 可选：hover 时叠加 radial-gradient 发光扩散层

### Button（主按钮）

- `bg-[#4f46e5] text-white hover:brightness-110`
- `rounded-xl`
- 阴影：`6px 6px 12px var(--neu-shadow-dark), -6px -6px 12px var(--neu-shadow-light)`
- 添加 `tech-btn-shimmer` 类实现 hover 白光扫过
- active: `active:scale-[0.97]`

### Input

- `border-0 rounded-xl`
- `box-shadow: var(--neu-pressed-sm)`（凹陷感）
- focus: 使用 `:focus-visible` 叠加外圈 glow，避免内联 JS：

  ```css
  .numina-input:focus-visible {
    outline: none;
    box-shadow:
      var(--neu-pressed-sm),
      0 0 8px rgba(79, 70, 229, 0.25);
    animation: tech-glow-pulse 2s ease-in-out infinite;
  }
  ```

### KPI Card / 数据卡片

- 同 Card 基础样式
- 数值添加 `tech-data-flicker` 类
- hover 叠加 radial-gradient 光晕层（`rgba(79,70,229,0.06)`）

### Sidebar 导航项

- 当前项：`background: var(--sidebar-active-bg)` + `animation: tech-glow-pulse 3s ease-in-out infinite`
- 当前项左侧发光条：`w-[3px] h-[60%] bg-gradient-to-b from-transparent via-[#4f46e5] to-transparent`

---

## Shadcn / Next.js 组件示例

### `components/ui/numina-card.tsx`

```tsx
import { cn } from "@/lib/utils";

interface NuminaCardProps extends React.HTMLAttributes<HTMLDivElement> {}

export function NuminaCard({ className, children, ...props }: NuminaCardProps) {
  return (
    <div
      className={cn(
        "rounded-xl bg-card p-6 transition-all duration-300",
        "hover:-translate-y-0.5",
        className
      )}
      style={{ boxShadow: "var(--neu-raised)" }}
      {...props}
    >
      {children}
    </div>
  );
}
```

### 页面骨架

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

---

## 使用示例

### 页面背景粒子

```tsx
<div className="space-y-6 tech-bg-particles">
  {/* 内容 */}
</div>
```

### 主按钮

```tsx
<Button className="tech-btn-shimmer">
  分析
</Button>
```

### 输入框

```tsx
<Input className="numina-input" />
```

## 暗色 / 高对比模式（可选扩展）

Numina 默认提供浅色拟态主题。如需暗色模式，定义第二套变量：

```css
[data-theme="dark"] {
  --background: #0f172a;
  --card: #1e293b;
  --foreground: #f1f5f9;
  --muted-foreground: #94a3b8;
  --neu-shadow-light: #334155;
  --neu-shadow-dark: #020617;
}
```

高对比模式应进一步增大文字与背景对比度，并确保所有状态（hover/active/focus）有非颜色提示（如边框、图标）。

## 排版尺度

| Token | Size | Line Height | Usage |
|---|---|---|---|
| `--text-xs` | 0.75rem | 1rem | 标签、辅助文字 |
| `--text-sm` | 0.875rem | 1.25rem | 表格、次要内容 |
| `--text-base` | 1rem | 1.5rem | 正文 |
| `--text-lg` | 1.125rem | 1.75rem | 小标题 |
| `--text-xl` | 1.25rem | 1.75rem | 卡片标题 |
| `--text-2xl` | 1.5rem | 2rem | 页面标题 |
| `--text-3xl` | 1.875rem | 2.25rem | 数据大屏 KPI |

## 响应式 Sidebar

桌面端使用固定 16rem (`w-64`) sidebar。移动端改为抽屉：

```tsx
<aside className="fixed z-50 h-full w-64 -translate-x-full transition-transform md:translate-x-0 data-[open=true]:translate-x-0">
  {/* nav */}
</aside>
```

主内容区在移动端不需要偏移：

```tsx
<main className="p-4 md:ml-64 md:p-8">...{</main>
```

---

## 关键原则

1. **WCAG 合规**：所有文字与背景对比度 ≥ 4.5:1，动画需支持 `prefers-reduced-motion`。
2. **border 全透明**：`--border: transparent`，拟态风格不靠 border 划分层级
3. **圆角统一**：全部使用 `rounded-xl`（16px）
4. **阴影分两套**：浅色区用 `#ffffff/#c5c9ce`，深色 sidebar 用 `rgba(0,0,0,0.4)/rgba(255,255,255,0.06)`
5. **科技效果要 subtle**：动画时长 2-4s，opacity 低（0.03-0.25），不抢主体内容视线
6. **响应式优先**：组件必须同时支持桌面 sidebar 和移动端 drawer。
7. **无 mock 数据**：数据为空时展示"暂无数据"，绝不使用假数据填充界面
