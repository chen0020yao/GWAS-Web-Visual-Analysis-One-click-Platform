<template>
  <div class="chart-container">
    <!-- 图表工具栏：方便科研导出 -->
    <div class="chart-toolbar">
      <button class="tool-btn" @click="downloadImage" title="导出高清图片">💾 导出</button>
      <button class="tool-btn" @click="resizeChart" title="刷新视图">🔄 重置</button>
    </div>

    <!-- 图表主容器 -->
    <div
        ref="chartRef"
        :style="{ width: width, height: height }"
        class="echarts-dom"
    ></div>

    <!-- 加载遮罩：用于长耗时绘图（如曼哈顿图渲染） -->
    <div v-if="loading" class="chart-loading">
      <div class="spinner"></div>
      <span>正在渲染大规模基因组数据...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  options: {
    type: Object,
    required: true
  },
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: String,
    default: '500px'
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

// 1. 初始化图表
const initChart = () => {
  if (!chartRef.value) return

  // 销毁旧实例，防止内存泄漏
  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartRef.value, null, {
    renderer: 'canvas', // GWAS 散点图建议使用 canvas 提高性能
    useDirtyRect: true  // 开启脏矩形渲染优化
  })

  chartInstance.setOption(props.options)
}

// 2. 高清图片导出逻辑
const downloadImage = () => {
  if (!chartInstance) return
  const url = chartInstance.getDataURL({
    type: 'png',
    pixelRatio: 2, // 2倍清晰度，满足科研论文需求
    backgroundColor: '#fff'
  })
  const link = document.createElement('a')
  link.href = url
  link.download = `GWAS_Plot_${Date.now()}.png`
  link.click()
}

// 3. 响应式尺寸调整
const resizeChart = () => {
  chartInstance?.resize()
}

// 4. 监听配置变化
watch(
    () => props.options,
    (newOptions) => {
      if (chartInstance) {
        // notMerge: true 确保切换不同类型的图（如从曼哈顿切到QQ图）时配置不冲突
        chartInstance.setOption(newOptions, { notMerge: true })
      }
    },
    { deep: true }
)

// 5. 窗口缩放适配
const handleResize = () => {
  resizeChart()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose() // 必须销毁，释放 GPU 资源
})

// 暴露方法给父组件
defineExpose({
  resizeChart,
  chartInstance
})
</script>

<style scoped>
.chart-container {
  position: relative;
  background: var(--card-bg);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--border-color);
  padding: 10px;
  width: 100%;
}

.chart-toolbar {
  position: absolute;
  top: 10px;
  right: 15px;
  z-index: 10;
  display: flex;
  gap: 8px;
}

.tool-btn {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.tool-btn:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.echarts-dom {
  min-height: 300px;
}

.chart-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 11;
  font-size: 14px;
  color: var(--primary-color);
}

.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid var(--border-color);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>