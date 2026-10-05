<template>
  <section class="page" data-module="certificate">
    <header class="page-head">
      <div>
        <h2>持证管理管理</h2>
        <p class="page-desc">维护持证人员，围绕人员编号、姓名、证书类别、证书编号做登记、筛选与状态流转。</p>
      </div>
      <div class="page-actions">
        <button class="btn primary" type="button" @click="openCreate">登记持证人员</button>
        <button class="btn" type="button" @click="exportRows">导出持证管理清单</button>
      </div>
    </header>

    <div class="stat-row">
      <article v-for="item in stats" :key="item.label" class="stat-card">
        <span class="stat-label">{{ item.label }}</span>
        <strong class="stat-value">{{ item.value }}</strong>
      </article>
    </div>

    <form class="filter-bar" @submit.prevent="reload">
      <label v-for="field in filterFields" :key="field" class="filter-item">
        <span>{{ field }}</span>
        <input v-model="filters[field]" :placeholder="`按${field}检索`" />
      </label>
      <button class="btn" type="submit">查询</button>
      <button class="btn ghost" type="button" @click="resetFilters">重置条件</button>
    </form>

    <table class="data-table">
      <thead>
        <tr>
          <th v-for="column in columns" :key="column">{{ column }}</th>
          <th>可执行动作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="String(row.id)">
          <td v-for="column in columns" :key="column">{{ row[column] ?? '—' }}</td>
          <td class="row-actions">
            <button
              v-for="action in actions"
              :key="action"
              class="link"
              type="button"
              @click="runAction(action, row)"
            >
              {{ action }}
            </button>
          </td>
        </tr>
        <tr v-if="!rows.length">
          <td :colspan="columns.length + 1" class="empty-state">暂无持证管理数据，可先登记持证人员</td>
        </tr>
      </tbody>
    </table>

    <footer class="page-foot">
      <span>共 {{ total }} 条持证管理记录</span>
      <span v-if="errorMessage" class="error-text">{{ errorMessage }}</span>
    </footer>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

import { useEntryPage } from '@/api/entries'

const ENDPOINT = '/api/certificate'
const columns = ["人员编号", "姓名", "证书类别", "证书编号", "发证日期", "到期日期", "复训记录", "证书状态"]
const actions = ["安排复训", "登记过期", "注销证书"]
const statuses = ["持证有效", "即将到期", "已过期", "已注销"]
const stats = [{"label": "持证人员", "value": 0}, {"label": "到期人员", "value": 0}, {"label": "过期人员", "value": 0}]

const { rows, total, errorMessage, filters, reload, resetFilters, runAction } = useEntryPage({
  endpoint: ENDPOINT,
  label: '持证管理',
})
const filterFields = columns.slice(0, 3)

function exportRows() {
  window.open(`${ENDPOINT}/export`, '_blank')
}

function openCreate() {
  errorMessage.value = '持证人员登记入口尚未接入审批流'
}

onMounted(reload)
</script>
