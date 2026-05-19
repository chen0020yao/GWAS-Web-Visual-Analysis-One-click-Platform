import { defineStore } from 'pinia'
import {
    getTaskStatusAPI,
    getTaskLogsAPI,
    confirmNextStepAPI
} from '@/api/pipeline'
import { useProjectStore } from './project'

export const usePipelineStore = defineStore('pipeline', {
    state: () => ({
        // 1. 当前激活的任务信息
        activeTaskId: null as string | null,
        taskStatus: 'IDLE' as 'IDLE' | 'RUNNING' | 'SUCCESS' | 'FAILED' | 'WAITING',
        progress: 0,

        // 2. 实时日志与异常信息
        currentLog: '',         // 最新的一行日志
        errorDetail: '',       // 对应需求：没成功显示原因

        // 3. 轮询控制
        timer: null as number | null,
    }),

    getters: {
        // 是否正在显示加载遮罩
        showOverlay: (state) => state.taskStatus === 'RUNNING' || state.taskStatus === 'WAITING',

        // 异常描述文字
        statusMessage: (state) => {
            if (state.taskStatus === 'FAILED') return `分析任务失败：${state.errorDetail}`
            if (state.taskStatus === 'WAITING') return '检测到数据异常，请在下方确认处理方案'
            return state.currentLog || '正在处理中...'
        }
    },

    actions: {
        // 启动任务追踪
        trackTask(taskId: string) {
            this.activeTaskId = taskId
            this.taskStatus = 'RUNNING'
            this.errorDetail = ''
            this.startPolling()
        },

        // 核心轮询逻辑
        async startPolling() {
            if (this.timer) return

            this.timer = window.setInterval(async () => {
                if (!this.activeTaskId) return this.stopPolling()

                try {
                    const { data } = await getTaskStatusAPI(this.activeTaskId)

                    this.progress = data.progress
                    this.currentLog = data.message

                    // 状态机流转
                    switch (data.status) {
                        case 'SUCCESS':
                            this.taskStatus = 'SUCCESS'
                            this.stopPolling()
                            // 自动触发项目进度更新（由灰变黑）
                            useProjectStore().fetchProjectStatus()
                            break
                        case 'FAILED':
                            this.taskStatus = 'FAILED'
                            this.errorDetail = data.error_reason // 指出异常原因
                            this.stopPolling()
                            break
                        case 'AWAITING_CONFIRMATION':
                            this.taskStatus = 'WAITING' // 对应“异常原因指出让用户确认”
                            this.stopPolling()
                            break
                    }
                } catch (err) {
                    this.stopPolling()
                    this.taskStatus = 'FAILED'
                    this.errorDetail = '无法连接到远程计算引擎'
                }
            }, 2000)
        },

        // 停止轮询
        stopPolling() {
            if (this.timer) {
                clearInterval(this.timer)
                this.timer = null
            }
        },

        // 对应需求：用户确认执行清洗或下一步
        async confirmStep(projectId: string, step: string) {
            try {
                await confirmNextStepAPI(projectId, step)
                // 确认后，如果有新任务产生，重新开始追踪
                this.taskStatus = 'RUNNING'
                this.startPolling()
            } catch (err) {
                this.errorDetail = '确认操作失败'
            }
        },

        // 重置状态
        resetPipeline() {
            this.stopPolling()
            this.$reset()
        }
    }
})