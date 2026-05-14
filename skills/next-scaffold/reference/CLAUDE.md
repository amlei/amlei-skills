# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Electron desktop app built with Next.js 16 (App Router, static export), React 19, Shadcn UI 4, and Tailwind CSS 4. Package manager is **bun** — never use npm or yarn.

## Build & Dev Commands

```bash
bun install                        # Install dependencies
bun run dev                        # Start Next.js + Electron concurrently
bun run dev:next                   # Next.js dev server only
bun run dev:electron               # Electron only (requires Next.js already running)
bun run build                      # Production build: next build + electron-builder
bun run lint                       # ESLint
```

No test framework is configured yet.

## Architecture

**Dual-process Electron app:**
- **Renderer** — Next.js 16 App Router in `src/app/`, static exported to `out/`
- **Main process** — Electron entry in `electron/main.ts`, loaded via `tsx` at runtime
- **Preload** — `electron/preload.cjs` (CommonJS), context isolation enabled

**Dev mode:** Electron loads `http://localhost:3000` (Next.js dev server). **Production:** loads `out/index.html` from the static export.

**Path alias:** `@/*` → `./src/*`

### Key Directories

- `electron/` — Main process (`main.ts`) and preload (`preload.cjs`)
- `src/app/` — Next.js App Router pages and layouts
- `src/components/` — Cross-page reusable components only (e.g. `ui/`, `ai-elements/`, shared layout components)
- `src/components/workspace/` — Page-specific UI components only (styling/layout, no business logic). Each component is a single file (e.g. `src/components/workspace/github-icon.tsx`, `src/components/workspace/todo-list.tsx`). If a component is complex enough to need sub-components, use a directory (e.g. `src/components/workspace/chat-message/index.tsx`).
- `src/core/` — Business logic layer for pages (counterpart to `workspace/`). Organized by feature domain — each domain is a directory containing its own API calls, interfaces, types, hooks, and logic. `workspace/` handles UI; `core/` handles the underlying functionality.
  - `src/core/api/` — API proxy and shared request utilities
  - `src/core/utils/` — Shared business utilities
- `src/lib/` — Generic utilities (`utils.ts` has `cn()` helper)
- `docs/` — Project documentation (e.g. `shadcn-ui.md`, `ui-design/`)

### Shadcn UI

Config in `components.json` — uses `base-nova` style, CSS variables, Lucide icons. Add components via `bunx shadcn@latest add <name>`. Do not manually edit files in `src/components/ui/`. **Always use Shadcn UI components instead of developing new basic components from scratch.** If a needed component does not exist in `src/components/ui/`, install it via the `shadcn` CLI first.

### AI Elements

`src/components/ai-elements/` is the AI feature component library (not page components). Before creating a new component, first analyze whether it can be composed from existing Shadcn UI base components (e.g. `Button`, `Card`, `Avatar`, `Tooltip`, `Badge`, etc.). Build on top of Shadcn UI primitives rather than reimplementing basic UI patterns. Only add AI-specific styling and behavior as the customization layer.

Page-specific components belong in `src/components/workspace/` (e.g. `src/components/workspace/github-icon.tsx`, `src/components/workspace/todo-list.tsx`).

## Important Notes

- **Cross-platform:** The app must run on both macOS and Windows. Account for platform differences in UI (e.g. keyboard shortcuts use `Cmd` on Mac vs `Ctrl` on Windows, window chrome, font rendering) and Electron main process (e.g. file paths, tray behavior, app menu).
- Next.js 16 has breaking changes from earlier versions. Check `node_modules/next/dist/docs/` before using unfamiliar APIs.
- `next.config.ts` uses `output: "export"` and `images: { unoptimized: true }` — no server-side features (no API routes, no ISR, no image optimization).
- `electron/main.ts` uses `__dirname` derived from `import.meta.url` (ESM). The preload script is `.cjs` (CommonJS).
- Build output goes to `dist/` (electron-builder) and `out/` (Next.js static export).
