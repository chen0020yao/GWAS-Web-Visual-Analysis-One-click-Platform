<template>
  <div class="snp-table-container">

    <!-- Header -->
    <div class="table-header">
      <div class="left">
        <h3 class="table-title">{{ title }}</h3>
        <span class="count-tag">共 {{ data.length }} 条记录</span>
      </div>

      <div class="right">
        <div v-if="mode === 'result'" class="filter-group">
          <label>P-value < </label>
          <input
              type="number"
              v-model="pThreshold"
              class="threshold-input"
              @input="$emit('filter', pThreshold)"
          />
        </div>

        <button class="export-btn" @click="exportCSV">📥 导出 CSV</button>
      </div>
    </div>

    <!-- Table -->
    <div class="table-wrapper">
      <table class="custom-table">
        <thead>
        <tr>
          <th>SNP ID</th>
          <th>Chr</th>
          <th>Pos</th>

          <th v-if="mode === 'result'">P-value</th>
          <th v-if="mode === 'result'">-log10(P)</th>

          <th v-if="mode === 'qc'">异常原因</th>
          <th v-if="mode === 'qc'">MAF</th>

          <th>操作</th>
        </tr>
        </thead>

        <tbody>
        <tr
            v-for="item in pagedData"
            :key="item.rsid"
            :class="{ highlight: item.p < 5e-8 }"
        >
          <td class="rsid">{{ item.rsid }}</td>
          <td>Chr{{ item.chr }}</td>
          <td>{{ formatNumber(item.pos) }}</td>

          <td v-if="mode === 'result'" class="p-val">
            {{ item.p.toExponential(3) }}
          </td>

          <td v-if="mode === 'result'">
            {{ (-Math.log10(item.p)).toFixed(2) }}
          </td>

          <td v-if="mode === 'qc'">
            {{ item.reason || 'FAIL' }}
          </td>

          <td v-if="mode === 'qc'">
            {{ item.maf?.toFixed(4) }}
          </td>

          <!-- ⭐ 核心：SNP联动按钮 -->
          <td>
            <button
                class="action-link"
                @click="handleView(item.rsid)"
            >
              查看注释
            </button>
          </td>
        </tr>

        <tr v-if="data.length === 0">
          <td colspan="6" class="empty-state">暂无数据</td>
        </tr>
        </tbody>
      </table>
    </div>

    <!-- pagination -->
    <div class="pagination" v-if="data.length > pageSize">
      <button :disabled="currentPage === 1" @click="currentPage--">上一页</button>
      <span>{{ currentPage }} / {{ totalPages }}</span>
      <button :disabled="currentPage === totalPages" @click="currentPage++">下一页</button>
    </div>

    <!-- ⭐ SNP详情弹窗 -->
    <div v-if="snpInfo" class="snp-panel">
      <h4>🧬 SNP 注释详情</h4>

      <p><b>rsID:</b> {{ snpInfo.rsid }}</p>
      <p><b>Gene:</b> {{ snpInfo.gene }}</p>
      <p><b>Chr:</b> {{ snpInfo.chr }}</p>
      <p><b>Pos:</b> {{ snpInfo.pos }}</p>

      <a
          :href="`https://www.ncbi.nlm.nih.gov/snp/${snpInfo.rsid}`"
          target="_blank"
      >
        🔗 NCBI 查看
      </a>

      <button class="close-btn" @click="snpInfo = null">关闭</button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { getSNPAnnotationAPI } from '@/api/analysis'

interface SNPItem {
  rsid: string
  chr: string | number
  pos: number
  p?: number
  maf?: number
  reason?: string
}

const props = defineProps({
  data: { type: Array as () => SNPItem[], default: () => [] },
  title: { type: String, default: 'SNP列表' },
  mode: { type: String as () => 'result' | 'qc', default: 'result' }
})

const emit = defineEmits(['view-details', 'filter'])

const currentPage = ref(1)
const pageSize = ref(15)
const pThreshold = ref(0.05)

const snpInfo = ref<any>(null)

const totalPages = computed(() =>
    Math.ceil(props.data.length / pageSize.value)
)

const pagedData = computed(() =>
    props.data.slice(
        (currentPage.value - 1) * pageSize.value,
        currentPage.value * pageSize.value
    )
)

// =========================
// ⭐ SNP注释联动核心
// =========================
const handleView = async (rsid: string) => {
  emit('view-details', rsid)

  try {
    const res = await getSNPAnnotationAPI(rsid)

    snpInfo.value = {
      rsid,
      gene: res.data.gene || 'UNKNOWN',
      chr: res.data.chr,
      pos: res.data.pos
    }

  } catch (e) {
    snpInfo.value = {
      rsid,
      gene: 'NOT FOUND',
      chr: '-',
      pos: '-'
    }
  }
}

// =========================
const formatNumber = (num: number) =>
    num?.toLocaleString()

const exportCSV = () => {
  const content = props.data.map(i =>
      `${i.rsid},${i.chr},${i.pos}`
  ).join('\n')

  const blob = new Blob([content], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)

  const a = document.createElement('a')
  a.href = url
  a.download = `snp_${props.mode}.csv`
  a.click()
}
</script>

<style scoped>
.snp-table-container {
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  padding: 12px;
  background: #f8fafc;
}

.custom-table {
  width: 100%;
  border-collapse: collapse;
}

.custom-table td, th {
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.highlight {
  background: #f0fdf4;
}

.action-link {
  color: #3b82f6;
  border: none;
  background: none;
  cursor: pointer;
}

/* ⭐ SNP详情面板 */
.snp-panel {
  position: fixed;
  right: 20px;
  top: 120px;
  width: 300px;
  background: white;
  border: 1px solid #ddd;
  padding: 16px;
  border-radius: 12px;
}

.close-btn {
  margin-top: 10px;
}
</style>