import request from './request'
import type { LoginForm, LoginRes, UserInfo } from '@/types/user'

export const login = async (data: LoginForm): Promise<LoginRes> => {
  const res: any = await request.post('/v1/auth/login/', data)
  return res as LoginRes
}

export const getUserInfo = (): Promise<UserInfo> => {
  return request.get('/v1/auth/user/')
}

export const logout = () => {
  return request.post('/v1/auth/logout/')
}
