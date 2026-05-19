<template>
  <header class="app-header">
    <div class="left-section">
      <!-- 动态面包屑：显示当前所在版块 -->
      <nav class="breadcrumb">
        <span class="root">GWAS Platform</span>
        <span class="separator">/</span>
        <span class="current">{{ currentRouteName }}</span>
      </nav>

      <!-- 项目名称展示与编辑 -->
      <div class="project-tag" v-if="projectStore.currentProjectId">
        <span class="label">当前项目:</span>
        <div v-if="!isEditing" class="name-wrapper" @click="startEdit">
          <span class="name">{{ projectStore.projectName || '未命名项目' }}</span>
          <span class="edit-icon">✏️</span>
        </div>
        <input
            v-else
            ref="nameInput"
            v-model="tempName"
            class="name-input"
            @blur="saveName"
            @keyup.enter="saveName"
        />
        <!-- 核心步骤标签：显示当前流转状态 -->
        <div class="status-badge" :class="projectStore.step.toLowerCase()">
          {{ stepText }}
        </div>
      </div>
    </div>

    <div class="right-section">
      <!-- 通知中心（预留，可用于提示上传/分析完成） -->
      <div class="header-icon">🔔</div>

      <div class="divider"></div>

      <!-- 用户操作区 -->
      <div class="user-dropdown">
        <span class="username">{{ userStore.nickname || 'Admin' }}</span>
        <button class="logout-btn" @click="handleLogout">
          <span class="icon">🚪</span> 退出系统
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useProjectStore } from '@/store/project'
import { useUserStore } from '@/store/user'
import { useRouter, useRoute } from 'vue-router'
import { updateProjectAPI } from '@/api/project'

const projectStore = useProjectStore()
const userStore = useUserStore()
const router = useRouter()
const route = useRoute()

// 1. 项目名称重命名逻辑
const isEditing = ref(false)
const tempName = ref('')
const nameInput = ref<HTMLInputElement | null>(null)

const startEdit = () => {
  tempName.value = projectStore.projectName
  isEditing.value = true
  nextTick(() => nameInput.value?.focus())
}

const saveName = async () => {
  if (tempName.value && tempName.value !== projectStore.projectName) {
    try {
      // 如果已登录，同步到后端
      if (userStore.isLoggedIn && projectStore.currentProjectId) {
        await updateProjectAPI(projectStore.currentProjectId, { name: tempName.value })
      }
      projectStore.projectName = tempName.value
    } catch (e) {
      console.error('Rename failed')
    }
  }
  isEditing.value = false
}

// 2. 状态标签映射
const stepText = computed(() => {
  const map: Record<string, string> = {
    'IDLE': '等待上传',
    'UPLOADED': '待清洗',
    'QC_DONE': '待分析',
    'ANALYSIS_DONE': '分析完成'
  }
  return map[projectStore.step] || '未知状态'
})

// 3. 路由名称映射
const currentRouteName = computed(() => {
  const nameMap: Record<string, string> = {
    'dashboard': '仪表盘',
    'upload': '文件上传',
    'clean': '数据清洗',
    'visualize': '可视化分析',
    'profile': '个人中心',
    'history': '历史记录'
  }
  const pathArr = route.path.split('/')
  const lastPath = pathArr[pathArr.length - 1]
  return nameMap[lastPath] || 'GWAS 分析'
})

// 4. 退出登录
const handleLogout = () => {
  userStore.logout() // 清除 Pinia 状态
  projectStore.resetProject() // 清除当前项目进度
  router.push('/login')
}
</script>

<style scoped>
.app-header {
  height: var(--header-height);
  background: var(--card-bg);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: var(--shadow-sm);
  z-index: var(--z-header);
}

.left-section {
  display: flex;
  align-items: center;
  gap: 24px;
}

.breadcrumb {
  font-size: 14px;
  color: var(--text-muted);
}
.breadcrumb .current {
  color: var(--text-main);
  font-weight: 500;
  margin-left: 8px;
}

.project-tag {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-left: 20px;
  border-left: 2px solid var(--border-color);
}

.project-tag .label {
  font-size: 13px;
  color: var(--text-muted);
}

.name-wrapper {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}

.name-wrapper .name {
  font-weight: 600;
  color: var(--primary-color);
}

.edit-icon {
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.2s;
}

.name-wrapper:hover .edit-icon {
  opacity: 1;
}

.name-input {
  border: 1px solid var(--primary-color);
  border-radius: var(--border-radius-sm);
  padding: 2px 8px;
  outline: none;
  font-weight: 600;
  width: 150px;
}

/* 状态标签样式 */
.status-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: bold;
  text-transform: uppercase;
}
.status-badge.idle { background: #f1f5f9; color: #64748b; }
.status-badge.uploaded { background: #fef3c7; color: #d97706; }
.status-badge.qc_done { background: #dcfce7; color: #16a34a; }
.status-badge.analysis_done { background: #dbeafe; color: #2563eb; }

.right-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  cursor: pointer;
  font-size: 18px;
  color: var(--text-muted);
}

.divider {
  width: 1px;
  height: 24px;
  background: var(--border-color);
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  font-size: 14px;
  font-weight: 500;
}

.logout-btn {
  background: none;
  border: 1px solid var(--border-color);
  padding: 4px 10px;
  border-radius: var(--border-radius-sm);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: #fff1f2;
  color: var(--error-color);
  border-color: var(--error-color);
}
</style>