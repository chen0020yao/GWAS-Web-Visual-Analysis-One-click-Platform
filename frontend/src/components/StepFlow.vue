<template>
  <div class="step-flow-container">
    <div class="steps-wrapper">
      <div
          v-for="(step, index) in steps"
          :key="step.key"
          class="step-item"
          :class="[getStepStatus(step.key, index)]"
      >
        <!-- 步骤线条 -->
        <div v-if="index !== 0" class="step-line"></div>

        <!-- 步骤图标与索引 -->
        <div class="step-node">
          <div class="node-circle">
            <span v-if="isCompleted(index)">CheckmarkIcon</span>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <div class="node-content">
            <div class="step-title">{{ step.title }}</div>
            <div class="step-desc">{{ step.desc }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

/**
 * 步骤流转定义
 * IDLE -> UPLOADED -> QC_DONE -> ANALYSIS_DONE
 */
const props = defineProps({
  currentStep: {
    type: String,
    default: 'IDLE'
  }
})

const steps = [
  { key: 'IDLE', title: '数据上传', desc: '上传 VCF/Plink 文件' },
  { key: 'UPLOADED', title: '数据清洗', desc: '质控与格式转换' },
  { key: 'QC_DONE', title: '关联分析', desc: '运行 GWAS 模型' },
  { key: 'ANALYSIS_DONE', title: '可视化', desc: '结果图表展示' }
]

const stepOrder = ['IDLE', 'UPLOADED', 'QC_DONE', 'ANALYSIS_DONE']

// 获取当前步骤的索引
const currentIndex = computed(() => stepOrder.indexOf(props.currentStep))

// 判断步骤是否已完成
const isCompleted = (index: number) => {
  return index < currentIndex.value || props.currentStep === 'ANALYSIS_DONE'
}

// 获取步骤状态类名
const getStepStatus = (key: string, index: number) => {
  if (index < currentIndex.value) return 'status-completed'
  if (index === currentIndex.value) return 'status-active'
  return 'status-locked' // 灰色锁定状态
}
</script>

<style scoped>
.step-flow-container {
  padding: 30px 20px;
  background: var(--card-bg);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
  margin-bottom: 24px;
}

.steps-wrapper {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.step-item {
  flex: 1;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 步骤间的连接线 */
.step-line {
  position: absolute;
  top: 18px;
  left: -50%;
  right: 50%;
  height: 2px;
  background: var(--border-color);
  z-index: 1;
}

.status-completed .step-line,
.status-active .step-line {
  background: var(--primary-color);
}

.step-node {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

/* 节点圆圈 */
.node-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--card-bg);
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: var(--text-muted);
  transition: all 0.3s;
  margin-bottom: 12px;
}

.step-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.step-desc {
  font-size: 12px;
  color: var(--text-muted);
  max-width: 120px;
}

/* --- 状态样式流转 --- */

/* 1. 锁定态 (灰色) */
.status-locked .node-circle {
  background: #f8fafc;
  color: var(--text-muted);
}

/* 2. 激活态 (黑色/主色) */
.status-active .node-circle {
  border-color: var(--primary-color);
  color: var(--primary-color);
  box-shadow: 0 0 0 4px rgba(66, 185, 131, 0.1);
}

.status-active .step-title {
  color: var(--text-main); /* 由灰变黑 */
}

/* 3. 完成态 (绿色) */
.status-completed .node-circle {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

.status-completed .step-title {
  color: var(--primary-color);
}
</style>