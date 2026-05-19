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

          <button
              class="recalc-btn"
              :disabled="loading"
              @click="handleRecalculate"
          >
            {{ loading ? '计算中...' : '重新运行 PCA' }}
          </button>
        </div>

        <div class="outlier-card" v-if="outliers.length > 0">
          <h4>异常值检测 (Outliers)</h4>
          <p class="hint">系统识别出 {{ outliers.length }} 个偏离主群体的样本。</p>
          <div class="outlier-list">
            <div v-for="s in outliers" :key="s.id" class="outlier-item">
              <span>{{ s.name }}</span>
              <button class="remove-btn" @click="removeOutlier(s.id)">排除</button>
            </div>
          </div>
          <button class="batch-remove" @click="removeAllOutliers">一键排除所有异常点</button>
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

          <div class="chart-container">
            <ChartBox
                v-if="pcaOption"
                :option="pcaOption"
                height="500px"
            />
            <div v-else class="empty-placeholder">
              <p>点击上方按钮加载 PCA 数据</p>
            </div>
          </div>

          <div class="pca-explanation">
            <strong>结果指出：</strong>
            <span>
              当前群体 λGC 初步预测为 1.02。
              如果散点图出现明显的"团簇"分离，说明样本存在亚群结构，必须在 GWAS 模型中包含这些 PC 作为协变量。
            </span>
          </div>
        </div>

        <div class="scree-card">
          <h4>碎石图 (Scree Plot) - 特征值贡献度</h4>
          <div class="scree-bars">
            <div
                v-for="(val, idx) in varianceExplained"
                :key="idx"
                class="bar-wrapper"
                :title="`PC${idx+1}: ${val}%`"
            >
              <div class="bar" :style="{ height: val * 4 + 'px' }"></div>
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
  if (!projectStore.currentProjectId) return
  loading.value = true
  try {
    const data = await getPlotDataAPI(projectStore.currentProjectId, 'pca')
    const points = data.x.map((x: number, i: number) => [x, data.y[i]])
    pcaOption.value = {
      xAxis: { name: `PC${xAxis.value}` },
      yAxis: { name: `PC${yAxis.value}` },
      series: [{ type: 'scatter', data: points }]
    }
  } catch (e) {
    console.error('PCA数据加载失败', e)
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
  gap: 24px;
  margin-top: 24px;
}

.card-config, .outlier-card {
  background: var(--card-bg);
  padding: 20px;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
  margin-bottom: 20px;
}

.config-item {
  margin-bottom: 16px;
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
}

.config-item input, .axis-select select {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.axis-select {
  display: flex;
  align-items: center;
  gap: 10px;
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

.outlier-list {
  margin: 12px 0;
  max-height: 180px;
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
  padding: 2px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
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
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 10px;
}

.card-header h4 {
  margin: 0;
  font-size: 15px;
}

.chart-container {
  min-height: 400px;
  position: relative;
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
  margin-top: 16px;
  padding: 12px;
  background: #f0f9ff;
  border-left: 4px solid #0ea5e9;
  font-size: 13px;
  line-height: 1.6;
  border-radius: 0 4px 4px 0;
}

.scree-bars {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  height: 120px;
  padding-top: 20px;
}

.bar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.bar {
  width: 30px;
  background: var(--primary-color);
  border-radius: 4px 4px 0 0;
  transition: height 0.3s ease;
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
}

@media (max-width: 900px) {
  .pca-layout {
    grid-template-columns: 1fr;
  }
}
</style>
