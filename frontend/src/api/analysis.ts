import request from '@/utils/request'

const PREFIX = '/api/analysis'

// ====================
// 上传
// ====================
export const uploadFileAPI = (formData: FormData) =>
    request({
        url: `${PREFIX}/upload`,
        method: 'post',
        data: formData,
        headers: { 'Content-Type': 'multipart/form-data' }
    })

// ====================
// QC 质控
// ====================
export const getQCPreviewAPI = (data: any) =>
    request({
        url: `${PREFIX}/qc/preview`,
        method: 'post',
        data
    })

export const confirmAndRunQCAPI = (projectId: string, filters?: Record<string, any>) =>
    request({
        url: `${PREFIX}/qc/run`,
        method: 'post',
        data: { projectId, filters: filters || {} }
    })

export const getQCReportAPI = (projectId: string) =>
    request({ url: `${PREFIX}/qc/report/${projectId}`, method: 'get' })

// ====================
// GWAS 分析
// ====================
export const runGWASAnalysisAPI = (data: any) =>
    request({ url: `${PREFIX}/run`, method: 'post', data })

export const getAnalysisProgressAPI = (projectId?: string) =>
    request({ url: `/api/pipeline/progress/${projectId || 'latest'}`, method: 'get' })

// ====================
// 可视化数据
// ====================
export const getPlotDataAPI = (projectId: string, type: string) =>
    request({ url: `${PREFIX}/plot-data/${projectId}`, method: 'get', params: { type } })

export const getManhattanAPI = (projectId: string) => getPlotDataAPI(projectId, 'manhattan')
export const getQQAPI = (projectId: string) => getPlotDataAPI(projectId, 'qq')
export const getPCAAPI = (projectId: string) => getPlotDataAPI(projectId, 'pca')

// ====================
// 显著SNP
// ====================
export const getSignificantSNPAPI = (projectId: string) =>
    request({ url: `${PREFIX}/snp/significant/${projectId}`, method: 'get' })

// ====================
// SNP 注释
// ====================
export const getAnnotationAPI = (rsid: string) =>
    request({ url: `${PREFIX}/annotation/${rsid}`, method: 'get' })

export const getSNPAnnotationAPI = (rsid: string) =>
    request({ url: `${PREFIX}/snp/details`, method: 'get', params: { rsid } })

// ====================
// 富集分析
// ====================
export const getGOAPI = (projectId: string) =>
    request({ url: `${PREFIX}/enrichment/go/${projectId}`, method: 'get' })

export const getKEGGAPI = (projectId: string) =>
    request({ url: `${PREFIX}/enrichment/kegg/${projectId}`, method: 'get' })
