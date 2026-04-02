import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getUserInfo } from '@/api/auth'
import type { LoginForm, LoginRes, UserInfo } from '@/types/user'

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref<string>(localStorage.getItem('token') || '')
  const refreshToken = ref<string>(localStorage.getItem('refreshToken') || '')
  const userInfo = ref<UserInfo | null>(null)

  // Getters
  const isLoggedIn = computed(() => !!token.value)
  const username = computed(() => userInfo.value?.username || '')

  // Actions
  const setToken = (access: string, refresh: string) => {
    token.value = access
    refreshToken.value = refresh
    localStorage.setItem('token', access)
    localStorage.setItem('refreshToken', refresh)
  }

  const clearToken = () => {
    token.value = ''
    refreshToken.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  }

  const login = async (form: LoginForm) => {
    const res: LoginRes = await loginApi(form)
    setToken(res.access, res.refresh)
    await fetchUserInfo()
    return res
  }

  const fetchUserInfo = async () => {
    const res = await getUserInfo()
    userInfo.value = res
    return res
  }

  const logout = () => {
    clearToken()
  }

  return {
    token,
    refreshToken,
    userInfo,
    isLoggedIn,
    username,
    login,
    logout,
    fetchUserInfo,
    setToken,
    clearToken
  }
})
