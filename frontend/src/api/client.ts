/** 统一请求封装：拼后端地址、抛网络错误、给页脚留一句可读的说明。 */
const API_BASE = import.meta.env.VITE_API_BASE ?? ''

export function request(path: string, init?: RequestInit): Promise<Response> {
  const url = path.startsWith('http') ? path : `${API_BASE}${path}`
  return fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  }).catch((error: unknown) => {
    const detail = error instanceof Error ? error.message : '请求未送达'
    throw new Error(`接口请求失败：${detail}`)
  })
}

export async function fetchJson<T>(path: string): Promise<T> {
  const response = await request(path)
  if (!response.ok) {
    throw new Error(`接口返回 ${response.status}，数据未更新`)
  }
  return (await response.json()) as T
}

/** 列表分页数据：与后端 PageResult 对应。 */
export type ListResult<T> = {
  items: T[]
  total: number
  page: number
  size: number
}

/** 动作回执：与后端 ActionResult 对应，所有模块共用这一份结构。 */
export type ActionReceipt = {
  ok: boolean
  message: string
  entry: Record<string, unknown> | null
  repeated: boolean
}

/** 列表重新拉取：各模块页面共用，查询条件原样拼到 query 上。 */
export async function fetchList<T>(
  endpoint: string,
  filters: Record<string, string>,
): Promise<ListResult<T>> {
  const query = new URLSearchParams(filters).toString()
  const payload = await fetchJson<ListResult<T>>(`${endpoint}?${query}`)
  return {
    ...payload,
    items: payload.items ?? [],
    total: payload.total ?? 0,
  }
}

/**
 * 动作请求共用流程：动作名放在请求体最外层，回执统一按 ActionReceipt 解析；
 * 接口层失败或回执 ok=false 都抛错，message 以后端回执为准。
 */
export async function postAction(
  endpoint: string,
  entryId: string | number,
  action: string,
): Promise<ActionReceipt> {
  const response = await request(`${endpoint}/${entryId}/actions`, {
    method: 'POST',
    body: JSON.stringify({ action }),
  })
  if (!response.ok) {
    throw new Error(`接口返回 ${response.status}，动作未送达`)
  }
  const receipt = (await response.json()) as ActionReceipt
  if (!receipt.ok) {
    throw new Error(receipt.message || '动作未生效')
  }
  return receipt
}
