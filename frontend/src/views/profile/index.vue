<template>
  <div class="profile-page">
    <div class="profile-layout">
      <!-- 左侧：用户基本信息卡片 -->
      <aside class="profile-aside">
        <div class="user-card">
          <div class="avatar-wrapper">
            <div v-if="userStore.userInfo?.avatar" class="avatar-img">
              <img :src="userStore.userInfo.avatar" alt="Avatar" />
            </div>
            <div v-else class="avatar-placeholder">
              {{ userStore.initials }}
            </div>
            <button class="edit-avatar-btn">更换头像</button>
          </div>
          <h2 class="username">{{ userStore.userInfo?.nickname || '研究员' }}</h2>
          <p class="user-role">
            <StatusTag type="primary" :label="userStore.userInfo?.role.toUpperCase()" />
          </p>
          <div class="user-meta">
            <div class="meta-item">
              <span class="label">注册时间</span>
              <span class="value">2026-01-15</span>
            </div>
            <div class="meta-item">
              <span class="label">所属机构</span>
              <span class="value">Precision Med Lab</span>
            </div>
          </div>
        </div>

        <!-- 资源配额展示 -->
        <div class="quota-card">
          <h3>💾 存储配额</h3>
          <div class="quota-usage">
            <div class="usage-info">
              <span>已使用 45.2 GB</span>
              <span>总量 100 GB</span>
            </div>
            <div class="progress-bar">
              <div class="fill" style="width: 45.2%"></div>
            </div>
          </div>
          <p class="quota-hint">GWAS 原始文件较多，建议及时清理历史缓存。</p>
        </div>
      </aside>

      <!-- 右侧：设置页签 -->
      <main class="profile-main">
        <div class="tabs-container">
          <div class="tabs-header">
            <button
                v-for="tab in ['account', 'security', 'api']"
                :key="tab"
                :class="['tab-btn', { active: activeTab === tab }]"
                @click="activeTab = tab"
            >
              {{ tabLabelMap[tab] }}
            </button>
          </div>

          <div class="tabs-content">
            <!-- 账户设置 -->
            <div v-if="activeTab === 'account'" class="settings-form">
              <div class="form-section">
                <h4>基本信息</h4>
                <div class="form-row">
                  <div class="field">
                    <label>显示昵称</label>
                    <input v-model="profileForm.nickname" type="text" placeholder="设置您的公开名称" />
                  </div>
                  <div class="field">
                    <label>电子邮箱</label>
                    <input v-model="profileForm.email" type="email" />
                  </div>
                </div>
              </div>
              <button class="save-btn" @click="handleUpdateProfile">保存更改</button>
            </div>

            <!-- 安全设置 -->
            <div v-if="activeTab === 'security'" class="settings-form">
              <div class="form-section">
                <h4>修改密码</h4>
                <div class="field full">
                  <label>当前密码</label>
                  <input type="password" />
                </div>
                <div class="field full">
                  <label>新密码</label>
                  <input type="password" />
                </div>
              </div>
              <button class="save-btn warning">重置密码</button>
            </div>

            <!-- API 访问权限 (针对科研开发者) -->
            <div v-if="activeTab === 'api'" class="settings-form">
              <div class="api-notice">
                <p>通过 API Key，您可以使用 Python 脚本直接向计算引擎提交任务。</p>
              </div>
              <div class="field full">
                <label>Access Token</label>
                <div class="token-copy">
                  <input type="text" readonly value="sk_gwas_2026_xxxxxxxxxxxx" />
                  <button class="copy-btn">复制</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useUserStore } from '@/store/user'
import StatusTag from '@/components/StatusTag.vue'

const userStore = useUserStore()
const activeTab = ref('account')

const tabLabelMap: any = {
  account: '账户资料',
  security: '安全设置',
  api: 'API 密钥'
}

const profileForm = reactive({
  nickname: userStore.userInfo?.nickname || '',
  email: userStore.userInfo?.email || ''
})

const handleUpdateProfile = () => {
  // 模拟提交
  console.log('Update Profile:', profileForm)
  alert('资料更新成功！')
}
</script>

<style scoped>
.profile-page {
  max-width: 1100px;
  margin: 0 auto;
}

.profile-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
}

/* 左侧卡片 */
.user-card, .quota-card {
  background: var(--card-bg);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
  padding: 30px 20px;
  margin-bottom: 24px;
}

.avatar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.avatar-placeholder {
  width: 100px;
  height: 100px;
  background: var(--primary-color);
  color: white;
  font-size: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  margin-bottom: 12px;
}

.username {
  text-align: center;
  margin: 0 0 8px 0;
}

.user-role {
  text-align: center;
  margin-bottom: 24px;
}

.user-meta {
  border-top: 1px solid var(--border-color);
  padding-top: 20px;
}

.meta-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  margin-bottom: 10px;
}

.meta-item .label { color: var(--text-muted); }

/* 配额进度条 */
.usage-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  margin-bottom: 8px;
}

.progress-bar {
  height: 8px;
  background: #eee;
  border-radius: 4px;
  overflow: hidden;
}

.fill {
  height: 100%;
  background: var(--primary-color);
}

.quota-hint {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 12px;
}

/* 右侧标签页 */
.tabs-container {
  background: var(--card-bg);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
  min-height: 500px;
}

.tabs-header {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  padding: 0 20px;
}

.tab-btn {
  padding: 16px 24px;
  border: none;
  background: none;
  font-size: 14px;
  cursor: pointer;
  color: var(--text-muted);
  position: relative;
}

.tab-btn.active {
  color: var(--primary-color);
  font-weight: 600;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--primary-color);
}

.tabs-content {
  padding: 30px;
}

.form-section h4 {
  margin-top: 0;
  margin-bottom: 20px;
  color: var(--text-main);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.field {
  margin-bottom: 20px;
}

.field label {
  display: block;
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.field input {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
}

.save-btn {
  padding: 10px 24px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.save-btn.warning { background: var(--error-color); }

.token-copy {
  display: flex;
  gap: 10px;
}

.token-copy input { flex: 1; background: #f8f9fa; }

.copy-btn {
  padding: 0 16px;
  background: #eee;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
}
</style>