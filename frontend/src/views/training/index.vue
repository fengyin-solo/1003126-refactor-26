<template>
  <section class="page" data-module="training">
    <header class="page-head">
      <div>
        <h2>安全培训管理</h2>
        <p class="page-desc">维护培训记录，围绕培训编号、培训主题、培训对象、培训日期做登记、筛选与状态流转。</p>
      </div>
      <div class="page-actions">
        <button class="btn primary" type="button" @click="openCreate">登记培训记录</button>
        <button class="btn" type="button" @click="exportRows">导出安全培训清单</button>
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
          <td :colspan="columns.length + 1" class="empty-state">暂无安全培训数据，可先登记培训记录</td>
        </tr>
      </tbody>
    </table>

    <footer class="page-foot">
      <span>共 {{ total }} 条安全培训记录</span>
      <span v-if="errorMessage" class="error-text">{{ errorMessage }}</span>
    </footer>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

import { useEntryPage } from '@/api/entries'

const ENDPOINT = '/api/training'
const columns = ["培训编号", "培训主题", "培训对象", "培训日期", "培训讲师", "考核方式", "考核结果", "培训状态"]
const actions = ["组织培训", "组织考核", "归档"]
const statuses = ["待培训", "培训中", "已考核", "已归档"]
const stats = [{"label": "待培训人数", "value": 0}, {"label": "已考核人数", "value": 0}, {"label": "合格率", "value": 0}]

const { rows, total, errorMessage, filters, reload, resetFilters, runAction } = useEntryPage({
  endpoint: ENDPOINT,
  label: '安全培训',
})
const filterFields = columns.slice(0, 3)

function exportRows() {
  window.open(`${ENDPOINT}/export`, '_blank')
}

function openCreate() {
  errorMessage.value = '培训记录登记入口尚未接入审批流'
}

onMounted(reload)
</script>
