<template>
  <div class="snp-lookup-page">
    <!-- 顶部导航 -->
    <StepFlow currentStep="ANALYSIS_DONE" />

    <div class="lookup-container">
      <div class="search-section">
        <h2 class="title">🧬 SNP 功能注释查询</h2>
        <p class="subtitle">输入 RS ID 获取该位点的基因定位、调控元件及人群频率信息</p>

        <div class="search-box">
          <input
              v-model="searchId"
              type="text"
              placeholder="输入 RS ID (例如: rs112, rs445)..."
              @keyup.enter="handleSearch"
          />
          <button class="search-btn" :disabled="loading" @click="handleSearch">
            <span v-if="!loading">查询注释</span>
            <span v-else class="mini-spinner"></span>
          </button>
        </div>
      </div>

      <!-- 查询结果区域 -->
      <Transition name="fade">
        <div v-if="snpDetails" class="results-section">
          <!-- 1. 基础信息卡片 -->
          <div class="info-grid">
            <div class="detail-card main-info">
              <h3>基本信息</h3>
              <div class="grid-content">
                <div class="item"><label>RS ID:</label> <span>{{ snpDetails.rsid }}</span></div>
                <div class="item"><label>位置:</label> <span>Chr{{ snpDetails.chr }}:{{ snpDetails.pos }}</span></div>
                <div class="item"><label>等位基因:</label> <span>{{ snpDetails.ref }}/{{ snpDetails.alt }}</span></div>
                <div class="item"><label>功能类型:</label> <StatusTag type="primary" :label="snpDetails.func" /></div>
              </div>
            </div>

            <div class="detail-card gene-info">
              <h3>基因映射 (Gene Mapping)</h3>
              <div class="grid-content">
                <div class="item"><label>最近基因:</label> <span class="highlight">{{ snpDetails.nearestGene }}</span></div>
                <div class="item"><label>距离:</label> <span>{{ snpDetails.distance }} bp</span></div>
                <div class="item"><label>区域:</label> <span>{{ snpDetails.region }}</span></div>
              </div>
            </div>
          </div>

          <!-- 2. 人群频率表格 -->
          <div class="detail-card full-width">
            <h3>人群频率 (MAF)</h3>
            <table class="freq-table">
              <thead>
              <tr>
                <th>1000 Genomes</th>
                <th>EAS (东亚)</th>
                <th>EUR (欧洲)</th>
                <th>AFR (非洲)</th>
                <th>AMR (美洲)</th>
              </tr>
              </thead>
              <tbody>
              <tr>
                <td>{{ snpDetails.freq.global }}</td>
                <td>{{ snpDetails.freq.eas }}</td>
                <td>{{ snpDetails.freq.eur }}</td>
                <td>{{ snpDetails.freq.afr }}</td>
                <td>{{ snpDetails.freq.amr }}</td>
              </tr>
              </tbody>
            </table>
          </div>
        </div>
      </Transition>

      <!-- 初始状态提示 -->
      <div v-if="!snpDetails && !loading" class="empty-guide">
        <div class="icon">🔍</div>
        <p>在上方输入 ID 开始探索遗传位点的奥秘</p>
      </div>
    </div>

    <!-- 加载遮罩 -->
    <LoadingOverlay
        :visible="loading"
        title="正在检索注释数据库"
        description="正在从 Ensembl 和 dbSNP 获取最新的功能基因组数据..."
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import StepFlow from '@/components/StepFlow.vue'
import StatusTag from '@/components/StatusTag.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import { getSNPAnnotationAPI } from '@/api/analysis'

const searchId = ref('')
const loading = ref(false)
const snpDetails = ref<any>(null)

const handleSearch = async () => {
  if (!searchId.value) return
  const rsid = searchId.value.startsWith('rs') ? searchId.value : `rs${searchId.value}`

  loading.value = true
  try {
    const res = await getSNPAnnotationAPI(rsid)
    snpDetails.value = {
      rsid: res.rsid || rsid,
      chr: '1',
      pos: '—',
      ref: '—',
      alt: '—',
      func: res.consequence || res.gene || '查询中...',
      nearestGene: res.gene || 'Unknown',
      distance: '—',
      region: '—',
      freq: { global: '—', eas: '—', eur: '—', afr: '—', amr: '—' }
    }
  } catch (e) {
    console.error('SNP注释查询失败', e)
    alert('查询失败，请检查RS ID是否正确')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.snp-lookup-page {
  max-width: 1000px;
  margin: 0 auto;
}

.lookup-container {
  display: flex;
  flex-direction: column;
  gap: 30px;
  margin-top: 20px;
}

/* 搜索栏样式 */
.search-section {
  text-align: center;
  padding: 40px;
  background: var(--card-bg);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
}

.title {
  font-size: 24px;
  color: var(--text-main);
  margin-bottom: 8px;
}

.subtitle {
  color: var(--text-muted);
  font-size: 14px;
  margin-bottom: 24px;
}

.search-box {
  display: flex;
  max-width: 600px;
  margin: 0 auto;
  gap: 10px;
}

.search-box input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.search-box input:focus {
  border-color: var(--primary-color);
  outline: none;
}

.search-btn {
  padding: 0 24px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

/* 结果卡片样式 */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.detail-card {
  background: var(--card-bg);
  padding: 24px;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
}

.detail-card h3 {
  font-size: 16px;
  margin-bottom: 16px;
  color: var(--text-main);
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 10px;
}

.grid-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.item {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.item label {
  color: var(--text-muted);
}

.item span {
  font-weight: 500;
  color: var(--text-main);
}

.highlight {
  color: var(--primary-color) !important;
  font-weight: bold !important;
}

/* 频率表格 */
.freq-table {
  width: 100%;
  border-collapse: collapse;
}

.freq-table th {
  text-align: left;
  padding: 12px;
  font-size: 12px;
  color: var(--text-muted);
  background: #f8fafc;
}

.freq-table td {
  padding: 12px;
  font-size: 14px;
  border-top: 1px solid var(--border-color);
  font-family: 'Courier New', Courier, monospace;
}

.empty-guide {
  text-align: center;
  padding: 60px;
  color: var(--text-muted);
  opacity: 0.6;
}

.empty-guide .icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.5s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>