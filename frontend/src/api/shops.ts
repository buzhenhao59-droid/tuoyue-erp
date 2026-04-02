// 店铺 API 接口
import request from '@/utils/request'

export interface Shop {
  id: number
  name: string
  platform: string
  platform_name: string
  shop_id: string
  status: string
  auth_status: string
}

// 获取店铺列表
export function getShops() {
  return request<{
    count: number
    results: Shop[]
  }>({
    url: '/v1/shops/',
    method: 'get'
  })
}

// 获取店铺详情
export function getShopDetail(id: number) {
  return request<Shop>({
    url: `/v1/shops/${id}/`,
    method: 'get'
  })
}

// 创建店铺
export function createShop(data: Partial<Shop>) {
  return request<Shop>({
    url: '/v1/shops/',
    method: 'post',
    data
  })
}

// 更新店铺
export function updateShop(id: number, data: Partial<Shop>) {
  return request<Shop>({
    url: `/v1/shops/${id}/`,
    method: 'put',
    data
  })
}

// 删除店铺
export function deleteShop(id: number) {
  return request({
    url: `/v1/shops/${id}/`,
    method: 'delete'
  })
}