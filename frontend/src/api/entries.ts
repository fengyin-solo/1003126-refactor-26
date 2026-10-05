/** 动作链路共用流程：动作请求、回执解析、列表重新拉取，所有业务模块共用这一份实现。 */
import { ref } from 'vue'

import { request } from './client'

export type Row = Record<string, string | number | null>

/** 动作回执：后端所有模块的动作接口都按这一份结构返回执行结果。 */
export type ActionReceipt = {
  ok: boolean
  action: string
  message: string
  status: string | null
  entry: Row | null
  request_id: string | null
  replayed: boolean
}

type PagePayload = {
  items?: Row[]
  total?: number
}

function newRequestId(): string {
  // 每次提交生成一个幂等键：同一提交重复到达后端时只生效一次
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }
  return `req-${Date.now()}-${Math.random().toString(36).slice(2)}`
}

/** 动作请求与回执解析：动作名与幂等键放在请求体最外层，回执按统一结构校验。 */
export async function postEntryAction(
  endpoint: string,
  entryId: string | number,
  action: string,
  requestId: string,
): Promise<ActionReceipt> {
  const response = await request(`${endpoint}/${entryId}/actions`, {
    method: 'POST',
    body: JSON.stringify({ action, request_id: requestId }),
  })
  const receipt = (await response.json().catch(() => null)) as ActionReceipt | null
  if (!response.ok) {
    throw new Error(receipt?.message || `接口返回 ${response.status}，动作未生效`)
  }
  if (!receipt || typeof receipt.ok !== 'boolean') {
    throw new Error('动作回执格式无法识别')
  }
  return receipt
}

/** 列表重新拉取：所有模块共用同一种查询拼法与分页解析。 */
export async function fetchEntryPage(endpoint: string, filters: Record<string, string>): Promise<PagePayload> {
  const query = new URLSearchParams(filters).toString()
  const response = await request(`${endpoint}?${query}`)
  if (!response.ok) {
    throw new Error(`接口返回 ${response.status}，列表读取失败`)
  }
  return (await response.json()) as PagePayload
}

/** 模块页面的共用状态与流程：列表、筛选、动作执行、动作后的列表重拉。 */
export function useEntryPage(options: { endpoint: string; label: string }) {
  const { endpoint, label } = options
  const rows = ref<Row[]>([])
  const total = ref(0)
  const errorMessage = ref('')
  const filters = ref<Record<string, string>>({})
  const actionPending = ref(false)

  async function reload() {
    errorMessage.value = ''
    try {
      const payload = await fetchEntryPage(endpoint, filters.value)
      rows.value = payload.items ?? []
      total.value = payload.total ?? rows.value.length
    } catch (error) {
      errorMessage.value = error instanceof Error ? error.message : `${label}列表读取失败`
    }
  }

  function resetFilters() {
    filters.value = {}
    void reload()
  }

  async function runAction(action: string, row: Row) {
    if (actionPending.value) {
      return // 上一次动作尚未回执，忽略重复点击，同一提交只生效一次
    }
    actionPending.value = true
    errorMessage.value = ''
    try {
      const receipt = await postEntryAction(endpoint, row.id ?? '', action, newRequestId())
      if (!receipt.ok) {
        errorMessage.value = receipt.message || `${label}动作未生效，请稍后重试`
        return
      }
      // 动作成功后重新拉取列表：列表、详情、运营概览读到的都是同一份最新数据
      await reload()
    } catch (error) {
      errorMessage.value = error instanceof Error ? error.message : `${label}操作失败`
    } finally {
      actionPending.value = false
    }
  }

  return { rows, total, errorMessage, filters, actionPending, reload, resetFilters, runAction }
}
