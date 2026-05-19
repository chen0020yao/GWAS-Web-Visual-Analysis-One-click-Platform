<template>
  <div class="pca-page">
    <StepFlow currentStep="QC_DONE" />

    <div class="pca-layout">
      <aside class="pca-aside">
        <div class="card-config">
          <h3>PCA 结构校正配置</h3>

          <div class="config-item">
            <label>主成分提取数量 (PCs)</label>
            <input type="number" v-model="analysisStore.modelParams.pcaNum" min="2" max="10" />
            <p class="hint">通常提取前 3-5 个 PC 即可校正大部分群体分层。</p>
          </div>

          <div class="config-item">
            <label>可视化轴</label>
            <div class="axis-select">
              <select v-model="xAxis">
                <option v-for="i in 10" :key="i" :value="i">PC{{ i }}</option>
              </select>
              <span>vs</span>
              <select v-model="yAxis">
                <option v-for="i in 10" :key="i" :value="i">PC{{ i }}</option>
              </select>
            </div>
          </div>

          <button class="recalc-btn" :disabled="loading" @click="handleRecalculate">
            {{ loading ? '计算中...' : '重新运行 PCA' }}
          </button>
        </div>

        <div class="outlier-card" v-if="outliers.length > 0">
          <h4>异常值检测 (Outliers)</h4>
          <p class="hint">系统识别出 {{ outliers.length }} 个偏离主群体的样本。</p>
          <div class="outlier-list">
            <div v-for="s in outliers" :key="s.id" class="outlier-item">
              <span>{{ s.name }}</span>
              <button class="remove-btn" type="button" @click.stop="removeOutlier(s.id)">排除</button>
            </div>
          </div>
          <button class="batch-remove" type="button" @click.stop="removeAllOutliers">一键排除所有异常点</button>
        </div>
        <div class="outlier-card" v-else>
          <h4>异常值检测 (Outliers)</h4>
          <p class="hint">未检测到异常样本，数据质量良好。</p>
        </div>
      </aside>

      <main class="pca-main">
        <div class="viz-card">
          <div class="card-header">
            <h4>群体结构分布图 (PC{{ xAxis }} vs PC{{ yAxis }})</h4>
            <div class="legend">
              <span class="dot cases"></span> 病例组
              <span class="dot controls"></span> 对照组
            </div>
          </div>

          <div class="chart-area">
            <ChartBox v-if="pcaOption" :option="pcaOption" height="420px" />
            <div v-else-if="chartError" class="empty-placeholder">
              <p>{{ chartError }}</p>
            </div>
            <div v-else class="empty-placeholder">
              <p>点击左侧"重新运行 PCA"加载数据</p>
            </div>
          </div>

          <div class="pca-explanation">
            <strong>结果指出：</strong>
            当前群体 λGC 初步预测为 1.02。如果散点图出现明显的"团簇"分离，说明样本存在亚群结构，必须在 GWAS 模型中包含这些 PC 作为协变量。
          </div>
        </div>

        <div class="scree-card">
          <h4>碎石图 (Scree Plot) - 特征值贡献度</h4>
          <div class="scree-container">
            <div
                v-for="(val, idx) in varianceExplained"
                :key="idx"
                class="bar-wrapper"
            >
              <div class="bar-value">{{ val }}%</div>
              <div class="bar-track">
                <div class="bar-fill" :style="{ height: (val / 50 * 100) + '%' }"></div>
              </div>
              <span class="bar-label">PC{{ idx + 1 }}</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAnalysisStore } from '@/store/analysis'
import { useProjectStore } from '@/store/project'
import { getPlotDataAPI } from '@/api/analysis'
import StepFlow from '@/components/StepFlow.vue'
import ChartBox from '@/components/ChartBox.vue'

const analysisStore = useAnalysisStore()
const projectStore = useProjectStore()
const loading = ref(false)
const pcaOption = ref<any>(null)
const chartError = ref('')

const xAxis = ref(1)
const yAxis = ref(2)

const outliers = ref([
  { id: 1, name: 'Sample_092' },
  { id: 2, name: 'Sample_154' },
  { id: 3, name: 'Sample_211' },
  { id: 4, name: 'Sample_402' }
])

const varianceExplained = ref([42.5, 18.2, 10.4, 5.1, 3.2, 2.1, 1.5, 1.1])

const removeOutlier = (id: number) => {
  outliers.value = outliers.value.filter(o => o.id !== id)
}

const removeAllOutliers = () => {
  outliers.value = []
}

const loadPcaData = async () => {
  loading.value = true
  chartError.value = ''

  if (!projectStore.currentProjectId) {
    // 没有项目数据时生成模拟 PCA 数据用于演示
    const n = 200
    const xs: number[] = []
    const ys: number[] = []
    for (let i = 0; i < n; i++) {
      xs.push((Math.random() - 0.5) * 0.2 + (i < n / 2 ? -0.05 : 0.05))
      ys.push((Math.random() - 0.5) * 0.15 + (i < n / 2 ? -0.03 : 0.03))
    }
    pcaOption.value = {
      tooltip: { trigger: 'item', formatter: (p: any) => `PC1: ${p.data[0].toFixed(4)}<br/>PC2: ${p.data[1].toFixed(4)}` },
      xAxis: { name: `PC${xAxis.value}`, type: 'value' },
      yAxis: { name: `PC${yAxis.value}`, type: 'value' },
      series: [{
        type: 'scatter',
        data: xs.map((x, i) => [x, ys[i]]),
        symbolSize: 6,
        itemStyle: { color: '#42b983', opacity: 0.6 }
      }]
    }
    loading.value = false
    return
  }

  try {
    const data = await getPlotDataAPI(projectStore.currentProjectId, 'pca')
    const points = data.x.map((x: number, i: number) => [x, data.y[i]])
    pcaOption.value = {
      tooltip: { trigger: 'item' },
      xAxis: { name: `PC${xAxis.value}`, type: 'value' },
      yAxis: { name: `PC${yAxis.value}`, type: 'value' },
      series: [{ type: 'scatter', data: points, symbolSize: 6 }]
    }
  } catch (e: any) {
    chartError.value = 'PCA 数据加载失败：' + (e.message || '请确认已上传数据并完成 QC')
  } finally {
    loading.value = false
  }
}

const handleRecalculate = () => {
  loadPcaData()
}

onMounted(() => {
  loadPcaData()
})
</script>

<style scoped>
.pca-page {
  max-width: 1400px;
  margin: 0 auto;
}

.pca-layout {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 20px;
  margin-top: 20px;
}

.card-config, .outlier-card {
  background: var(--card-bg);
  padding: 18px;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
  margin-bottom: 16px;
}

.config-item {
  margin-bottom: 14px;
}

.config-item label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 6px;
}

.hint {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
  line-height: 1.4;
}

.config-item input, .axis-select select {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: white;
}

.axis-select {
  display: flex;
  align-items: center;
  gap: 8px;
}

.recalc-btn {
  width: 100%;
  padding: 10px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}
.recalc-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.outlier-list {
  margin: 10px 0;
  max-height: 160px;
  overflow-y: auto;
}

.outlier-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  background: #fff1f2;
  border-radius: 4px;
  margin-bottom: 4px;
  font-size: 12px;
}

.remove-btn {
  background: none;
  border: 1px solid #fda4af;
  color: #e11d48;
  padding: 2px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
  position: relative;
  z-index: 1;
}
.remove-btn:hover {
  background: #e11d48;
  color: white;
}

.batch-remove {
  width: 100%;
  background: #fef2f2;
  border: 1px solid #fca5a5;
  color: #e11d48;
  padding: 8px;
  font-size: 12px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  position: relative;
  z-index: 1;
}
.batch-remove:hover {
  background: #e11d48;
  color: white;
}

.viz-card, .scree-card {
  background: var(--card-bg);
  padding: 20px;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
}

.card-header h4 {
  margin: 0;
  font-size: 15px;
}

.chart-area {
  min-height: 350px;
}

.legend {
  display: flex;
  gap: 12px;
  font-size: 12px;
  align-items: center;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}
.cases { background: #ef4444; }
.controls { background: #3b82f6; }

.pca-explanation {
  margin-top: 14px;
  padding: 10px 14px;
  background: #f0f9ff;
  border-left: 4px solid #0ea5e9;
  font-size: 13px;
  line-height: 1.6;
  border-radius: 0 4px 4px 0;
}

/* 碎石图 */
.scree-container {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  height: 200px;
  padding-top: 10px;
  gap: 8px;
}

.bar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  min-width: 0;
  max-width: 60px;
  height: 100%;
  justify-content: flex-end;
}

.bar-value {
  font-size: 10px;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.bar-track {
  width: 100%;
  height: 150px;
  background: #f1f5f9;
  border-radius: 4px 4px 0 0;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
}

.bar-fill {
  width: 100%;
  background: linear-gradient(to top, #42b983, #38a169);
  border-radius: 4px 4px 0 0;
  transition: height 0.4s ease;
  min-height: 4px;
}

.bar-label {
  font-size: 10px;
  margin-top: 6px;
  color: var(--text-muted);
}

.empty-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: var(--text-muted);
  font-size: 14px;
}
</style>
