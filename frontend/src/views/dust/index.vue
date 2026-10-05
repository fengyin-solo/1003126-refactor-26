<template>
  <section class="page" data-module="dust">
    <header class="page-head">
      <div>
        <h2>粉尘防治管理</h2>
        <p class="page-desc">维护粉尘测点，围绕测点编号、所在区域、粉尘浓度、游离二氧化硅做登记、筛选与状态流转。</p>
      </div>
      <div class="page-actions">
        <button class="btn primary" type="button" @click="openCreate">登记粉尘测点</button>
        <button class="btn" type="button" @click="exportRows">导出粉尘防治清单</button>
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
          <td :colspan="columns.length + 1" class="empty-state">暂无粉尘防治数据，可先登记粉尘测点</td>
        </tr>
      </tbody>
    </table>

    <footer class="page-foot">
      <span>共 {{ total }} 条粉尘防治记录</span>
      <span v-if="errorMessage" class="error-text">{{ errorMessage }}</span>
    </footer>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

import { useEntryPage } from '@/api/entries'

const ENDPOINT = '/api/dust'
const columns = ["测点编号", "所在区域", "粉尘浓度", "游离二氧化硅", "降尘措施", "降尘效率", "监测日期", "测点状态"]
const actions = ["限值预警", "超标治理", "治理确认"]
const statuses = ["达标", "接近限值", "超标", "已治理"]
const stats = [{"label": "达标测点", "value": 0}, {"label": "接近限值测点", "value": 0}, {"label": "超标测点", "value": 0}]

const { rows, total, errorMessage, filters, reload, resetFilters, runAction } = useEntryPage({
  endpoint: ENDPOINT,
  label: '粉尘防治',
})
const filterFields = columns.slice(0, 3)

function exportRows() {
  window.open(`${ENDPOINT}/export`, '_blank')
}

function openCreate() {
  errorMessage.value = '粉尘测点登记入口尚未接入审批流'
}

onMounted(reload)
</script>
