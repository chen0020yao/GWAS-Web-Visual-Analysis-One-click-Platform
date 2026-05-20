<template>
  <div class="main-layout">
    <!-- 左侧导航栏：控制项目切换、用户信息、历史记录 -->
    <AppSidebar class="sidebar-container" />

    <div class="main-wrapper">
      <!-- 顶部信息栏：显示当前项目名、运行状态、用户操作 -->
      <AppHeader class="header-container" />

      <!-- 主视图区域：带有流畅的页面切换动画 -->
      <main class="content-body">
        <div class="content-scroll-area">
          <router-view v-slot="{ Component }">
            <transition name="fade-transform" mode="out-in">
              <component :is="Component" :key="route.fullPath" />
            </transition>
          </router-view>
        </div>
      </main>

      <!-- 全局底部状态条 (可选)：显示系统负载或后台任务数 -->
      <footer class="layout-footer">
        <div class="footer-left">
          <span class="status-indicator"></span>
          系统状态：运行良好
        </div>
        <div class="footer-right">
          © 2026 GWAS Data Analysis & Visualization System
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'

const route = useRoute()
const userStore = useUserStore()

onMounted(() => {
  if (userStore.token) {
    userStore.fetchUserInfo()
  }
})
</script>

<style scoped>
.main-layout {
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden; /* 防止外层出现多余滚动条 */
  background-color: var(--main-bg);
}

.sidebar-container {
  flex-shrink: 0;
  z-index: var(--z-sidebar);
}

.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0; /* 修复 flex 子元素溢出问题 */
}

.header-container {
  flex-shrink: 0;
}

.content-body {
  flex: 1;
  position: relative;
  overflow: hidden;
  padding: 24px; /* 全局页面内边距 */
}

.content-scroll-area {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  /* 已经在 variables.css 中美化过滚动条 */
}

.layout-footer {
  height: 32px;
  background: var(--card-bg);
  border-top: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  font-size: 11px;
  color: var(--text-muted);
}

.status-indicator {
  display: inline-block;
  width: 8px;
  height: 8px;
  background-color: var(--primary-color);
  border-radius: 50%;
  margin-right: 6px;
  box-shadow: 0 0 5px var(--primary-color);
}

/* 页面切换动画：从下方轻微浮现 */
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s ease;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>