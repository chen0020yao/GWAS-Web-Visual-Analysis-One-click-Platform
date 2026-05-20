<template>
  <div class="analyze-page">
    <StepFlow currentStep="QC_DONE" />

    <div class="analyze-layout">
      <aside class="config-panel">
        <div class="panel-header">
          <h3>关联分析配置</h3>
        </div>

        <div class="form-group">
          <label>统计模型 (Model)</label>
          <select v-model="analysisStore.modelParams.method" class="custom-select">
            <option value="GLM">GLM (一般线性模型)</option>
            <option value="MLM">MLM (混合线性模型 - 推荐)</option>
            <option value="FarmCPU">FarmCPU (迭代多位点模型)</option>
          </select>
          <p class="field-hint">MLM 能更好地校正群体结构和亲缘关系。</p>
        </div>

        <div class="form-group">
          <label>协变量 (Covariates)</label>
          <div class="checkbox-group">
            <label><input type="checkbox" checked disabled /> PCA (前 {{ analysisStore.modelParams.pcaNum }} 个主成分)</label>
            <label><input type="checkbox" v-model="includeSex" /> 性别 (Sex)</label>
            <label><input type="checkbox" v-model="includeAge" /> 年龄 (Age)</label>
          </div>
        </div>

        <div class="form-group">
          <label>显著性阈值 (P-value Cutoff)</label>
          <div class="input-with-unit">
            <span>5e-</span>
            <input type="number" v-model="pBase" min="1" max="10" />
          </div>
        </div>

        <button
            class="run-btn"
            :disabled="pipelineStore.taskStatus === 'RUNNING'"
            @click="handleStartGWAS"
        >
          <span v-if="pipelineStore.taskStatus !== 'RUNNING'">开始关联分析</span>
          <span v-else>分析运行中...</span>
        </button>
      </aside>

      <main class="status-panel">
        <div class="card-header">
          <h4>分析任务状态</h4>
          <StatusTag
              :type="statusTagType"
              :label="pipelineStore.taskStatus"
          />
        </div>

        <div class="progress-section">
          <div class="progress-info">
            <span>{{ pipelineStore.currentLog || '准备就绪' }}</span>
            <span>{{ pipelineStore.progress }}%</span>
          </div>
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" :style="{ width: pipelineStore.progress + '%' }"></div>
          </div>
        </div>

        <div class="console-box">
          <div class="console-header">
            <span>Console Output</span>
            <button class="clear-btn" @click="clearLogs">清除</button>
          </div>
          <div class="console-content" ref="logScroll">
            <div v-for="(log, index) in logs" :key="index" class="log-line">
              <span class="log-time">[{{ new Date().toLocaleTimeString() }}]</span>
              <span class="log-text">{{ log }}</span>
            </div>
            <div v-if="pipelineStore.errorDetail" class="log-line error">
              <span class="log-text">错误详情: {{ pipelineStore.errorDetail }}</span>
            </div>
            <div v-if="logs.length === 0" class="log-placeholder">等待任务启动...</div>
          </div>
        </div>

        <div v-if="pipelineStore.taskStatus === 'SUCCESS'" class="success-action">
          <p>分析已顺利完成！现在可以查看曼哈顿图和结果列表。</p>
          <button @click="$router.push('/project/visualize')">前往结果可视化</button>
        </div>
      </main>
    </div>

    <LoadingOverlay
        :visible="pipelineStore.taskStatus === 'RUNNING'"
        title="GWAS 计算任务运行中"
        :description="pipelineStore.currentLog"
        :progress="pipelineStore.progress"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed, onMounted } from 'vue'
import { useAnalysisStore } from '@/store/analysis'
import { usePipelineStore } from '@/store/pipeline'
import { useProjectStore } from '@/store/project'
import { runGWASAnalysisAPI } from '@/api/analysis'
import { updateProjectAPI } from '@/api/project'
import StepFlow from '@/components/StepFlow.vue'
import StatusTag from '@/components/StatusTag.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'

const analysisStore = useAnalysisStore()
const pipelineStore = usePipelineStore()
const projectStore = useProjectStore()

onMounted(() => {
  pipelineStore.resetPipeline()
})

const pBase = ref(8)
const includeSex = ref(true)
const includeAge = ref(true)
const logs = ref<string[]>([])
const logScroll = ref<HTMLElement | null>(null)

const statusTagType = computed(() => {
  const map: Record<string, string> = {
    'SUCCESS': 'success',
    'FAILED': 'error',
    'RUNNING': 'primary',
    'WAITING': 'warning'
  }
  return map[pipelineStore.taskStatus] || 'info'
})

watch(() => pipelineStore.currentLog, (newLog) => {
  if (newLog) {
    logs.value.push(newLog)
    nextTick(() => {
      if (logScroll.value) {
        logScroll.value.scrollTop = logScroll.value.scrollHeight
      }
    })
  }
})

const handleStartGWAS = async () => {
  if (!projectStore.currentProjectId) {
    alert('请先选择或创建一个项目')
    return
  }

  pipelineStore.taskStatus = 'RUNNING'
  logs.value = ['初始化计算环境...', '检测表型文件格式...', '加载基因型索引...']

  try {
    const res: any = await runGWASAnalysisAPI({
      projectId: projectStore.currentProjectId,
      model: analysisStore.modelParams.method,
      covariates: analysisStore.modelParams.covariates
    })

    logs.value.push(res?.msg || 'GWAS分析任务已提交完成')
    pipelineStore.taskStatus = 'SUCCESS'
    projectStore.step = 'ANALYSIS_DONE'
    try {
      await updateProjectAPI(projectStore.currentProjectId, { current_step: 'ANALYSIS_DONE' })
      console.log('[GWAS] step已同步到DB')
    } catch (e: any) {
      console.error('[GWAS] DB更新失败:', e?.message || e)
    }

  } catch (e: any) {
    console.error('GWAS分析失败', e)
    pipelineStore.taskStatus = 'FAILED'
    pipelineStore.errorDetail = e.message || '分析任务执行失败'
    logs.value.push(`错误: ${e.message || '未知错误'}`)
  }
}

const clearLogs = () => {
  logs.value = []
}
</script>

<style scoped>
.analyze-page {
  max-width: 1300px;
  margin: 0 auto;
}

.analyze-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  margin-top: 24px;
}

.config-panel {
  background: var(--card-bg);
  padding: 24px;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
  height: fit-content;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 10px;
}

.custom-select {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: 13px;
}

.input-with-unit {
  display: flex;
  align-items: center;
  gap: 8px;
}

.input-with-unit input {
  width: 60px;
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.run-btn {
  width: 100%;
  padding: 14px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.run-btn:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

.field-hint {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
}

.status-panel {
  background: var(--card-bg);
  padding: 24px;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-section {
  padding: 20px;
  background: #f8fafc;
  border-radius: 8px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  margin-bottom: 10px;
}

.progress-bar-bg {
  height: 12px;
  background: #e2e8f0;
  border-radius: 6px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(to right, #3b82f6, #42b983);
  transition: width 0.3s ease;
}

.console-box {
  background: #1e293b;
  border-radius: 8px;
  overflow: hidden;
}

.console-header {
  background: #334155;
  padding: 10px 16px;
  display: flex;
  justify-content: space-between;
  color: #e2e8f0;
  font-size: 12px;
}

.console-content {
  height: 300px;
  overflow-y: auto;
  padding: 16px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  color: #94a3b8;
}

.log-line { margin-bottom: 6px; }
.log-time { color: #64748b; margin-right: 10px; }
.log-line.error { color: #f87171; }
.clear-btn { background: none; border: none; color: #94a3b8; cursor: pointer; }
.clear-btn:hover { color: white; }

.success-action {
  text-align: center;
  padding: 20px;
  background: #ecfdf5;
  border: 1px solid #10b981;
  border-radius: 8px;
}

.success-action button {
  background: #10b981;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  margin-top: 10px;
  cursor: pointer;
}
</style>
