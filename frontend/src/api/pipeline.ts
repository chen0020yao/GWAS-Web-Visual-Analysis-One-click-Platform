import request from '@/utils/request'

/**
 * GWAS 工作流任务管理接口
 */

// 1. 获取任务实时状态
// 用于在前端显示进度条或 Loading 状态，判断任务是否完成、失败或进行中
export const getTaskStatusAPI = (taskId: string) =>
    request({
        url: `/api/pipeline/status/${taskId}`,
        method: 'get'
    })

// 2. 获取任务运行日志
// 当任务失败时，从后端获取具体的错误信息（如：Plink 报错日志、内存溢出原因等）
// 对应你要求的“没成功显示原因”
export const getTaskLogsAPI = (taskId: string) =>
    request({
        url: `/api/pipeline/logs/${taskId}`,
        method: 'get'
    })

// 3. 终止正在运行的任务
// 用户在等待 QC 或分析过程中点击取消
export const stopTaskAPI = (taskId: string) =>
    request({
        url: `/api/pipeline/stop/${taskId}`,
        method: 'post'
    })

// 4. 获取项目完整进度轨迹
// 返回当前项目已完成的步骤（UPLOADED -> QC -> VIZ），用于侧边栏的由灰变黑逻辑同步
export const getProjectProgressAPI = (projectId: string) =>
    request({
        url: `/api/pipeline/progress/${projectId}`,
        method: 'get'
    })

/**
 * 特殊工作流触发器
 */

// 5. 触发 VCF 转 Plink 的异步转换任务
export const triggerFormatConversionAPI = (projectId: string) =>
    request({
        url: '/api/pipeline/convert-vcf',
        method: 'post',
        data: { projectId }
    })

// 6. 获取数据清洗（QC）的详细异常统计报告
// 对应你要求的“清洗后不合要求的数据显示给用户看并指出异常原因”
export const getQCReportAPI = (projectId: string) =>
    request({
        url: `/api/pipeline/qc-report/${projectId}`,
        method: 'get'
    })

// 7. 历史记录批量管理
// 清除选中的历史任务记录
export const batchDeleteHistoryAPI = (projectIds: string[]) =>
    request({
        url: '/api/pipeline/history/batch-delete',
        method: 'post',
        data: { projectIds }
    })

// ✅【修复最后一个报错】步骤确认接口
export const confirmNextStepAPI = (data: any) => request.post('/api/pipeline/confirm-next', data)

/**
 * 响应结构示例说明：
 * getTaskStatusAPI 建议返回：
 * {
 *   status: 'running' | 'success' | 'failed',
 *   progress: 85, // 百分比
 *   current_step: 'Calculating kinship matrix...',
 *   error_msg: 'Format error in line 452' // 如果失败
 * }
 */