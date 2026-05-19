<template>
  <div class="enrichment-page">
    <!-- 顶部步骤进度：展示当前处于分析完成状态 -->
    <StepFlow currentStep="ANALYSIS_DONE" />

    <div class="analysis-layout">
      <!-- 左侧：参数配置面板 -->
      <aside class="config-side">
        <div class="config-card">
          <h3 class="section-title">分析配置</h3>

          <div class="form-group">
            <label>物种 (Species)</label>
            <select v-model="params.species" class="custom-select">
              <option value="hsa">Homo sapiens (人)</option>
              <option value="mmu">Mus musculus (小鼠)</option>
            </select>
          </div>

          <div class="form-group">
            <label>显著性阈值 (P-value <)</label>
            <input type="number" v-model="params.pThreshold" step="0.01" class="custom-input" />
          </div>

          <div class="form-group">
            <label>背景基因集</label>
            <div class="checkbox-list">
              <label><input type="checkbox" v-model="params.db" value="GO" /> GO Ontology</label>
              <label><input type="checkbox" v-model="params.db" value="KEGG" /> KEGG Pathway</label>
            </div>
          </div>

          <button
              class="primary-btn"
              :disabled="loading"
              @click="runEnrichment"
          >
            {{ loading ? '计算中...' : '开始富集分析' }}
          </button>
        </div>

        <!-- 统计摘要 -->
        <div class="summary-card" v-if="enrichData.length">
          <div class="summary-item">
            <span class="label">显著通路数</span>
            <span class="value">{{ enrichData.length }}</span>
          </div>
        </div>
      </aside>

      <!-- 右侧：可视化图表与结果表 -->
      <main class="result-main">
        <!-- 气泡图卡片 -->
        <div class="viz-card">
          <div class="card-header">
            <h4>富集气泡图 (Dot Plot)</h4>
            <StatusTag v-if="enrichData.length" type="success" label="已更新" />
          </div>

          <div class="chart-wrapper">
            <ChartBox
                v-if="enrichData.length"
                :options="bubbleOptions"
                height="500px"
            />
            <div v-else-if="!loading" class="empty-state">
              <p>暂无分析数据，请调整参数后点击“开始分析”</p>
            </div>
            <div v-else class="loading-state">
              <div class="spinner"></div>
              <p>正在查询生物信息学数据库...</p>
            </div>
          </div>
        </div>

        <!-- 详细结果表格 -->
        <div class="table-card" v-if="enrichData.length">
          <div class="card-header">
            <h4>详细通路列表</h4>
          </div>
          <SNPTable
              :data="tableFormattedData"
              mode="result"
              title="Pathway Enrichment List"
          />
        </div>
      </main>
    </div>

    <!-- 全局进度遮罩 -->
    <LoadingOverlay
        :visible="loading"
        title="正在执行富集分析"
        :description="`正在对显著 SNP 关联基因进行超几何分布检验...`"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useAnalysisStore } from '@/store/analysis'
import { useProjectStore } from '@/store/project'
import { getGOAPI, getKEGGAPI } from '@/api/analysis'
import StepFlow from '@/components/StepFlow.vue'
import ChartBox from '@/components/ChartBox.vue'
import SNPTable from '@/components/SNPTable.vue'
import StatusTag from '@/components/StatusTag.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'

const analysisStore = useAnalysisStore()
const projectStore = useProjectStore()
const loading = ref(false)
const enrichData = ref<any[]>([])

const params = reactive({
  species: 'hsa',
  pThreshold: 0.05,
  db: ['GO', 'KEGG']
})

const runEnrichment = async () => {
  if (!projectStore.currentProjectId) {
    alert('请先创建或选择一个项目')
    return
  }
  loading.value = true
  try {
    const results: any[] = []
    if (params.db.includes('GO')) {
      try {
        const goRes = await getGOAPI(projectStore.currentProjectId)
        if (Array.isArray(goRes)) {
          results.push(...goRes.map((i: any) => ({
            term: i.Term || i.term || '',
            count: parseInt(i['Overlap'] || i.overlap || '0') || 0,
            pvalue: parseFloat(i['Adjusted P-value'] || i.pvalue || 1),
            ratio: parseFloat(i['Odds Ratio'] || i.ratio || '0') || 0
          })))
        }
      } catch (e) { console.error('GO富集失败', e) }
    }
    if (params.db.includes('KEGG')) {
      try {
        const keggRes = await getKEGGAPI(projectStore.currentProjectId)
        if (Array.isArray(keggRes)) {
          results.push(...keggRes.map((i: any) => ({
            term: i.Term || i.term || '',
            count: parseInt(i['Overlap'] || i.overlap || '0') || 0,
            pvalue: parseFloat(i['Adjusted P-value'] || i.pvalue || 1),
            ratio: parseFloat(i['Odds Ratio'] || i.ratio || '0') || 0
          })))
        }
      } catch (e) { console.error('KEGG富集失败', e) }
    }
    enrichData.value = results.sort((a, b) => a.pvalue - b.pvalue)
  } catch (e) {
    console.error('富集分析失败', e)
    alert('富集分析失败，请确保已完成GWAS分析')
  } finally {
    loading.value = false
  }
}

// 格式化数据给 SNPTable (复用组件)
const tableFormattedData = computed(() => {
  return enrichData.value.map(item => ({
    rsid: item.term,   // 借用 ID 列显示通路名
    chr: 'N/A',
    pos: item.count,   // 借用位置列显示基因计数
    p: item.pvalue,
    a1: item.ratio.toFixed(2),
    a2: 'Detail'
  }))
})

// 配置气泡图
const bubbleOptions = computed(() => ({
  tooltip: { trigger: 'item' },
  grid: { left: '20%', right: '10%', bottom: '15%' },
  xAxis: { name: 'Gene Ratio', splitLine: { show: true } },
  yAxis: {
    type: 'category',
    data: enrichData.value.map(i => i.term),
    axisLabel: { interval: 0, fontSize: 11 }
  },
  series: [{
    type: 'scatter',
    data: enrichData.value.map(i => [i.ratio, i.term, i.count, i.pvalue]),
    symbolSize: (data: any) => data[2] * 0.8, // 气泡大小对应 Count
    itemStyle: {
      color: (params: any) => {
        const p = params.data[3]
        return p < 0.01 ? '#ef4444' : '#fb923c' // 颜色深浅对应显著性
      },
      opacity: 0.8
    }
  }]
}))
</script>

<style scoped>
.enrichment-page {
  max-width: 1300px;
  margin: 0 auto;
}

.analysis-layout {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 20px;
  margin-top: 24px;
}

.config-side {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.config-card, .summary-card {
  background: var(--card-bg);
  padding: 20px;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
}

.section-title {
  font-size: 16px;
  margin-bottom: 20px;
  color: var(--text-main);
  border-left: 4px solid var(--primary-color);
  padding-left: 10px;
}

.form-group {
  margin-bottom: 18px;
}

.form-group label {
  display: block;
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.custom-select, .custom-input {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.checkbox-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 13px;
}

.primary-btn {
  width: 100%;
  padding: 12px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.primary-btn:disabled {
  background: var(--border-color);
  cursor: not-allowed;
}

.result-main {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.viz-card, .table-card {
  background: var(--card-bg);
  padding: 24px;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-wrapper {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state {
  color: var(--text-muted);
  text-align: center;
}
</style>