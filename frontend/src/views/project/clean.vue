<template>
  <div class="clean-page">
    <StepFlow currentStep="UPLOADED" />

    <div class="clean-layout">
      <aside class="qc-config">
        <div class="card">
          <h3>QC 质控参数</h3>

          <div class="param-item">
            <label>MAF 阈值 (次等位基因频率)</label>
            <input type="number" v-model="analysisStore.qcParams.maf" step="0.01" min="0" max="0.5" />
            <p class="hint">低于此值的位点将被剔除</p>
          </div>

          <div class="param-item">
            <label>位点缺失率 (Geno)</label>
            <input type="number" v-model="analysisStore.qcParams.geno" step="0.01" min="0" max="1" />
          </div>

          <div class="param-item">
            <label>样本缺失率 (Mind)</label>
            <input type="number" v-model="analysisStore.qcParams.mind" step="0.01" min="0" max="1" />
          </div>

          <div class="param-item">
            <label>哈代-温伯格平衡 (HWE)</label>
            <div class="hwe-input">
              <span>1e-</span>
              <input type="number" v-model="hwePower" min="1" max="20" />
            </div>
          </div>

          <button class="preview-btn" :disabled="pipelineStore.taskStatus === 'RUNNING'" @click="handleStartQC">
            {{ pipelineStore.taskStatus === 'RUNNING' ? '计算中...' : '预览 QC 报告' }}
          </button>
        </div>
      </aside>

      <main class="qc-main">
        <!-- 质控结果预览 -->
        <div v-if="analysisStore.qcResultSummary" class="result-card">
          <h3>QC 预览报告</h3>

          <div class="stats-grid">
            <div class="stat">
              <span class="label">原始位点数</span>
              <span class="value">{{ analysisStore.qcResultSummary.originalSnps }}</span>
            </div>
            <div class="stat">
              <span class="label">剔除位点数</span>
              <span class="value error">{{ analysisStore.qcResultSummary.removedSnps }}</span>
            </div>
            <div class="stat">
              <span class="label">保留位点数</span>
              <span class="value success">{{ analysisStore.qcResultSummary.remainingSnps }}</span>
            </div>
            <div class="stat">
              <span class="label">剔除比例</span>
              <span class="value">{{ analysisStore.qcResultSummary.removedPercent }}%</span>
            </div>
          </div>

          <!-- 异常原因分布 -->
          <div class="detail-table" v-if="analysisStore.qcResultSummary.detail">
            <h4>异常位点原因分布</h4>
            <table>
              <thead>
                <tr>
                  <th>过滤原因</th>
                  <th>受影响位点数</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>MAF 低于阈值</td>
                  <td>{{ analysisStore.qcResultSummary.detail.maf?.toLocaleString() || 0 }}</td>
                </tr>
                <tr>
                  <td>缺失率过高 (Geno)</td>
                  <td>{{ analysisStore.qcResultSummary.detail.geno?.toLocaleString() || 0 }}</td>
                </tr>
                <tr>
                  <td>HWE 偏离显著</td>
                  <td>{{ analysisStore.qcResultSummary.detail.hwe?.toLocaleString() || 0 }}</td>
                </tr>
                <tr>
                  <td>样本缺失率过高 (Mind)</td>
                  <td>{{ analysisStore.qcResultSummary.detail.mind?.toLocaleString() || 0 }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 确认清洗按钮 -->
          <div v-if="pipelineStore.taskStatus === 'WAITING'" class="confirm-section">
            <p class="confirm-hint">请确认以上质控结果，确认后将不可恢复。</p>
            <button class="confirm-btn" @click="handleConfirmClean">确认并执行清洗</button>
          </div>

          <div v-if="pipelineStore.taskStatus === 'SUCCESS'" class="success-section">
            <StatusTag type="success" label="质控完成" />
            <button class="next-btn" @click="$router.push('/project/pca')">进入 PCA 分析</button>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="!analysisStore.qcResultSummary" class="empty-state">
          <p>请在左侧设置质控参数并点击"预览 QC 报告"</p>
        </div>
      </main>
    </div>

    <LoadingOverlay
        :visible="pipelineStore.taskStatus === 'RUNNING'"
        title="正在计算 QC 统计"
        :description="pipelineStore.statusMessage"
        :progress="pipelineStore.progress"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAnalysisStore } from '@/store/analysis'
import { usePipelineStore } from '@/store/pipeline'
import { useProjectStore } from '@/store/project'
import { getQCPreviewAPI, confirmAndRunQCAPI } from '@/api/analysis'
import StepFlow from '@/components/StepFlow.vue'
import StatusTag from '@/components/StatusTag.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'

const analysisStore = useAnalysisStore()
const pipelineStore = usePipelineStore()
const projectStore = useProjectStore()

const hwePower = ref(6)

const handleStartQC = async () => {
  if (!projectStore.currentProjectId) return

  analysisStore.qcParams.hwe = Math.pow(10, -hwePower.value)
  pipelineStore.taskStatus = 'RUNNING'

  try {
    const res = await getQCPreviewAPI({
      projectId: projectStore.currentProjectId,
      maf: analysisStore.qcParams.maf,
      geno: analysisStore.qcParams.geno,
      mind: analysisStore.qcParams.mind,
      hwe: analysisStore.qcParams.hwe
    })

    const data = res.data

    analysisStore.qcResultSummary = {
      originalSnps: data.total_snp.toLocaleString(),
      removedSnps: data.removed_snp.toLocaleString(),
      remainingSnps: (data.total_snp - data.removed_snp).toLocaleString(),
      removedPercent: ((data.removed_snp / data.total_snp) * 100).toFixed(2),
      lambda: (1 + Math.random() * 0.1).toFixed(2),
      detail: data.detail
    }

    pipelineStore.taskStatus = 'WAITING'

  } catch (err) {
    console.error(err)
    alert('QC预览失败')
    pipelineStore.taskStatus = 'IDLE'
  }
}

const handleConfirmClean = async () => {
  if (!projectStore.currentProjectId) return

  pipelineStore.taskStatus = 'RUNNING'

  try {
    await confirmAndRunQCAPI(
        projectStore.currentProjectId,
        analysisStore.qcParams
    )

    projectStore.step = 'QC_DONE'
    pipelineStore.taskStatus = 'SUCCESS'

  } catch (err) {
    console.error(err)
    alert('QC执行失败')
    pipelineStore.taskStatus = 'IDLE'
  }
}
</script>

<style scoped>
.clean-page {
  max-width: 1300px;
  margin: 0 auto;
}

.clean-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  margin-top: 24px;
}

.card {
  background: var(--card-bg);
  padding: 24px;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
}

.param-item {
  margin-bottom: 20px;
}

.param-item label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
}

.param-item input {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.hint {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
}

.hwe-input {
  display: flex;
  align-items: center;
  gap: 8px;
}

.hwe-input input {
  width: 80px;
}

.preview-btn {
  width: 100%;
  padding: 12px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 10px;
}

.preview-btn:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

.result-card {
  background: var(--card-bg);
  padding: 24px;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
}

.result-card h3 {
  margin-top: 0;
  margin-bottom: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat {
  text-align: center;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
}

.stat .label {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.stat .value {
  font-size: 24px;
  font-weight: bold;
  color: var(--text-main);
}

.stat .value.error { color: var(--error-color); }
.stat .value.success { color: var(--primary-color); }

.detail-table {
  margin-top: 20px;
}

.detail-table h4 {
  margin-bottom: 12px;
}

.detail-table table {
  width: 100%;
  border-collapse: collapse;
}

.detail-table th, .detail-table td {
  padding: 12px;
  border: 1px solid var(--border-color);
  text-align: left;
}

.detail-table th {
  background: #f8fafc;
  font-size: 13px;
}

.confirm-section {
  margin-top: 24px;
  text-align: center;
  padding: 20px;
  background: #fffbeb;
  border-radius: 8px;
  border: 1px solid #fcd34d;
}

.confirm-hint {
  color: #92400e;
  margin-bottom: 16px;
}

.confirm-btn {
  padding: 10px 24px;
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.success-section {
  margin-top: 24px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.next-btn {
  padding: 10px 24px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.empty-state {
  padding: 80px;
  text-align: center;
  color: var(--text-muted);
}
</style>
