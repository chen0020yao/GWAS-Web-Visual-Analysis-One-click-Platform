import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { useUserStore } from '@/store/user'

const service: AxiosInstance = axios.create({
    // 请确保这里的地址和你后端 Uvicorn 运行地址一致
    baseURL: import.meta.env.VITE_API_BASE_URL || '',
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

// 2. 响应拦截器
service.interceptors.response.use(
    (response: AxiosResponse) => {
        return response.data
    },
    (error) => {
        // 提取后端返回的具体错误信息
        if (error.response) {
            const { status, data } = error.response

            if (status === 422 && data?.detail) {
                // Pydantic 校验失败：detail 是数组 [{loc, msg, type}]
                const messages = Array.isArray(data.detail)
                    ? data.detail.map((e: any) => {
                        const field = e.loc?.join('.') || ''
                        return field ? `${field}: ${e.msg}` : e.msg
                    }).join('；')
                    : data.detail
                return Promise.reject(new Error(messages))
            }

            if (status === 401) {
                return Promise.reject(new Error(data?.detail || '认证失败，请检查账号密码'))
            }

            if (status === 400) {
                return Promise.reject(new Error(data?.detail || '请求参数错误'))
            }

            if (status >= 500) {
                return Promise.reject(new Error(data?.detail || '服务器内部错误'))
            }

            return Promise.reject(new Error(data?.detail || `请求失败 (${status})`))
        }

        return Promise.reject(new Error('网络连接失败，请检查后端服务是否启动'))
    }
)

export default service