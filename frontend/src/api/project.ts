import request from '@/utils/request'

/**
 * GWAS 项目管理接口
 */

// 1. 获取项目列表 (历史记录)
// 登录后侧边栏展示的已命名或按时间命名的项目列表
export const getProjectListAPI = () =>
    request({
        url: '/api/projects',
        method: 'get'
    })

// 2. 获取单个项目详细信息
// 用于进入某个历史项目时，恢复当时的文件状态、QC 结果和可视化数据
export const getProjectDetailAPI = (projectId: string) =>
    request({
        url: `/api/projects/${projectId}`,
        method: 'get'
    })

// 3. 更新项目信息 (重命名/修改昵称)
// 对应你要求的“未命名按时间命名”，用户可以在此处自定义项目名称
export const updateProjectAPI = (projectId: string, data: { name?: string, description?: string, current_step?: string, sample_count?: number, snp_count?: number }) =>
    request({
        url: `/api/projects/${projectId}`,
        method: 'patch',
        data
    })

// 4. 删除项目
// 对应你要求的“记录清除”，需同步删除服务器上的物理文件
export const deleteProjectAPI = (projectId: string) =>
    request({
        url: `/api/projects/${projectId}`,
        method: 'delete'
    })

// 5. 初始化新项目 (空项目占位)
// 当用户点击“创建新项目”但尚未上传文件时，可以先在后端生成一个 UUID
export const createProjectAPI = (data: { id?: string, name?: string }) =>
    request({
        url: '/api/projects',
        method: 'post',
        data
    })

// 6. 获取项目统计摘要
// 用于在“个人中心”或“历史记录”概览页显示：如总共有多少项目，总占用磁盘空间等
export const getProjectSummaryAPI = () =>
    request({
        url: '/api/projects/summary',
        method: 'get'
    })

/**
 * 返回数据结构示例 (getProjectListAPI):
 * [
 *   {
 *     id: "uuid-12345",
 *     name: "大豆抗旱性分析_20231001", // 用户命名的名称
 *     created_at: "2023-10-01 12:00:00", // 未命名时前端显示的备选名称
 *     status: "COMPLETED",
 *     step: "VIZ" // 用于控制侧边栏变黑/变灰的进度标记
 *   }
 * ]
 */