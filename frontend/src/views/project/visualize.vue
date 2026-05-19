<template>
  <div class="visualize-page">
    <!-- 1. 顶部切换 Tab：采用生信分析常用分类 -->
    <div class="viz-nav-wrapper">
      <div class="viz-tabs">
        <button
            v-for="t in tabs"
            :key="t.key"
            :class="['tab-btn', { active: tab === t.key }]"
            @click="tab = t.key"
        >
          <span class="tab-icon">{{ t.icon }}</span>
          {{ t.label }}
        </button>
      </div>
      <div class="export-actions">
        <button class="export-btn" @click="downloadReport">📑 导出分析报告</button>
      </div>
    </div>

    <div class="viz-layout">
      <!-- 2. 主图表区域 -->
      <main class="viz-main">
        <div class="chart-card">
          <div class="chart-header">
            <h4>{{ currentTabLabel }} 可视化展示</h4>
            <div v-if="tab === 'manhattan'" class="threshold-tag">
              Threshold: <span class="math">5 \times 10^{-8}</span>
            </div>
            <div v-if="tab === 'qq'" class="lambda-tag">
              Genomic Inflation (λ): <strong>{{ lambdaGC }}</strong>
            </div>
          </div>

          <div class="chart-body">
            <ChartBox
                :option="option"
                :style="{ height: '500px' }"
                @chart-click="handleSnpClick"
            />
          </div>
        </div>

        <!-- 3. 下方联动面板：SNP 注释或显著列表 -->
        <section class="detail-section">
          <!-- SNP 实时注释详情 -->
          <div v-if="info" class="annotation-panel">
            <div class="panel-title">
              <span class="rsid-badge">{{ info.rsid }}</span>
              <span class="gene-name">Target Gene: <i>{{ info.gene }}</i></span>
            </div>
            <div class="annotation-grid">
              <div class="info-item"><b>位点类型:</b> {{ info.consequence || 'Intergenic' }}</div>
              <div class="info-item"><b>染色体位置:</b> Chr{{ info.chr }}:{{ info.pos }}</div>
              <div class="info-item"><b>等位基因:</b> {{ info.ref }}/{{ info.alt }}</div>
              <div class="info-item">
                <a :href="`https://www.ncbi.nlm.nih.gov/snp/${info.rsid}`" target="_blank" class="ncbi-link">
                  View in NCBI ↗
                </a>
              </div>
            </div>
          </div>

          <!-- 显著 SNP 数据表格 -->
          <div v-if="tab === 'manhattan' && sigList.length" class="table-card">
            <div class="table-header">
              <h5>显著位点列表 (P < 5e-8)</h5>
            </div>
            <div class="table-wrapper">
              <table class="data-table">
                <thead>
                <tr>
                  <th>rsID</th>
                  <th>Chr</th>
                  <th>Position (BP)</th>
                  <th>P-value</th>
                  <th>Annotation</th>
                </tr>
                </thead>
                <tbody>
                <tr v-for="s in sigList" :key="s.ID" @click="fetchSnpDetail(s.ID)" class="clickable-row">
                  <td><b>{{ s.ID }}</b></td>
                  <td>{{ s.CHR }}</td>
                  <td>{{ s.BP.toLocaleString() }}</td>
                  <td class="p-val">{{ s.P.toExponential(2) }}</td>
                  <td><span class="gene-tag">{{ s.GENE || 'Pending' }}</span></td>
                </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </main>

      <!-- 4. 右侧辅助：分析结论摘要 -->
      <aside class="viz-summary">
        <div class="summary-card">
          <h5>📊 统计摘要</h5>
          <div class="summary-stat">
            <label>Total Variants</label>
            <span>8,421,092</span>
          </div>
          <div class="summary-stat">
            <label>Significant Loci</label>
            <span class="highlight">{{ sigList.length }}</span>
          </div>
          <hr />
          <div class="summary-conclusion">
            <h6>💡 专家建议</h6>
            <p v-if="lambdaGC > 1.05" class="warning">
              检测到 λ 较大，建议检查 PCA 协变量是否已完全包含。
            </p>
            <p v-else>
              群体分层控制良好，显著位点具有较高的可信度。
            </p>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import ChartBox from '@/components/ChartBox.vue'
import { useProjectStore } from '@/store/project'
import {
  getManhattanAPI,
  getQQAPI,
  getPCAAPI,
  getAnnotationAPI,
  getSignificantSNPAPI,
  getGOAPI,
  getKEGGAPI
} from '@/api/analysis'

const projectStore = useProjectStore()

const tabs = [
  { key: 'manhattan', label: '曼哈顿图', icon: '🏙️' },
  { key: 'qq', label: 'QQ图', icon: '📈' },
  { key: 'pca', label: 'PCA分析', icon: '📍' },
  { key: 'go', label: 'GO富集', icon: '🧬' },
  { key: 'kegg', label: 'KEGG通路', icon: '🧪' }
] as const

const tab = ref<typeof tabs[number]['key']>('manhattan')
const option = ref<any>({})
const info = ref<any>(null)
const sigList = ref<any[]>([])
const lambdaGC = ref(1.02)

const currentTabLabel = computed(() => tabs.find(t => t.key === tab.value)?.label)

const handleSnpClick = (params: any) => {
  const rsid = params.data?.rsid || params.name
  if (rsid) fetchSnpDetail(rsid)
}

const fetchSnpDetail = async (rsid: string) => {
  try {
    const res = await getAnnotationAPI(rsid)
    info.value = res
    window.scrollTo({ top: 600, behavior: 'smooth' })
  } catch (e) {
    console.error('获取SNP注释失败', e)
  }
}

watch(tab, async (newTab) => {
  if (!projectStore.currentProjectId) return
  const pid = projectStore.currentProjectId

  info.value = null
  option.value = {}

  if (newTab === 'manhattan') {
    const [manhattanRes, sigRes] = await Promise.all([
      getManhattanAPI(pid),
      getSignificantSNPAPI(pid)
    ])
    const manhattanData = manhattanRes
    const snpList = Array.isArray(sigRes) ? sigRes : (sigRes.data || [])
    sigList.value = snpList
    option.value = {
      tooltip: { trigger: 'item' },
      xAxis: { type: 'value', name: 'Genomic Position' },
      yAxis: { type: 'value', name: '-log10(p)' },
      series: manhattanData.groups.map((g: any, idx: number) => ({
        name: `Chr ${g.chr}`,
        type: 'scatter',
        data: g.data.map((d: any) => ({
          value: d.value,
          rsid: d.rsid,
          p: d.p,
          significant: d.significant
        })),
        symbolSize: (val: any, params: any) => params.data.significant ? 8 : 4,
        itemStyle: { color: idx % 2 === 0 ? '#3b82f6' : '#64748b' }
      }))
    }
  }

  if (newTab === 'qq') {
    const data = await getQQAPI(pid)
    lambdaGC.value = data.lambda_gc
    option.value = {
      xAxis: { name: 'Expected -log10(P)' },
      yAxis: { name: 'Observed -log10(P)' },
      series: [
        { type: 'line', data: [[0, 0], [data.expected[data.expected.length - 1] || 8, data.expected[data.expected.length - 1] || 8]], lineStyle: { type: 'dashed', color: '#aaa' } },
        { type: 'scatter', data: data.expected.map((e: number, i: number) => [e, data.observed[i]]) }
      ]
    }
  }

  if (newTab === 'pca') {
    const data = await getPCAAPI(pid)
    const points = data.x.map((x: number, i: number) => [x, data.y[i]])
    option.value = {
      xAxis: { name: 'PC1' },
      yAxis: { name: 'PC2' },
      series: [{ type: 'scatter', data: points }]
    }
  }

  if (newTab === 'go') {
    const data = await getGOAPI(pid)
    if (Array.isArray(data) && data.length > 0) {
      option.value = {
        tooltip: { trigger: 'item' },
        grid: { left: '25%', right: '10%', bottom: '15%' },
        xAxis: { name: 'Gene Ratio', type: 'value' },
        yAxis: { type: 'category', data: data.map((i: any) => i.Term || i.term || '').slice(0, 15).reverse(), axisLabel: { interval: 0, fontSize: 11 } },
        series: [{
          type: 'scatter',
          data: data.map((i: any) => {
            const overlap = parseFloat(i['Overlap'] || i.overlap || '1/10')
            const ratio = typeof overlap === 'number' ? overlap : (eval(overlap) || 0.1)
            return [ratio, i.Term || i.term || '', parseFloat(i['Adjusted P-value'] || i.pvalue || 0.05), i['Adjusted P-value'] || '']
          }).slice(0, 15).reverse(),
          symbolSize: (val: any) => Math.max(10, val[0] * 200),
          itemStyle: { color: (p: any) => parseFloat(p.data[3]) < 0.01 ? '#ef4444' : '#fb923c', opacity: 0.8 }
        }]
      }
    }
  }

  if (newTab === 'kegg') {
    const data = await getKEGGAPI(pid)
    if (Array.isArray(data) && data.length > 0) {
      option.value = {
        tooltip: { trigger: 'item' },
        grid: { left: '25%', right: '10%', bottom: '15%' },
        xAxis: { name: 'Gene Ratio', type: 'value' },
        yAxis: { type: 'category', data: data.map((i: any) => i.Term || i.term || '').slice(0, 15).reverse(), axisLabel: { interval: 0, fontSize: 11 } },
        series: [{
          type: 'scatter',
          data: data.map((i: any) => {
            const overlap = parseFloat(i['Overlap'] || i.overlap || '1/10')
            const ratio = typeof overlap === 'number' ? overlap : (eval(overlap) || 0.1)
            return [ratio, i.Term || i.term || '', parseFloat(i['Adjusted P-value'] || i.pvalue || 0.05), i['Adjusted P-value'] || '']
          }).slice(0, 15).reverse(),
          symbolSize: (val: any) => Math.max(10, val[0] * 200),
          itemStyle: { color: (p: any) => parseFloat(p.data[3]) < 0.01 ? '#ef4444' : '#fb923c', opacity: 0.8 }
        }]
      }
    }
  }
}, { immediate: true })

const downloadReport = () => { /* 导出 PDF 逻辑 */ }
</script>

<style scoped>
.visualize-page { max-width: 1440px; margin: 0 auto; padding: 20px; }

/* Tab 导航 */
.viz-nav-wrapper {
  display: flex; justify-content: space-between; align-items: center;
  background: #fff; padding: 12px 24px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.viz-tabs { display: flex; gap: 8px; }
.tab-btn {
  padding: 10px 20px; border: none; background: #f1f5f9; border-radius: 8px;
  cursor: pointer; font-weight: 500; transition: all 0.3s;
}
.tab-btn.active { background: var(--primary-color); color: white; }

/* 布局控制 */
.viz-layout { display: grid; grid-template-columns: 1fr 300px; gap: 24px; margin-top: 24px; }

.chart-card { background: white; border-radius: 12px; border: 1px solid #e2e8f0; padding: 24px; }
.chart-header { display: flex; justify-content: space-between; margin-bottom: 20px; }

/* 注释面板 */
.annotation-panel {
  background: #f8fafc; border: 1px solid var(--primary-color); border-radius: 12px;
  padding: 20px; margin-bottom: 24px;
}
.rsid-badge { background: var(--primary-color); color: white; padding: 4px 12px; border-radius: 20px; font-weight: bold; margin-right: 15px; }
.annotation-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-top: 15px; font-size: 14px; }

/* 数据表格 */
.table-card { background: white; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { background: #f8fafc; padding: 12px; text-align: left; font-size: 13px; color: #64748b; }
.data-table td { padding: 12px; border-top: 1px solid #f1f5f9; font-size: 14px; }
.clickable-row { cursor: pointer; transition: background 0.2s; }
.clickable-row:hover { background: #f0f9ff; }
.p-val { font-family: 'Courier New', monospace; color: #e11d48; font-weight: 600; }

/* 右侧摘要 */
.summary-card { background: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; position: sticky; top: 20px; }
.summary-stat { display: flex; justify-content: space-between; margin: 12px 0; font-size: 14px; }
.highlight { color: var(--primary-color); font-weight: bold; font-size: 18px; }
.warning { color: #e11d48; font-size: 13px; line-height: 1.4; }
.math { font-family: "Times New Roman", serif; font-style: italic; }
</style>