# Electron + Next.js Desktop App Reference

This reference covers adding Electron to a Next.js + Shadcn UI project. Only applies when building a desktop app.

## Architecture

**Dual-process Electron app:**
- **Renderer** — Next.js App Router in `src/app/`, static exported to `out/`
- **Main process** — Electron entry in `electron/main.ts`, loaded via `tsx` at runtime
- **Preload** — `electron/preload.cjs` (CommonJS), context isolation enabled

**Dev mode:** Electron loads `http://localhost:3000` (Next.js dev server). **Production:** loads `out/index.html` from the static export.

## Key Directories

- `electron/` — Main process (`main.ts`) and preload (`preload.cjs`)

## Build & Dev Commands

```bash
bun run dev                        # Start Next.js + Electron concurrently
bun run dev:next                   # Next.js dev server only
bun run dev:electron               # Electron only (requires Next.js already running)
bun run build                      # Production build: next build + electron-builder
```

## Next.js Config (Static Export)

```js
// next.config.ts
export default {
  output: "export",
  images: { unoptimized: true },
}
```

No server-side features: no API routes, no ISR, no image optimization.

## Important Notes

- **Cross-platform:** Must run on both macOS and Windows. Account for platform differences in UI (keyboard shortcuts use `Cmd` on Mac vs `Ctrl` on Windows, window chrome, font rendering) and Electron main process (file paths, tray behavior, app menu).
- `electron/main.ts` uses `__dirname` derived from `import.meta.url` (ESM). The preload script is `.cjs` (CommonJS).
- Build output goes to `dist/` (electron-builder) and `out/` (Next.js static export).
