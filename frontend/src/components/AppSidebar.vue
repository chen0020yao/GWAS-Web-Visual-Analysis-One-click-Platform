<template>
  <div class="app-sidebar">
    <!-- 顶部用户状态区 -->
    <div class="user-section">
      <div class="avatar-wrapper">
        <img :src="userStore.userInfo?.avatar || '/default-avatar.png'" class="avatar" @error="$event.target.style.display='none'" />
        <div class="status-dot" :class="{ online: userStore.isLoggedIn }"></div>
      </div>
      <div class="user-info">
        <span class="nickname">{{ userStore.userInfo?.nickname || '游客' }}</span>
        <span class="role" @click="!userStore.isLoggedIn && router.push('/login')">
          {{ userStore.isLoggedIn ? '研究员' : '点击登录' }}
        </span>
      </div>
    </div>

    <div class="menu-container">
      <!-- 1. 创建新项目 (一级) -->
      <div class="menu-group">
        <div class="menu-item parent" @click="toggleGroup('new')">
          <span class="icon">✨</span>
          <span class="text">创建新项目</span>
          <span class="arrow" :class="{ expanded: expandedGroups.new }">▼</span>
        </div>

        <transition name="expand">
          <div class="sub-menu" v-show="expandedGroups.new">
            <!-- 文件上传 (始终可选) -->
            <div class="menu-item sub" :class="{ active: isCurrent('/project/upload') }" @click="go('/project/upload')">
              <span class="dot"></span> 文件上传
            </div>

            <!-- 数据清洗 (上传成功后解锁) -->
            <div
                class="menu-item sub"
                :class="{
                disabled: !projectStore.canAccessQC,
                active: isCurrent('/project/clean')
              }"
                @click="projectStore.canAccessQC && go('/project/clean')"
            >
              <span class="dot"></span> 数据清洗
            </div>

            <!-- 可视化分析 (清洗完成后解锁) -->
            <div
                class="menu-item sub"
                :class="{
                disabled: !projectStore.canAccessViz,
                active: isCurrent('/project/visualize')
              }"
                @click="projectStore.canAccessViz && go('/project/visualize')"
            >
              <span class="dot"></span> 可视化分析
            </div>
          </div>
        </transition>
      </div>

      <!-- 2. 历史记录 (登录后解锁) -->
      <div class="menu-group">
        <div
            class="menu-item parent"
            :class="{ disabled: !userStore.isLoggedIn }"
            @click="userStore.isLoggedIn && toggleHistory()"
        >
          <span class="icon">🕰️</span>
          <span class="text">历史记录</span>
          <span class="arrow" :class="{ expanded: expandedGroups.history }">▼</span>
        </div>

        <transition name="expand">
          <div class="sub-menu" v-show="expandedGroups.history && userStore.isLoggedIn">
            <div
                v-for="item in historyList"
                :key="item.id"
                class="menu-item sub history-item"
                @click="loadHistoryProject(item.id)"
            >
              {{ item.name || item.created_at }}
            </div>
            <div v-if="historyList.length === 0" class="no-data">暂无记录</div>
          </div>
        </transition>
      </div>

      <!-- 3. 个人中心 (登录后解锁) -->
      <div
          class="menu-item"
          :class="{ disabled: !userStore.isLoggedIn, active: isCurrent('/profile') }"
          @click="userStore.isLoggedIn && go('/profile')"
      >
        <span class="icon">👤</span>
        <span class="text">个人中心</span>
      </div>
    </div>

    <!-- 底部重置按钮 (仅创建项目时显示) -->
    <div class="sidebar-footer" v-if="projectStore.currentProjectId">
      <button class="reset-btn" @click="handleNewProject">重新开始</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useProjectStore } from '@/store/project'
import { useUserStore } from '@/store/user'
import { getProjectListAPI } from '@/api/project'

const router = useRouter()
const route = useRoute()
const projectStore = useProjectStore()
const userStore = useUserStore()

// 控制二级菜单展开状态
const expandedGroups = reactive({
  new: true,
  history: false
})

const historyList = ref<any[]>([])

const toggleGroup = (key: 'new' | 'history') => {
  expandedGroups[key] = !expandedGroups[key]
}

const go = (path: string) => router.push(path)
const isCurrent = (path: string) => route.path === path

// 重新开始逻辑
const handleNewProject = () => {
  if (confirm('确定要放弃当前进度并创建新项目吗？')) {
    projectStore.resetProject()
    go('/project/upload')
  }
}

// 加载历史记录
const fetchHistory = async () => {
  if (userStore.isLoggedIn) {
    try {
      const data: any = await getProjectListAPI()
      historyList.value = Array.isArray(data) ? data : (data?.data || [])
    } catch (e) {
      console.error('Failed to fetch history')
    }
  }
}

const loadHistoryProject = async (id: string) => {
  await projectStore.setCurrentProject(id)
  const stepMap: Record<string, string> = {
    'IDLE': '/project/upload',
    'UPLOADED': '/project/clean',
    'QC_DONE': '/project/pca',
    'ANALYSIS_DONE': '/project/visualize',
  }
  router.push(stepMap[projectStore.step] || '/project/upload')
}

const toggleHistory = async () => {
  if (!expandedGroups.history) {
    await fetchHistory()
  }
  toggleGroup('history')
}

onMounted(() => {
  if (userStore.isLoggedIn) fetchHistory()
})
</script>

<style scoped>
.app-sidebar {
  width: var(--sidebar-width);
  height: 100vh;
  background-color: var(--sidebar-bg);
  display: flex;
  flex-direction: column;
  color: var(--sidebar-text-active);
  user-select: none;
}

/* 用户区块 */
.user-section {
  padding: 30px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid var(--sidebar-border);
}

.avatar-wrapper {
  position: relative;
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--sidebar-border);
}

.status-dot {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #64748b;
  border: 2px solid var(--sidebar-bg);
}

.status-dot.online {
  background: var(--primary-color);
}

.user-info {
  display: flex;
  flex-direction: column;
}

.nickname {
  font-size: 14px;
  font-weight: 600;
}

.role {
  font-size: 11px;
  color: var(--sidebar-text-disabled);
  cursor: pointer;
}

/* 菜单项 */
.menu-container {
  flex: 1;
  padding: 15px 0;
  overflow-y: auto;
}

.menu-item {
  padding: 12px 20px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--sidebar-text-active);
}

.menu-item:hover {
  background-color: var(--sidebar-item-hover);
}

.menu-item.active {
  background-color: rgba(66, 185, 131, 0.1);
  color: var(--primary-color);
  border-right: 3px solid var(--primary-color);
}

.icon {
  margin-right: 12px;
  font-size: 16px;
  width: 20px;
  text-align: center;
}

.text {
  flex: 1;
  font-size: 14px;
}

.arrow {
  font-size: 10px;
  transition: transform 0.3s;
}

.arrow.expanded {
  transform: rotate(180deg);
}

/* 子菜单 */
.sub-menu {
  background-color: rgba(0, 0, 0, 0.1);
}

.menu-item.sub {
  padding-left: 52px;
  font-size: 13px;
  color: var(--sidebar-text-active);
}

.dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background-color: currentColor;
  margin-right: 10px;
  opacity: 0.5;
}

/* 历史记录项 */
.history-item {
  font-size: 12px !important;
  color: var(--sidebar-text-disabled) !important;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 禁用状态：由灰变黑的核心逻辑 */
.disabled {
  color: var(--sidebar-text-disabled) !important;
  cursor: not-allowed !important;
  pointer-events: none; /* 彻底禁止点击 */
}

.disabled .icon {
  filter: grayscale(1);
  opacity: 0.5;
}

.no-data {
  padding: 10px 52px;
  font-size: 12px;
  color: var(--sidebar-text-disabled);
}

/* 底部操作 */
.sidebar-footer {
  padding: 20px;
  border-top: 1px solid var(--sidebar-border);
}

.reset-btn {
  width: 100%;
  padding: 8px;
  background: transparent;
  border: 1px solid var(--sidebar-border);
  color: var(--sidebar-text-disabled);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: 12px;
}

.reset-btn:hover {
  border-color: var(--error-color);
  color: var(--error-color);
}

/* 展开动画 */
.expand-enter-active, .expand-leave-active {
  transition: max-height 0.3s ease;
  overflow: hidden;
}
.expand-enter-from, .expand-leave-to {
  max-height: 0;
}
.expand-enter-to, .expand-leave-from {
  max-height: 300px;
}
</style>