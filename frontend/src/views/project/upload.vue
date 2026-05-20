<template>
  <div class="upload-page">
    <StepFlow currentStep="IDLE" />

    <div class="upload-container">
      <aside class="project-info-card">
        <div class="card-header">
          <h3>🆕 初始化分析项目</h3>
        </div>

        <div class="form-body">
          <div class="form-item">
            <label>项目名称 (可选)</label>
            <input
                v-model="projectName"
                type="text"
                placeholder="未命名将使用时间戳..."
                class="styled-input"
            />
          </div>

          <div class="form-item">
            <label>物种参考</label>
            <select v-model="reference" class="styled-select">
              <option value="hg38">Human (hg38)</option>
              <option value="mm10">Mouse (mm10)</option>
            </select>
          </div>

          <div class="project-preview">
            <label>项目预览名称</label>
            <div class="name-box">{{ displayProjectName }}</div>
          </div>
        </div>
      </aside>

      <main class="upload-main">
        <div class="upload-grid">
          <div class="upload-box" :class="{ active: files.vcf }">
            <h4>基因型数据 *</h4>
            <div class="drop-zone" @click="triggerFile('vcf')">
              <span v-if="!files.vcf">点击上传 VCF / BED</span>
              <span v-else>{{ files.vcf.name }}</span>
            </div>
          </div>

          <div class="upload-box" :class="{ active: files.pheno }">
            <h4>表型数据 *</h4>
            <div class="drop-zone" @click="triggerFile('pheno')">
              <span v-if="!files.pheno">点击上传 .txt/.csv</span>
              <span v-else>{{ files.pheno.name }}</span>
            </div>
          </div>

          <div class="upload-box optional" :class="{ active: files.cov }">
            <h4>协变量（可选）</h4>
            <div class="drop-zone" @click="triggerFile('cov')">
              <span v-if="!files.cov">点击上传</span>
              <span v-else>{{ files.cov.name }}</span>
            </div>
          </div>
        </div>

        <input type="file" ref="vcfInput" hidden @change="e => handleFile(e,'vcf')" />
        <input type="file" ref="phenoInput" hidden @change="e => handleFile(e,'pheno')" />
        <input type="file" ref="covInput" hidden @change="e => handleFile(e,'cov')" />

        <div class="action-footer">
          <button
              :disabled="!canSubmit || uploading"
              @click="handleUpload"
              class="start-btn"
          >
            {{ uploading ? '上传中...' : '🚀 开始上传' }}
          </button>
        </div>
      </main>
    </div>

    <LoadingOverlay
        :visible="uploading"
        title="上传中"
        :description="`进度：${progress}%`"
        :progress="progress"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '@/store/project'
import { uploadFileAPI } from '@/api/analysis'
import { createProjectAPI, updateProjectAPI } from '@/api/project'
import StepFlow from '@/components/StepFlow.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'

const router = useRouter()
const projectStore = useProjectStore()

const projectName = ref('')
const reference = ref('hg38')
const uploading = ref(false)
const progress = ref(0)

const files = ref({
  vcf: null as File | null,
  pheno: null as File | null,
  cov: null as File | null
})

const vcfInput = ref<HTMLInputElement>()
const phenoInput = ref<HTMLInputElement>()
const covInput = ref<HTMLInputElement>()

const displayProjectName = computed(() => {
  return projectName.value || 'GWAS_' + Date.now()
})

const canSubmit = computed(() => {
  return files.value.vcf && files.value.pheno
})

const triggerFile = (type: string) => {
  if (type === 'vcf') vcfInput.value?.click()
  if (type === 'pheno') phenoInput.value?.click()
  if (type === 'cov') covInput.value?.click()
}

const handleFile = (e: any, type: string) => {
  const file = e.target.files[0]
  if (file) files.value[type as keyof typeof files.value] = file
}

const handleUpload = async () => {
  if (!canSubmit.value) return

  uploading.value = true
  progress.value = 10

  try {
    const projectId = projectStore.currentProjectId || 'PRJ_' + Math.random().toString(36).slice(2, 10)

    projectStore.currentProjectId = projectId
    projectStore.projectName = displayProjectName.value

    const formData = new FormData()
    formData.append('project_id', projectId)

    if (files.value.vcf) formData.append('file', files.value.vcf)
    if (files.value.pheno) formData.append('phenotype', files.value.pheno)
    if (files.value.cov) formData.append('covariate', files.value.cov)

    const res = await uploadFileAPI(formData)

    if (res.code === 200 || res.status === 200) {
      progress.value = 100
      projectStore.step = 'UPLOADED'

      // 同步项目记录到后端数据库
      try {
        await createProjectAPI({ id: projectId, name: displayProjectName.value })
        await updateProjectAPI(projectId, { current_step: 'UPLOADED' })
        console.log('[Upload] 项目已写入DB:', projectId)
      } catch (e: any) {
        console.error('[Upload] DB写入失败:', e?.message || e)
      }

      setTimeout(() => {
        router.push('/project/clean')
      }, 500)
    }

  } catch (err: any) {
    console.error('上传过程出错:', err)
    const errorMsg = err.response?.data?.detail || '上传失败，服务器无响应'
    alert(errorMsg)
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.upload-container {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 30px;
  margin-top: 20px;
}
.upload-box {
  border: 2px dashed #dcdfe6;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  transition: all 0.3s;
  background: #fff;
}
.upload-box.active {
  border-color: #42b983;
  background: #f0fdf4;
}
.drop-zone {
  height: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
}
.start-btn {
  margin-top: 30px;
  width: 100%;
  padding: 15px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
}
.start-btn:disabled {
  background: #a7e1c4;
  cursor: not-allowed;
}
</style>