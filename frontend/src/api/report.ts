import request from '@/utils/request'

/**
 * GWAS 质控 (QC) 与 结果报告接口
 */

// 1. 获取 QC 详细异常报告
// 对应需求：清洗后不合要求的数据显示给用户看并指出异常原因
// 返回内容包括：因 MAF 过低、缺失率过高、HWE 不平衡而被剔除的具体 SNP 数量、ID 及原因摘要
export const getQCDetailReportAPI = (projectId: string) =>
    request({
        url: `/api/report/qc-detail/${projectId}`,
        method: 'get'
    })

// 2. 获取显著性 SNP 列表 (用于可视化板块下的详细表格)
// 筛选出 P-Value 小于指定阈值（如 5e-8）的位点，供用户导出或在 SNPTable 中查看
export const getSignificantSNPsAPI = (params: {
    projectId: string,
    pThreshold?: number,
    limit?: number
}) =>
    request({
        url: '/api/report/significant-snps',
        method: 'get',
        params
    })

// 3. 导出项目完整报告
// 将整个分析流程、QC 参数、显著 SNP 及图像路径生成 PDF 或 Excel 下载链接
export const exportProjectReportAPI = (projectId: string, format: 'pdf' | 'xlsx') =>
    request({
        url: `/api/report/export/${projectId}`,
        method: 'get',
        params: { format },
        responseType: 'blob' // 处理文件流
    })

// 4. 获取执行日志摘要
// 对应需求：没成功显示原因。获取后台算法（如 Plink/GEMMA）输出的原始错误日志摘要
export const getExecutionSummaryAPI = (projectId: string) =>
    request({
        url: `/api/report/execution-summary/${projectId}`,
        method: 'get'
    })

// 5. 获取数据分布统计（用于 QC 确认页面的直方图/饼图）
// 比如：清洗前后的杂合度分布、样本缺失率分布，辅助用户“确认清洗或保留”
export const getDataDistributionAPI = (projectId: string, metric: 'maf' | 'missing' | 'hwe') =>
    request({
        url: `/api/report/distribution/${projectId}`,
        method: 'get',
        params: { metric }
    })

/**
 * 响应结构示例 (getQCDetailReportAPI):
 * {
 *   total_initial_snps: 500000,
 *   total_removed_snps: 12400,
 *   rejection_reasons: [
 *     { reason: "Minor Allele Frequency (MAF) < 0.01", count: 8000, samples: ["rs123", "rs456"] },
 *     { reason: "Hardy-Weinberg Equilibrium (HWE) < 1e-6", count: 4400, samples: ["rs789"] }
 *   ],
 *   status: "WAITING_CONFIRMATION" // 对应你要求的“用户确认”状态
 * }
 */