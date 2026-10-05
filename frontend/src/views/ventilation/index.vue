<template>
  <section class="page" data-module="ventilation">
    <header class="page-head">
      <div>
        <h2>通风系统管理</h2>
        <p class="page-desc">维护通风设备，围绕设备编号、设备类型、额定风量、运行频率做登记、筛选与状态流转。</p>
      </div>
      <div class="page-actions">
        <button class="btn primary" type="button" @click="openCreate">登记通风设备</button>
        <button class="btn" type="button" @click="exportRows">导出通风系统清单</button>
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
          <td :colspan="columns.length + 1" class="empty-state">暂无通风系统数据，可先登记通风设备</td>
        </tr>
      </tbody>
    </table>

    <footer class="page-foot">
      <span>共 {{ total }} 条通风系统记录</span>
      <span v-if="errorMessage" class="error-text">{{ errorMessage }}</span>
    </footer>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

import { useEntryPage } from '@/api/entries'

const ENDPOINT = '/api/ventilation'
const columns = ["设备编号", "设备类型", "额定风量", "运行频率", "电流值", "所属巷道", "上次检修", "设备状态"]
const actions = ["降频运行", "故障停机", "办理更换"]
const statuses = ["正常", "降频运行", "故障停机", "已更换"]
const stats = [{"label": "正常设备", "value": 0}, {"label": "降频设备", "value": 0}, {"label": "故障设备", "value": 0}]

const { rows, total, errorMessage, filters, reload, resetFilters, runAction } = useEntryPage({
  endpoint: ENDPOINT,
  label: '通风系统',
})
const filterFields = columns.slice(0, 3)

function exportRows() {
  window.open(`${ENDPOINT}/export`, '_blank')
}

function openCreate() {
  errorMessage.value = '通风设备登记入口尚未接入审批流'
}

onMounted(reload)
</script>
