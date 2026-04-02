// Dashboard API 接口
import request from '@/utils/request'

// 获取仪表盘统计数据
export function getDashboardStats() {
  return request({
    url: '/v1/dashboard/stats/',
    method: 'get'
  })
}

// 获取销售趋势
export function getSalesTrend(params: { days: number }) {
  return request({
    url: '/v1/dashboard/sales-trend/',
    method: 'get',
    params
  })
}

// 获取订单分布
export function getOrderDistribution() {
  return request({
    url: '/v1/dashboard/order-distribution/',
    method: 'get'
  })
}

// 获取热销商品
export function getTopProducts() {
  return request({
    url: '/v1/dashboard/top-products/',
    method: 'get'
  })
}