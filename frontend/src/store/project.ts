import { defineStore } from 'pinia'
import { getProjectDetailAPI, updateProjectAPI } from '@/api/project'

// 定义项目进度的枚举类型
export type ProjectStep = 'IDLE' | 'UPLOADED' | 'QC_DONE' | 'ANALYSIS_DONE'

export const useProjectStore = defineStore('project', {
    state: () => ({
        // 1. 项目基本信息
        currentProjectId: '' as string,
        projectName: '' as string,
        createdAt: '' as string,

        // 2. 核心状态：决定 UI “由灰变黑”的关键
        // IDLE: 初始态 | UPLOADED: 已上传 | QC_DONE: 质控完成 | ANALYSIS_DONE: 分析完成
        step: 'IDLE' as ProjectStep,

        // 3. 统计摘要
        summary: {
            sampleCount: 0,
            snpCount: 0,
            phenotype: ''
        }
    }),

    getters: {
        // 逻辑锁：是否可以进入“数据清洗/质控”
        canAccessQC: (state) => {
            const weights: Record<ProjectStep, number> = {
                'IDLE': 0,
                'UPLOADED': 1,
                'QC_DONE': 2,
                'ANALYSIS_DONE': 3
            }
            return weights[state.step] >= 1
        },

        // 逻辑锁：是否可以进入“可视化/结果分析”
        // 只要 QC 过了，通常就能看中间结果，如果是最终结果则需要 ANALYSIS_DONE
        canAccessViz: (state) => {
            return state.step === 'ANALYSIS_DONE'
        },

        // 格式化显示名称
        displayName: (state): string => {
            if (state.projectName) return state.projectName
            return state.createdAt
                ? `项目_${new Date(state.createdAt).toLocaleDateString()}`
                : '新分析项目'
        }
    },

    actions: {
        // 设置当前项目并初始化
        async setCurrentProject(projectId: string) {
            this.currentProjectId = projectId
            await this.fetchProjectStatus()
        },

        // 从后端拉取进度
        async fetchProjectStatus() {
            if (!this.currentProjectId) return
            try {
                const res = await getProjectDetailAPI(this.currentProjectId)
                const data = res.data

                this.projectName = data.name
                this.step = data.current_step as ProjectStep
                this.createdAt = data.created_at
                this.summary = {
                    sampleCount: data.sample_count,
                    snpCount: data.snp_count,
                    phenotype: data.phenotype_name
                }
            } catch (error) {
                console.error('同步项目状态失败:', error)
            }
        },

        // 更新名称
        async updateName(newName: string) {
            if (!this.currentProjectId) return
            try {
                await updateProjectAPI(this.currentProjectId, { name: newName })
                this.projectName = newName
            } catch (error) {
                console.error('重命名失败:', error)
                throw error
            }
        },

        // 彻底重置
        resetProject() {
            this.$reset() // 使用 Pinia 内置的重置方法
            localStorage.removeItem('gwas_project_storage')
        }
    },

    // 持久化配置
    persist: {
        // 存放在 LocalStorage 中的 Key 值
        key: 'gwas_project_storage',
        // 指定保存哪些字段，防止把所有临时状态都存进去
        // 建议保存 ID、名称和进度，summary 可以重新从接口获取
        paths: ['currentProjectId', 'projectName', 'step', 'createdAt'],
    }
})