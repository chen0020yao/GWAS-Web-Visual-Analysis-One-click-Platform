<template>
  <span
      class="status-tag"
      :class="[typeClass, sizeClass, { 'is-capsule': capsule }]"
  >
    <!-- 状态圆点：增强视觉识别度 -->
    <i v-if="dot" class="status-dot"></i>
    <slot>{{ label }}</slot>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

/**
 * 属性说明：
 * @prop type: 状态类型，对应不同的颜色预设
 * @prop label: 显示的文字
 * @prop size: 尺寸 (small, medium)
 * @prop dot: 是否显示左侧圆点
 * @prop capsule: 是否为圆角胶囊风格
 */
const props = defineProps({
  type: {
    type: String as () => 'primary' | 'success' | 'warning' | 'error' | 'info' | 'idle',
    default: 'info'
  },
  label: { type: String, default: '' },
  size: { type: String as () => 'small' | 'medium', default: 'small' },
  dot: { type: Boolean, default: true },
  capsule: { type: Boolean, default: false }
})

const typeClass = computed(() => `status-${props.type}`)
const sizeClass = computed(() => `size-${props.size}`)
</script>

<style scoped>
.status-tag {
  display: inline-flex;
  align-items: center;
  line-height: 1;
  font-weight: 500;
  white-space: nowrap;
  border-radius: var(--border-radius-sm);
  transition: all 0.2s;
}

/* 尺寸预设 */
.size-small {
  padding: 4px 8px;
  font-size: 12px;
}

.size-medium {
  padding: 6px 12px;
  font-size: 13px;
}

.is-capsule {
  border-radius: 20px;
}

/* 状态圆点 */
.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-right: 6px;
  background-color: currentColor;
}

/* --- 核心配色方案 (基于 variables.css) --- */

/* 1. Primary - 运行中 / 进行中 */
.status-primary {
  background-color: #ecfdf5;
  color: var(--primary-color);
  border: 1px solid rgba(66, 185, 131, 0.2);
}

/* 2. Success - 已完成 / QC通过 */
.status-success {
  background-color: #f0fdf4;
  color: #16a34a;
  border: 1px solid rgba(22, 163, 74, 0.2);
}

/* 3. Warning - 异常数据 / 待确认 */
.status-warning {
  background-color: #fffbeb;
  color: var(--warning-color);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

/* 4. Error - 格式错误 / 任务失败 */
.status-error {
  background-color: #fef2f2;
  color: var(--error-color);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

/* 5. Info - 格式转换中 / 系统提示 */
.status-info {
  background-color: #eff6ff;
  color: var(--info-color);
  border: 1px solid rgba(59, 130, 246, 0.2);
}

/* 6. Idle - 待开始 / 锁定中 (对应由灰变黑的灰) */
.status-idle {
  background-color: #f8fafc;
  color: var(--status-locked);
  border: 1px solid var(--border-color);
}
</style>