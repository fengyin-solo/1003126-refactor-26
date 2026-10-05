<template>
  <section class="page" data-module="roof">
    <header class="page-head">
      <div>
        <h2>顶板管理管理</h2>
        <p class="page-desc">维护顶板监测，围绕监测编号、所在工作面、离层量、锚杆受力做登记、筛选与状态流转。</p>
      </div>
      <div class="page-actions">
        <button class="btn primary" type="button" @click="openCreate">登记顶板监测</button>
        <button class="btn" type="button" @click="exportRows">导出顶板管理清单</button>
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
          <td :colspan="columns.length + 1" class="empty-state">暂无顶板管理数据，可先登记顶板监测</td>
        </tr>
      </tbody>
    </table>

    <footer class="page-foot">
      <span>共 {{ total }} 条顶板管理记录</span>
      <span v-if="errorMessage" class="error-text">{{ errorMessage }}</span>
    </footer>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

import { useEntryPage } from '@/api/entries'

const ENDPOINT = '/api/roof'
const columns = ["监测编号", "所在工作面", "离层量", "锚杆受力", "收敛变形", "监测日期", "监测人员", "顶板状态"]
const actions = ["离层预警", "变形报警", "加固完成"]
const statuses = ["稳定", "离层预警", "变形超标", "已加固"]
const stats = [{"label": "稳定区域", "value": 0}, {"label": "预警区域", "value": 0}, {"label": "报警区域", "value": 0}]

const { rows, total, errorMessage, filters, reload, resetFilters, runAction } = useEntryPage({
  endpoint: ENDPOINT,
  label: '顶板管理',
})
const filterFields = columns.slice(0, 3)

function exportRows() {
  window.open(`${ENDPOINT}/export`, '_blank')
}

function openCreate() {
  errorMessage.value = '顶板监测登记入口尚未接入审批流'
}

onMounted(reload)
</script>
