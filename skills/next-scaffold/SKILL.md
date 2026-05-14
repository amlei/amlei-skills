---
name: next-scaffold
description: Frontend scaffolding skill for React + Next.js + Shadcn UI projects. Use when initializing a new frontend project, setting up a Next.js app with Shadcn UI components, configuring theming/dark mode/i18n. Default package manager is bun.
argument-hint: "[项目名称]"
disable-model-invocation: true
---

# Next.js + Shadcn UI Frontend Scaffold

Initialize a production-ready frontend project with **React + Next.js + Shadcn UI**, using **bun** as the default package manager.

## Activation

This skill activates when:
- User explicitly asks to initialize/scaffold a new frontend project
- User invokes: `/next-scaffold` command
- User says: "初始化前端", "新建前端项目", "scaffold"

## Step 1: Create Next.js Project

```bash
bun create next-app@latest <project-name> --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
```

Interactive prompts will ask about Turbopack etc. — accept defaults.

After creation, `cd <project-name>`.

## Step 2: Initialize Shadcn UI

```bash
bunx --bun shadcn@latest init -t next
```

This will:
- Create `components.json` config
- Set up CSS variables and theme tokens in `globals.css`
- Configure path aliases

If prompts appear, choose:
- Style: `base-nova` (recommended)
- Base color: `neutral` (default) or as user prefers
- CSS variables: `yes`

## Step 3: Install All Shadcn UI Components

```bash
bunx --bun shadcn@latest add --all
```

This installs every component from the Shadcn UI registry into `src/components/ui/`.

## Step 4: Load Shadcn UI Skill for AI

```bash
bunx --bun skills add shadcn/ui
```

This loads the full shadcn/ui skill (rules, component docs, CLI reference) into the scaffolded project for AI assistants.

## Step 5: Theming Configuration

Shadcn UI uses CSS variables for theming. The theme tokens live in `src/app/globals.css` under `:root` (light) and `.dark` (dark).

### Key Tokens

| Token | Controls |
|-------|----------|
| `background` / `foreground` | App background and default text |
| `card` / `card-foreground` | Elevated surfaces (Card, panels) |
| `popover` / `popover-foreground` | Floating surfaces (Dropdown, Popover) |
| `primary` / `primary-foreground` | Primary actions (Button, active states) |
| `secondary` / `secondary-foreground` | Secondary actions |
| `muted` / `muted-foreground` | Subtle text, placeholders, empty states |
| `accent` / `accent-foreground` | Hover/focus states |
| `destructive` | Error and destructive actions |
| `border` / `input` / `ring` | Borders, input outlines, focus rings |
| `radius` | Base corner radius (all components derive from this) |

### Adding Custom Tokens

Define under `:root` and `.dark`, then expose to Tailwind:

```css
:root {
  --warning: oklch(0.84 0.16 84);
  --warning-foreground: oklch(0.28 0.07 46);
}
.dark {
  --warning: oklch(0.41 0.11 46);
  --warning-foreground: oklch(0.99 0.02 95);
}
@theme inline {
  --color-warning: var(--warning);
  --color-warning-foreground: var(--warning-foreground);
}
```

Use as `bg-warning` / `text-warning-foreground` in components.

### Base Colors

Available base colors: **Neutral**, **Stone**, **Zinc**, **Mauve**, **Olive**, **Mist**, **Taupe**. Set during `shadcn init` or change in `components.json`.

Reference: see `shadcn` skill (`.claude/skills/shadcn/`) for full component rules, docs, and CLI reference.

## Step 6: Dark Mode

### Install next-themes

```bash
bun add next-themes
```

### Create Theme Provider

`src/components/theme-provider.tsx`:

```tsx
"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"

export function ThemeProvider({
  children,
  ...props
}: React.ComponentProps<typeof NextThemesProvider>) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}
```

### Wrap Root Layout

`src/app/layout.tsx`:

```tsx
import { ThemeProvider } from "@/components/theme-provider"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

### Add Mode Toggle

Create `src/components/mode-toggle.tsx` using the DropdownMenu + Button from Shadcn UI with `useTheme()` hook from `next-themes`.

## Step 7: i18n (Internationalization)

### Install next-intl

```bash
bun add next-intl
```

### Configure

1. Create message files: `src/messages/en.json`, `src/messages/zh.json`
2. Create `src/i18n/request.ts` for request-level config
3. Create `src/i18n/routing.ts` for locale routing
4. Update `src/middleware.ts` for locale detection
5. Wrap layout with `NextIntlClientProvider`

### Usage in Components

```tsx
import { useTranslations } from "next-intl"

export function MyComponent() {
  const t = useTranslations("Common")
  return <h1>{t("title")}</h1>
}
```

## Step 8: Copy CLAUDE.md to Scaffolded Project

Copy the reference CLAUDE.md (Electron + Next.js + Shadcn UI project conventions) to the scaffolded project root:

```bash
cp <skill-dir>/reference/CLAUDE.md <project-name>/CLAUDE.md
```

Then update the copied CLAUDE.md to match the new project (adjust project name, remove Electron-specific sections if not needed, update paths).

## Quick Reference

| Action | Command |
|--------|---------|
| Create Next.js app | `bun create next-app@latest <name>` |
| Init Shadcn UI | `bunx --bun shadcn@latest init -t next` |
| Add all components | `bunx --bun shadcn@latest add --all` |
| Add specific component | `bunx --bun shadcn@latest add <name>` |
| Load AI skill | `bunx --bun skills add shadcn/ui` |
| Add dependency | `bun add <package>` |
| Dev server | `bun run dev` |
| Build | `bun run build` |
| Lint | `bun run lint` |

## Conventions

- Package manager: **bun** only — never use npm or yarn
- Path alias: `@/*` → `./src/*`
- Shadcn UI components live in `src/components/ui/` — do not manually edit, manage via CLI
- Always prefer Shadcn UI components over building from scratch
- CSS variables for all theming — no hardcoded colors
