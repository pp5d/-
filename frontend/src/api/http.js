import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({ baseURL: '/api', timeout: 60000 })

http.interceptors.request.use((cfg) => {
  const token = localStorage.getItem('token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

http.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const status = err.response?.status
    const detail = err.response?.data?.detail
    if (status === 401) {
      localStorage.removeItem('token')
      if (location.pathname.startsWith('/login')) {
        ElMessage.error(typeof detail === 'string' ? detail : '用户名或密码错误')
      } else {
        location.href = '/login'
      }
    } else {
      ElMessage.error(typeof detail === 'string' ? detail : '网络错误，请稍后重试')
    }
    return Promise.reject(err)
  }
)

export default http
