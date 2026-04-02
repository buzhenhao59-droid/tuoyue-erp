export interface LoginForm {
  username: string
  password: string
}

export interface LoginRes {
  access: string
  refresh: string
  user: UserInfo
}

export interface UserInfo {
  id: number
  username: string
  email: string
  real_name: string
  avatar: string
  roles: string[]
}
