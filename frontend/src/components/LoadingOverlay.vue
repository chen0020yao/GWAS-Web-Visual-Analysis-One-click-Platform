<template>
  <Transition name="fade">
    <div v-if="visible" class="loading-overlay">
      <div class="loading-card">
        <!-- 动态动画图标 -->
        <div class="dna-spinner">
          <div class="dot" v-for="n in 8" :key="n"></div>
        </div>

        <div class="loading-content">
          <h3 class="title">{{ title }}</h3>
          <p class="description">{{ description }}</p>

          <!-- 进度条展示 -->
          <div v-if="showProgress" class="progress-container">
            <div class="progress-bar">
              <div
                  class="progress-fill"
                  :style="{ width: `${progress}%` }"
              ></div>
            </div>
            <span class="progress-text">{{ progress }}%</span>
          </div>

          <!-- 实时日志/状态展示 (对应“没成功显示原因”) -->
          <div v-if="statusLog" class="status-log">
            <code>> {{ statusLog }}</code>
          </div>
        </div>

        <!-- 只有在允许的情况下显示取消按钮 -->
        <button v-if="allowCancel" class="cancel-btn" @click="$emit('cancel')">
          取消任务
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
/**
 * 属性说明：
 * @prop visible: 是否显示
 * @prop title: 主标题（如：正在运行 GWAS）
 * @prop description: 副标题（如：这可能需要几分钟，请勿关闭页面）
 * @prop progress: 进度百分比 (0-100)
 * @prop statusLog: 当前正在执行的具体步骤（来自后端 pipeline）
 */
defineProps({
  visible: { type: Boolean, default: false },
  title: { type: String, default: '正在处理数据' },
  description: { type: String, default: '系统正在全力计算中，请稍候...' },
  progress: { type: Number, default: 0 },
  showProgress: { type: Boolean, default: true },
  statusLog: { type: String, default: '' },
  allowCancel: { type: Boolean, default: false }
})

defineEmits(['cancel'])
</script>

<style scoped>
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(15, 23, 42, 0.8); /* 深色半透明背景 */
  backdrop-filter: blur(4px);      /* 毛玻璃效果，提升高级感 */
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
}

.loading-card {
  background: var(--card-bg);
  padding: 40px;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
  width: 400px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* DNA / 基因风格动画 */
.dna-spinner {
  position: relative;
  width: 60px;
  height: 60px;
  margin-bottom: 24px;
}

.dna-spinner .dot {
  position: absolute;
  width: 8px;
  height: 8px;
  background: var(--primary-color);
  border-radius: 50%;
  animation: dna-bounce 1.2s infinite ease-in-out;
}

/* 螺旋动画逻辑 */
.dna-spinner .dot:nth-child(1) { top: 0; left: 26px; animation-delay: 0s; }
.dna-spinner .dot:nth-child(2) { top: 10px; left: 45px; animation-delay: 0.1s; }
.dna-spinner .dot:nth-child(3) { top: 26px; left: 52px; animation-delay: 0.2s; }
.dna-spinner .dot:nth-child(4) { top: 45px; left: 45px; animation-delay: 0.3s; }
.dna-spinner .dot:nth-child(5) { top: 52px; left: 26px; animation-delay: 0.4s; }
.dna-spinner .dot:nth-child(6) { top: 45px; left: 10px; animation-delay: 0.5s; }
.dna-spinner .dot:nth-child(7) { top: 26px; left: 0; animation-delay: 0.6s; }
.dna-spinner .dot:nth-child(8) { top: 10px; left: 10px; animation-delay: 0.7s; }

@keyframes dna-bounce {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(0.3); opacity: 0.3; }
}

.title {
  margin: 0 0 8px;
  color: var(--text-main);
  font-size: 18px;
}

.description {
  color: var(--text-muted);
  font-size: 14px;
  margin-bottom: 24px;
}

/* 进度条 */
.progress-container {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: var(--border-color);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: var(--primary-color);
  font-weight: bold;
  width: 35px;
}

/* 实时日志 */
.status-log {
  margin-top: 20px;
  width: 100%;
  background: #1e293b;
  padding: 8px 12px;
  border-radius: 4px;
  text-align: left;
}

.status-log code {
  color: #4ade80;
  font-size: 12px;
  word-break: break-all;
}

.cancel-btn {
  margin-top: 24px;
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  padding: 6px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.cancel-btn:hover {
  color: var(--error-color);
  border-color: var(--error-color);
}

/* 过渡动画 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>