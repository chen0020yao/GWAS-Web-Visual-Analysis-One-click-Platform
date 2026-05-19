import { defineStore } from 'pinia'
import {
    runGWASAnalysisAPI,
    getAnalysisProgressAPI,
    getQCReportAPI
} from '@/api/analysis'

export const useAnalysisStore = defineStore('analysis', {
    state: () => ({
        // 1. QC 质控参数
        qcParams: {
            maf: 0.05,        // 次等位基因频率阈值
            geno: 0.1,       // 位点缺失率阈值
            mind: 0.1,       // 样本缺失率阈值
            hwe: 1e-6,       // 哈代-温伯格平衡阈值
        },

        // 2. 算法模型参数
        modelParams: {
            method: 'MLM',   // 常用模型：GLM, MLM (Mixed Linear Model)
            covariates: [],  // 协变量选择
            pcaNum: 3,       // 使用的主成分数量
        },

        // 3. 任务执行状态
        isRunning: false,
        progress: 0,
        statusText: '',    // 对应“实时日志显示”
        errorMsg: '',      // 对应“没成功显示原因”

        // 4. 分析结果摘要
        qcResultSummary: null as any, // 存储 QC 剔除后的统计数据
    }),

    actions: {
        // 设置 QC 参数
        setQCParams(params: Partial<typeof this.qcParams>) {
            this.qcParams = { ...this.qcParams, ...params }
        },

        // 触发 GWAS 分析任务
        async startAnalysis(projectId: string) {
            this.isRunning = true
            this.progress = 0
            this.errorMsg = ''

            try {
                const data = await runGWASAnalysisAPI({
                    projectId,
                    ...this.qcParams,
                    ...this.modelParams
                })

                // 如果后端支持 WebSocket，此处通常建立连接
                // 如果是 Polling，则启动定时器查询进度
                this.pollProgress(data.taskId)
            } catch (error: any) {
                this.isRunning = false
                this.errorMsg = error.message || '分析启动失败'
            }
        },

        // 轮询任务进度 (配合 pipeline API)
        async pollProgress(taskId: string) {
            const timer = setInterval(async () => {
                try {
                    const data = await getAnalysisProgressAPI(taskId)
                    this.progress = data.progress
                    this.statusText = data.log

                    if (data.status === 'SUCCESS') {
                        clearInterval(timer)
                        this.isRunning = false
                        // 可以在此处通知 projectStore 更新 step 为 'ANALYSIS_DONE'
                    } else if (data.status === 'FAILED') {
                        clearInterval(timer)
                        this.isRunning = false
                        this.errorMsg = data.error_reason // 指出具体报错原因
                    }
                } catch (e) {
                    clearInterval(timer)
                    this.isRunning = false
                }
            }, 2000)
        },

        // 获取 QC 后的异常数据报告
        async fetchQCReport(projectId: string) {
            try {
                const data = await getQCReportAPI(projectId)
                this.qcResultSummary = data
                return data
            } catch (error) {
                console.error('获取质控报告失败')
            }
        },

        // 重置分析状态
        resetAnalysis() {
            this.$reset()
        }
    },

    persist: {
        enabled: true,
        strategies: [{ storage: localStorage, paths: ['qcParams', 'modelParams'] }]
    }
})