<template>
  <div class="login-container">
    <div class="login-brand">
      <div class="brand-content">
        <h1 class="logo-text">🧬 GWAS Platform</h1>
        <p class="tagline">专业、高效、可视化的全基因组关联分析解决方案</p>

        <div class="feature-list">
          <div class="feature-item">
            <span class="icon">⚡</span>
            <div class="text">
              <h4>大规模并行计算</h4>
              <p>集成高效算法，支持千万级 SNP 位点分析</p>
            </div>
          </div>
          <div class="feature-item">
            <span class="icon">📊</span>
            <div class="text">
              <h4>交互式可视化</h4>
              <p>动态生成 Manhattan、Q-Q 及 Volcano Plots</p>
            </div>
          </div>
          <div class="feature-item">
            <span class="icon">🛡️</span>
            <div class="text">
              <h4>数据隐私保护</h4>
              <p>符合生物信息学安全标准的加密存储</p>
            </div>
          </div>
        </div>
      </div>
      <div class="dna-decoration"></div>
    </div>

    <div class="login-form-section">
      <div class="form-card">
        <div class="form-header">
          <h2>欢迎回来</h2>
          <p class="welcome-msg">请登录您的科研账号以继续分析任务</p>
        </div>

        <form @submit.prevent="handleLogin">
          <div class="form-item" :class="{ 'has-error': errorMsg }">
            <label>用户名 / 邮箱</label>
            <div class="input-wrapper">
              <input
                  v-model="loginForm.username"
                  type="text"
                  placeholder="请输入账号"
                  required
                  :disabled="loading"
              />
            </div>
          </div>

          <div class="form-item" :class="{ 'has-error': errorMsg }">
            <label>密码</label>
            <div class="input-wrapper">
              <input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="请输入密码"
                  required
                  :disabled="loading"
              />
            </div>
          </div>

          <div v-if="errorMsg" class="error-banner">
            <span>⚠️ {{ errorMsg }}</span>
          </div>

          <div class="form-options">
            <label class="remember-me">
              <input type="checkbox" v-model="rememberMe" /> 记住登录状态
            </label>
            <a href="javascript:void(0)" @click="handleForgotPwd" class="forgot-pwd">忘记密码？</a>
          </div>

          <button type="submit" class="login-btn" :disabled="loading">
            <span v-if="!loading">立即进入平台</span>
            <span v-else class="loading-dots">正在验证身份<i>.</i><i>.</i><i>.</i></span>
          </button>
        </form>

        <div class="form-footer">
          <span>还没有账号？</span>
          <router-link to="/register" class="reg-link">申请开通权限</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const errorMsg = ref('')
const rememberMe = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const handleLogin = async () => {
  if (loading.value) return

  loading.value = true
  errorMsg.value = ''

  try {
    await userStore.login(loginForm)
    // 获取重定向地址或默认跳转仪表盘
    const redirectPath = (route.query.redirect as string) || '/dashboard'
    router.push(redirectPath)
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || '登录失败，请检查账号密码或网络连接'
  } finally {
    loading.value = false
  }
}

const handleForgotPwd = () => {
  alert('为确保科研数据安全，密码重置请联系您所属机构的平台管理员或通过单位内网进行操作。')
}
</script>

<style scoped>
.login-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background-color: #ffffff;
}

/* --- 左侧品牌区 --- */
.login-brand {
  flex: 1.2;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  color: white;
  padding: 60px;
}

.brand-content {
  position: relative;
  z-index: 10;
  max-width: 520px;
}

.logo-text {
  font-size: 42px;
  font-weight: 800;
  margin-bottom: 12px;
  background: linear-gradient(to right, #42b983, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -1px;
}

.tagline {
  font-size: 18px;
  opacity: 0.8;
  line-height: 1.6;
  margin-bottom: 50px;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.feature-item .icon {
  background: rgba(255, 255, 255, 0.1);
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  font-size: 20px;
  flex-shrink: 0;
}

.feature-item h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  color: #42b983;
}

.feature-item p {
  margin: 0;
  font-size: 14px;
  opacity: 0.6;
}

/* --- 右侧表单区 --- */
.login-form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8fafc;
}

.form-card {
  width: 100%;
  max-width: 420px;
  padding: 40px;
}

.form-header h2 {
  font-size: 28px;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.welcome-msg {
  color: #64748b;
  font-size: 14px;
  margin-bottom: 32px;
}

.form-item {
  margin-bottom: 24px;
}

.form-item label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 8px;
}

.input-wrapper input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 15px;
  background: white;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.input-wrapper input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.has-error input {
  border-color: #ef4444;
}

.error-banner {
  background-color: #fef2f2;
  border-left: 4px solid #ef4444;
  color: #b91c1c;
  padding: 12px;
  border-radius: 4px;
  font-size: 13px;
  margin-bottom: 24px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  margin-bottom: 32px;
}

.remember-me {
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}

.forgot-pwd {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}

.login-btn {
  width: 100%;
  padding: 14px;
  background-color: #1e293b;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.login-btn:hover {
  background-color: #0f172a;
  transform: translateY(-1px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.login-btn:active {
  transform: translateY(0);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.form-footer {
  margin-top: 40px;
  text-align: center;
  font-size: 14px;
  color: #64748b;
}

.reg-link {
  color: #3b82f6;
  font-weight: 600;
  text-decoration: none;
  margin-left: 6px;
  padding-bottom: 2px;
  border-bottom: 2px solid transparent;
  transition: border-color 0.2s;
}

.reg-link:hover {
  border-color: #3b82f6;
}

/* --- 背景装饰与动画 --- */
.dna-decoration {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background-image: radial-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px);
  background-size: 32px 32px;
  opacity: 0.6;
  pointer-events: none; /* 关键：防止遮挡表单点击 */
  z-index: 1;
}

.loading-dots i {
  font-style: normal;
  animation: blink 1.4s infinite both;
}
.loading-dots i:nth-child(2) { animation-delay: 0.2s; }
.loading-dots i:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
  0% { opacity: 0.2; }
  20% { opacity: 1; }
  100% { opacity: 0.2; }
}

/* 响应式调整 */
@media (max-width: 900px) {
  .login-brand { display: none; }
}
</style>