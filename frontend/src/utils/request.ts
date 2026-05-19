import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { useUserStore } from '@/store/user'

const service: AxiosInstance = axios.create({
    // 请确保这里的地址和你后端 Uvicorn 运行地址一致
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
    timeout: 60000
})

// 1. 请求拦截器 (保持不变)
service.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        const userStore = useUserStore()
        const token = userStore.token || localStorage.getItem('token')
        if (token && config.headers) {
            config.headers['Authorization'] = `Bearer ${token}`
        }
        return config
    },
    (error) => Promise.reject(error)
)

// 2. 响应拦截器 (彻底简化版)
service.interceptors.response.use(
    (response: AxiosResponse) => {
        // FastAPI 返回的 {access_token: "..."} 就在 response.data 里
        const res = response.data

        // ⭐ 放弃 res.code 检查，因为 FastAPI 默认不返回这个字段
        // 只有当后端明确给了错误码（且不是200）时才报错
        if (res && res.code !== undefined && res.code !== 200) {
            const msg = res.message || res.error_detail || '业务逻辑错误'
            return Promise.reject(new Error(msg))
        }

        // 只要能走到这里，说明 HTTP 状态码是 200，直接返回数据主体
        return res
    },
    (error) => {
        // 处理 401 授权失败（如密码错误或 Token 过期）
        if (error.response && error.response.status === 401) {
            console.error('认证失败，请检查账号密码')
        }
        return Promise.reject(error)
    }
)

export default service