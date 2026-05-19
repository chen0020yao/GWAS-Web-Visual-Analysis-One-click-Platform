<template>
  <div class="dashboard-page">
    <!-- 1. 顶部数据概览 -->
    <header class="stat-grid">
      <div class="stat-card" v-for="item in statistics" :key="item.label">
        <div class="stat-icon" :style="{ backgroundColor: item.color + '15', color: item.color }">
          <i :class="item.icon"></i>
        </div>
        <div class="stat-info">
          <span class="label">{{ item.label }}</span>
          <div class="value-row">
            <span class="value">{{ item.value }}</span>
            <span class="unit">{{ item.unit }}</span>
          </div>
        </div>
      </div>
    </header>

    <div class="dashboard-main">
      <!-- 2. 左侧：最近项目动态 (核心业务) -->
      <section class="project-timeline">
        <div class="section-header">
          <h3>🕒 最近分析项目</h3>
          <router-link to="/history" class="more-link">查看全部</router-link>
        </div>

        <div class="project-list">
          <div v-for="proj in recentProjects" :key="proj.id" class="project-item">
            <div class="proj-status">
              <StatusTag :type="getStatusType(proj.step)" :label="proj.stepLabel" :dot="true" />
            </div>
            <div class="proj-body">
              <h4 @click="navigateToProject(proj.id)">{{ proj.name || '未命名项目' }}</h4>
              <p>样本数: {{ proj.samples }} | 位点数: {{ proj.snps }} | 创建于: {{ proj.date }}</p>
            </div>
            <div class="proj-actions">
              <button class="ghost-btn" @click="navigateToProject(proj.id)">继续分析</button>
            </div>
          </div>
        </div>

        <!-- 快捷入口 -->
        <div class="quick-start">
          <button class="primary-btn pulse" @click="$router.push('/project/upload')">
            🚀 开启全新分析任务
          </button>
        </div>
      </section>

      <!-- 3. 右侧：系统资源与指南 -->
      <aside class="dashboard-aside">
        <div class="system-monitor card">
          <h4>💻 服务器算力监控</h4>
          <div class="monitor-item">
            <label>CPU 使用率</label>
            <div class="progress-bar"><div class="fill" style="width: 45%"></div></div>
          </div>
          <div class="monitor-item">
            <label>内存 (128GB RAM)</label>
            <div class="progress-bar"><div class="fill warning" style="width: 78%"></div></div>
          </div>
          <p class="monitor-note">当前队列排队中：2 个任务</p>
        </div>

        <div class="guide-card card">
          <h4>📚 快速指南</h4>
          <ul class="guide-links">
            <li><a href="#">如何准备 VCF 文件？</a></li>
            <li><a href="#">QC 质控标准说明</a></li>
            <li><a href="#">PCA 群体分层详解</a></li>
          </ul>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '@/store/project'
import StatusTag from '@/components/StatusTag.vue'

const router = useRouter()
const projectStore = useProjectStore()

// 模拟统计数据
const statistics = [
  { label: '累计分析样本', value: '1,420', unit: '个', icon: '👤', color: '#42b983' },
  { label: '显著关联位点', value: '284', unit: 'SNPs', icon: '🧬', color: '#3b82f6' },
  { label: '占用存储空间', value: '1.2', unit: 'TB', icon: '💾', color: '#f59e0b' },
  { label: '计算总耗时', value: '45.5', unit: 'h', icon: '⏱️', color: '#8b5cf6' }
]

// 模拟最近项目列表
const recentProjects = ref([
  { id: 'p1', name: 'T2D_GWAS_Phase1', step: 'ANALYSIS_DONE', stepLabel: '已完成', samples: 500, snps: '1.2M', date: '2026-05-01' },
  { id: 'p2', name: 'Kidney_Disease_Replication', step: 'UPLOADED', stepLabel: '待清洗', samples: 120, snps: '800K', date: '2026-05-05' },
  { id: 'p3', name: '', step: 'IDLE', stepLabel: '待上传', samples: 0, snps: '0', date: '2026-05-06' }
])

const getStatusType = (step: string) => {
  const map: any = { 'ANALYSIS_DONE': 'success', 'UPLOADED': 'warning', 'IDLE': 'idle' }
  return map[step] || 'info'
}

const navigateToProject = (id: string) => {
  projectStore.setCurrentProject(id)
  router.push('/project/clean') // 或根据 step 动态跳转
}
</script>

<style scoped>
.dashboard-page {
  max-width: 1400px;
  margin: 0 auto;
}

/* 统计卡片 */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--card-bg);
  padding: 24px;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-info .label {
  font-size: 13px;
  color: var(--text-muted);
}

.value-row {
  margin-top: 4px;
}

.value-row .value {
  font-size: 24px;
  font-weight: bold;
  color: var(--text-main);
}

.value-row .unit {
  font-size: 12px;
  color: var(--text-muted);
  margin-left: 4px;
}

/* 主区域布局 */
.dashboard-main {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
}

.project-timeline {
  background: var(--card-bg);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
  padding: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.more-link {
  font-size: 13px;
  color: var(--primary-color);
  text-decoration: none;
}

/* 项目列表 */
.project-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.project-item {
  display: flex;
  align-items: center;
  padding: 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.project-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.proj-body {
  flex: 1;
  margin-left: 16px;
}

.proj-body h4 {
  margin: 0 0 4px 0;
  cursor: pointer;
  color: var(--text-main);
}

.proj-body p {
  margin: 0;
  font-size: 12px;
  color: var(--text-muted);
}

.quick-start {
  margin-top: 30px;
  text-align: center;
}

/* 右侧边栏样式 */
.dashboard-aside {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card {
  background: var(--card-bg);
  padding: 20px;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
}

.card h4 { margin-top: 0; margin-bottom: 16px; font-size: 15px; }

.monitor-item {
  margin-bottom: 15px;
}

.monitor-item label { font-size: 12px; color: var(--text-muted); }

.progress-bar {
  height: 8px;
  background: #edf2f7;
  border-radius: 4px;
  margin-top: 6px;
  overflow: hidden;
}

.fill { height: 100%; background: var(--primary-color); }
.fill.warning { background: var(--error-color); }

.monitor-note { font-size: 11px; color: var(--text-muted); text-align: right; }

.guide-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.guide-links li { margin-bottom: 10px; }
.guide-links a { font-size: 13px; color: var(--info-color); text-decoration: none; }
.guide-links a:hover { text-decoration: underline; }

/* 动效 */
.pulse {
  animation: pulse-animation 2s infinite;
}

@keyframes pulse-animation {
  0% { box-shadow: 0 0 0 0px rgba(66, 185, 131, 0.4); }
  100% { box-shadow: 0 0 0 10px rgba(66, 185, 131, 0); }
}
</style>