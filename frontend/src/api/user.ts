import request from '@/utils/request'

/**
 * 用户身份验证与个人中心接口
 */

// 1. 用户登录
// 登录成功后应返回 token，用于解锁历史记录和个人中心菜单
export const loginAPI = (data: any) =>
    request({
        url: '/api/user/login',
        method: 'post',
        data
    })

// 2. 用户注册
export const registerAPI = (data: any) =>
    request({
        url: '/api/user/register',
        method: 'post',
        data
    })

// 3. 获取个人详细信息
// 用于进入“个人中心”页面展示，或在侧边栏显示用户头像和昵称
export const getUserInfoAPI = () =>
    request({
        url: '/api/user/info',
        method: 'get'
    })

// 4. 修改个人信息 (昵称等)
// 对应需求：个人中心可以修改头像和昵称等个人信息
export const updateProfileAPI = (data: { nickname?: string, email?: string }) =>
    request({
        url: '/api/user/update',
        method: 'patch',
        data
    })

// 5. 上传/更换头像
// 专门处理头像文件的上传接口
export const uploadAvatarAPI = (data: FormData) =>
    request({
        url: '/api/user/avatar',
        method: 'post',
        data,
        headers: { 'Content-Type': 'multipart/form-data' }
    })

// 6. 安全退出
// 通知后端注销当前 token
export const logoutAPI = () =>
    request({
        url: '/api/user/logout',
        method: 'post'
    })

// 7. 修改密码
export const changePasswordAPI = (data: any) =>
    request({
        url: '/api/user/password',
        method: 'post',
        data
    })

/**
 * 响应结构示例 (getUserInfoAPI):
 * {
 *   id: "user-001",
 *   username: "gwas_researcher",
 *   nickname: "张科研",
 *   avatar: "http://example.com/storage/avatars/user-001.jpg",
 *   role: "user", // 或 "guest"
 *   created_at: "2023-01-01"
 * }
 */