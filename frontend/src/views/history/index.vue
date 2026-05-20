<template>
  <div class="history-page">
    <!-- 顶部标题与筛选 -->
    <div class="page-header">
      <div class="header-left">
        <h2>📂 项目历史记录</h2>
        <p class="subtitle">管理您的所有 GWAS 分析任务及阶段性结果</p>
      </div>
      <div class="header-right">
        <div class="filter-group">
          <select v-model="filterStatus" class="status-select">
            <option value="all">所有状态</option>
            <option value="ANALYSIS_DONE">已完成</option>
            <option value="QC_DONE">已质控</option>
            <option value="UPLOADED">已上传</option>
            <option value="IDLE">待处理</option>
          </select>
          <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索项目名称..."
              class="search-input"
          />
        </div>
      </div>
    </div>

    <!-- 项目列表表格 -->
    <div class="table-container">
      <table class="history-table">
        <thead>
        <tr>
          <th>项目名称</th>
          <th>当前进度</th>
          <th>样本/位点数</th>
          <th>创建时间</th>
          <th>最近操作</th>
          <th>操作</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="item in filteredProjects" :key="item.id" class="table-row">
          <!-- 项目名：如果为空则显示未命名 -->
          <td class="proj-name">
            <span class="name-text">{{ item.name || '未命名项目' }}</span>
            <span class="proj-id">ID: {{ item.id }}</span>
          </td>

          <!-- 进度标签：复用 StatusTag -->
          <td>
            <StatusTag
                :type="getStatusType(item.step)"
                :label="getStatusLabel(item.step)"
            />
          </td>

          <!-- 规模统计 -->
          <td class="stats-cell">
            <div v-if="item.samples > 0">
              <span class="tag">N={{ item.samples }}</span>
              <span class="tag">M={{ item.snps }}</span>
            </div>
            <span v-else class="text-placeholder">暂无数据</span>
          </td>

          <td class="time-cell">{{ item.date }}</td>
          <td class="time-cell">{{ item.lastModified }}</td>

          <!-- 操作按钮 -->
          <td class="actions-cell">
            <button class="action-btn view" @click="handleContinue(item)">
              {{ item.step === 'ANALYSIS_DONE' ? '查看结果' : '继续分析' }}
            </button>
            <button class="action-btn delete" @click="confirmDelete(item.id)">
              删除
            </button>
          </td>
        </tr>
        </tbody>
      </table>

      <!-- 加载中 -->
      <div v-if="loading" class="empty-state">
        <div class="empty-icon">⏳</div>
        <p>正在加载项目列表...</p>
      </div>

      <!-- 加载错误 -->
      <div v-else-if="errorMsg" class="empty-state error">
        <div class="empty-icon">⚠️</div>
        <p>{{ errorMsg }}</p>
        <button class="action-btn view" style="margin-top:12px" @click="fetchProjects">重新加载</button>
      </div>

      <!-- 空状态 -->
      <div v-else-if="filteredProjects.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">📂</div>
        <p>{{ searchQuery || filterStatus !== 'all' ? '未找到符合条件的分析项目' : '还没有任何项目，请先上传数据进行一次分析' }}</p>
      </div>
    </div>

    <!-- 底部翻页（模拟） -->
    <div class="pagination">
      <span>共 {{ filteredProjects.length }} 个项目</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '@/store/project'
import { getProjectListAPI, deleteProjectAPI } from '@/api/project'
import StatusTag from '@/components/StatusTag.vue'

const router = useRouter()
const projectStore = useProjectStore()

const filterStatus = ref('all')
const searchQuery = ref('')
const loading = ref(true)
const errorMsg = ref('')

interface ProjectItem {
  id: string
  name: string
  step: string
  samples: number
  snps: number
  date: string
  lastModified: string
}

const projects = ref<ProjectItem[]>([])

onMounted(async () => {
  await fetchProjects()
})

async function fetchProjects() {
  loading.value = true
  errorMsg.value = ''
  try {
    const data: any = await getProjectListAPI()
    const list: any[] = Array.isArray(data) ? data : (data?.data || data?.list || [])
    projects.value = list.map((p: any) => ({
      id: p.id || p.ID || '',
      name: p.name || '',
      step: p.current_step || p.step || 'IDLE',
      samples: p.sample_count ?? p.samples ?? 0,
      snps: p.snp_count ?? p.snps ?? 0,
      date: formatDate(p.created_at || p.date),
      lastModified: formatDate(p.updated_at || p.lastModified || p.updatedAt),
    }))
  } catch (e: any) {
    errorMsg.value = e?.message || '加载项目列表失败'
  } finally {
    loading.value = false
  }
}

function formatDate(raw: string): string {
  if (!raw) return ''
  try {
    const d = new Date(raw)
    if (isNaN(d.getTime())) return raw
    return d.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
  } catch {
    return raw
  }
}

const filteredProjects = computed(() => {
  return projects.value.filter(p => {
    const matchStatus = filterStatus.value === 'all' || p.step === filterStatus.value
    const matchSearch = p.name.toLowerCase().includes(searchQuery.value.toLowerCase()) || p.id.includes(searchQuery.value)
    return matchStatus && matchSearch
  })
})

const getStatusType = (step: string) => {
  const map: any = { 'ANALYSIS_DONE': 'success', 'UPLOADED': 'warning', 'QC_DONE': 'info', 'IDLE': 'idle' }
  return map[step] || 'info'
}

const getStatusLabel = (step: string) => {
  const map: any = { 'ANALYSIS_DONE': '已完成', 'QC_DONE': '已质控', 'UPLOADED': '已上传', 'IDLE': '待上传' }
  return map[step] || '未知'
}

async function handleContinue(item: ProjectItem) {
  projectStore.setCurrentProject(item.id)
  const stepMap: Record<string, string> = {
    'IDLE': '/project/upload',
    'UPLOADED': '/project/clean',
    'QC_DONE': '/project/pca',
    'ANALYSIS_DONE': '/project/gwas',
  }
  router.push(stepMap[item.step] || '/project/upload')
}

async function confirmDelete(id: string) {
  if (!confirm(`确定要永久删除项目 ${id} 吗？此操作不可撤销。`)) return
  try {
    await deleteProjectAPI(id)
    projects.value = projects.value.filter(p => p.id !== id)
  } catch (e: any) {
    alert('删除失败: ' + (e?.message || '未知错误'))
  }
}
</script>

<style scoped>
.history-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
}

.subtitle {
  color: var(--text-muted);
  font-size: 14px;
  margin-top: 4px;
}

.filter-group {
  display: flex;
  gap: 12px;
}

.search-input, .status-select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--card-bg);
}

.search-input { width: 240px; }

/* 表格样式 */
.table-container {
  background: var(--card-bg);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.history-table th {
  background: #f8fafc;
  padding: 16px;
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 600;
  border-bottom: 1px solid var(--border-color);
}

.table-row {
  transition: background 0.2s;
}

.table-row:hover {
  background: #f1f5f9;
}

.history-table td {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  font-size: 14px;
}

.proj-name {
  display: flex;
  flex-direction: column;
}

.name-text {
  font-weight: 600;
  color: var(--text-main);
}

.proj-id {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.stats-cell .tag {
  display: inline-block;
  padding: 2px 6px;
  background: #e2e8f0;
  border-radius: 4px;
  font-size: 11px;
  margin-right: 4px;
}

.time-cell {
  color: var(--text-muted);
  font-size: 13px;
}

/* 操作按钮 */
.action-btn {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  border: 1px solid transparent;
  margin-right: 8px;
}

.action-btn.view {
  background: var(--primary-color);
  color: white;
}

.action-btn.delete {
  background: transparent;
  color: var(--error-color);
  border-color: var(--error-color);
}

.action-btn.delete:hover {
  background: var(--error-color);
  color: white;
}

.empty-state {
  padding: 60px;
  text-align: center;
  color: var(--text-muted);
}

.empty-icon { font-size: 40px; margin-bottom: 12px; opacity: 0.5; }

.pagination {
  margin-top: 20px;
  text-align: right;
  font-size: 13px;
  color: var(--text-muted);
}
</style>