<template>
  <div class="register-container">
    <div class="brand-section">
      <div class="brand-content">
        <h1 class="logo-text">🧬 GWAS Platform</h1>
        <p class="tagline">加入科研社区，开启极速全基因组关联分析</p>

        <div class="simple-features">
          <div class="f-item">✓ 快速创建分析任务</div>
          <div class="f-item">✓ 实时交互可视化图表</div>
          <div class="f-item">✓ 云端存储分析历史</div>
        </div>
      </div>
      <div class="dna-decoration"></div>
    </div>

    <div class="form-section">
      <div class="form-card">
        <div class="back-nav" @click="$router.push('/login')">
          <span class="arrow">←</span> 返回登录
        </div>
        <h2>创建新账号</h2>
        <p class="desc">填写基础信息即可完成注册</p>

        <form @submit.prevent="handleRegister">
          <div class="form-item">
            <label>用户昵称</label>
            <input v-model="form.nickname" type="text" placeholder="起个好听的名字" required />
          </div>

          <div class="form-item">
            <label>电子邮箱</label>
            <input v-model="form.email" type="email" placeholder="example@mail.com" required />
          </div>

          <div class="form-item">
            <label>设置密码</label>
            <input v-model="form.password" type="password" placeholder="不少于6位字符" required />
          </div>

          <div class="form-item" :class="{ 'has-error': !passwordMatch && form.confirmPassword }">
            <label>确认密码</label>
            <input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" required />
            <span v-if="!passwordMatch && form.confirmPassword" class="error-msg">两次输入的密码不一致</span>
          </div>

          <button type="submit" class="reg-btn" :disabled="loading || !passwordMatch">
            <span v-if="!loading">立即注册</span>
            <span v-else>正在同步数据...</span>
          </button>
        </form>

        <div class="form-footer">
          注册即代表您同意本平台的《服务条款》
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { registerAPI } from '@/api/user'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  nickname: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// 校验两次密码是否一致
const passwordMatch = computed(() => {
  return form.password === form.confirmPassword
})

const handleRegister = async () => {
  if (!passwordMatch.value) {
    alert('两次输入的密码不一致')
    return
  }

  if (!form.email.includes('@')) {
    alert('请输入有效的邮箱地址')
    return
  }

  if (form.password.length < 6) {
    alert('密码长度不能少于6位')
    return
  }

  loading.value = true

  try {
    await registerAPI({
      nickname: form.nickname,
      email: form.email,
      password: form.password
    })

    alert('注册成功！请登录')
    router.push('/login')
  } catch (err: any) {
    // 响应拦截器已经把后端错误提取为 message 字符串
    const msg = err.message || '注册失败，请检查网络连接'
    alert(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: #ffffff;
  overflow: hidden;
}

/* 左侧品牌 */
.brand-section {
  flex: 1;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 60px;
  color: white;
}

.brand-content { position: relative; z-index: 10; max-width: 400px; }

.logo-text {
  font-size: 36px;
  font-weight: 800;
  background: linear-gradient(to right, #42b983, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 12px;
}

.tagline { opacity: 0.8; font-size: 16px; margin-bottom: 40px; line-height: 1.5; }

.simple-features {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.f-item {
  font-size: 14px;
  background: rgba(255, 255, 255, 0.05);
  padding: 10px 15px;
  border-radius: 8px;
  border-left: 3px solid #42b983;
}

/* 右侧表单 */
.form-section {
  flex: 1.2;
  background-color: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-card { width: 100%; max-width: 400px; padding: 40px; }

.back-nav {
  color: #64748b;
  font-size: 14px;
  cursor: pointer;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.back-nav:hover { color: #3b82f6; }

.form-card h2 { font-size: 28px; color: #1e293b; margin: 0 0 8px 0; }
.desc { color: #64748b; font-size: 14px; margin-bottom: 30px; }

.form-item { margin-bottom: 20px; position: relative; }
.form-item label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 8px;
}

.form-item input {
  width: 100%;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  transition: all 0.2s;
}

.form-item input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.has-error input { border-color: #ef4444; }
.error-msg {
  font-size: 12px;
  color: #ef4444;
  position: absolute;
  bottom: -18px;
  left: 0;
}

.reg-btn {
  width: 100%;
  padding: 14px;
  background: #1e293b;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 15px;
  transition: all 0.2s;
}

.reg-btn:hover:not(:disabled) { background: #0f172a; transform: translateY(-1px); }
.reg-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.form-footer {
  text-align: center;
  font-size: 12px;
  color: #94a3b8;
  margin-top: 24px;
}

.dna-decoration {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background-image: radial-gradient(rgba(255,255,255,0.05) 1px, transparent 1px);
  background-size: 30px 30px;
  pointer-events: none;
}
</style>