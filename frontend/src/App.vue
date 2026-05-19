<template>
  <!-- 全局唯一的路由出口 -->
  <router-view v-slot="{ Component }">
    <transition name="fade" mode="out-in">
      <component :is="Component" />
    </transition>
  </router-view>
</template>

<style>
/* 1. 定义全局 CSS 变量 (Design Tokens) */
:root {
  /* 品牌色与状态色 - 典型的生信分析软件配色 */
  --primary-color: #42b983;      /* 核心绿色 */
  --primary-hover: #38a169;
  --secondary-color: #3b82f6;    /* 蓝色，常用于对照组 */
  --accent-color: #e11d48;       /* 红色，常用于显著位点或病例组 */

  /* 背景与边框 */
  --bg-color: #f8fafc;           /* 极浅灰蓝背景 */
  --card-bg: #ffffff;
  --border-color: #e2e8f0;

  /* 文字颜色 */
  --text-main: #1e293b;
  --text-muted: #64748b;

  /* 阴影与圆角 */
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
  --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1);
  --border-radius-lg: 12px;
  --border-radius-md: 8px;
}

/* 2. 基础 Reset */
* {
  box-sizing: border-box;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

html, body, #app {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  color: var(--text-main);
  background-color: var(--bg-color);
  font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
}

/* 3. 路由切换动画 - 让单页应用更平滑 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 4. 全局滚动条样式 (针对 Webkit 内核) */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* 5. 通用工具类 */
.math {
  font-family: "Times New Roman", Times, serif;
  font-style: italic;
}
</style>