import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    const { data } = response
    // 处理JWT登录接口返回的原始格式
    if (data.access && data.refresh) {
      return data
    }
    // 处理统一响应格式
    if (data.code !== undefined && data.code !== 200) {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message))
    }
    return data.data || data
  },
  (error) => {
    const { response } = error
    
    if (response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      window.location.href = '/login'
      ElMessage.error('登录已过期，请重新登录')
    } else {
      ElMessage.error(response?.data?.detail || response?.data?.message || '网络错误')
    }
    
    return Promise.reject(error)
  }
)

export default api
