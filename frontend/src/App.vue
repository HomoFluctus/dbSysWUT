<template>
  <router-view v-slot="{ Component, route }">
    <transition name="page-fade" mode="out-in">
      <component :is="Component" :key="route.path" />
    </transition>
  </router-view>
</template>

<script setup>
</script>

<style>
/* ===== Element Plus Dark Overrides ===== */
html.dark {
  --el-bg-color: #0f172a;
  --el-bg-color-overlay: #1e293b;
  --el-bg-color-page: #0f172a;
  --el-border-color: #334155;
  --el-border-color-light: #334155;
  --el-border-color-lighter: #1e293b;
  --el-text-color-primary: #f1f5f9;
  --el-text-color-regular: #e2e8f0;
  --el-text-color-secondary: #94a3b8;
  --el-text-color-placeholder: #64748b;
  --el-fill-color: #1e293b;
  --el-fill-color-light: #253349;
  --el-fill-color-blank: #0f172a;
  --el-color-primary: #818cf8;
  --el-color-primary-light-3: #6366f1;
  --el-color-primary-light-5: #4f46e5;
  --el-color-primary-light-7: #3730a3;
  --el-color-primary-light-9: #312e81;
  --el-color-primary-dark-2: #a5b4fc;
  --el-mask-color: rgba(0,0,0,0.6);
  --el-font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans SC', sans-serif;
}

/* ===== Design Tokens ===== */
:root {
  --bg-base: #0f172a;
  --bg-surface: #1e293b;
  --bg-elevated: #1e293b;
  --text-primary: #f1f5f9;
  --text-secondary: #e2e8f0;
  --text-muted: #94a3b8;
  --border-color: #334155;
  --radius-lg: 12px;
  --radius-md: 8px;
  --shadow-card: 0 1px 3px rgba(0,0,0,0.3);
  --shadow-hover: 0 4px 16px rgba(0,0,0,0.5);
  --transition-fast: 0.15s ease;
  --transition-normal: 0.25s ease;
}

/* ===== Global Reset ===== */
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: var(--el-font-family);
  background: var(--bg-base);
  color: var(--text-primary);
  min-height: 100vh;
}
a { color: var(--el-color-primary); text-decoration: none; }

/* ===== Scrollbar ===== */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #475569; }

/* ===== Page Transitions ===== */
.page-fade-enter-active, .page-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.page-fade-enter-from { opacity: 0; transform: translateY(10px); }
.page-fade-leave-to { opacity: 0; transform: translateY(-10px); }

/* ===== Element Plus Overrides ===== */
.el-card {
  --el-card-bg-color: var(--bg-surface);
  --el-card-border-color: var(--border-color);
  border-radius: var(--radius-lg);
}
.el-button { border-radius: var(--radius-md); font-weight: 500; }
.el-input__wrapper, .el-textarea__inner {
  background: var(--bg-base) !important;
  border-radius: var(--radius-md) !important;
}
.el-select .el-input__wrapper { background: var(--bg-base) !important; }
.el-dialog {
  --el-dialog-bg-color: var(--bg-surface);
  border-radius: var(--radius-lg);
}
.el-popper.is-dark { background: var(--bg-elevated) !important; }
.el-message { border-radius: var(--radius-md); }
.el-pagination button, .el-pager li {
  background: var(--bg-surface) !important;
  border-radius: 6px !important;
}
.el-pager li.is-active { background: var(--el-color-primary) !important; }
.el-tag { border-radius: 6px; }
.el-empty__description p { color: var(--text-muted); }
.el-drawer { --el-drawer-bg-color: var(--bg-surface); }
.el-timeline-item__node { background: var(--border-color); }
.el-descriptions__label { color: var(--text-muted); }
.el-skeleton { --el-skeleton-color: #253349; --el-skeleton-to-color: #334155; }
</style>
