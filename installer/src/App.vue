<template>
  <div class="installer-wrapper">
    <div class="installer-card">
      <!-- Header -->
      <div class="card-header">
        <div class="header-left">
          <div class="header-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
            </svg>
          </div>
          <div>
            <h1 class="header-title">SmartOffice Integration Installer</h1>
            <p class="header-subtitle">필수 업무 소프트웨어 통합 설치 관리자</p>
          </div>
        </div>
        <div class="header-badge" :class="globalStatusClass">
          {{ globalStatusText }}
        </div>
      </div>

      <!-- Toolbar -->
      <div class="toolbar">
        <div class="toolbar-left">
          <label class="auto-run-label">
            <input type="checkbox" v-model="autoRunOnRestart" class="checkbox" />
            <span class="checkmark"></span>
            <span>재부팅 시 자동으로 통합설치프로그램 실행</span>
            <span class="auto-run-note">*설치가 다 끝나지 않은 채 재부팅 될 경우</span>
          </label>
        </div>
        <div class="toolbar-right">
          <button class="btn btn-secondary" @click="rescan" :disabled="isScanning">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 4v6h-6"/><path d="M1 20v-6h6"/>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
            </svg>
            {{ isScanning ? '스캔 중...' : '재스캔' }}
          </button>
          <button class="btn btn-secondary" @click="openDownloadFolder">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
            </svg>
            다운로드 폴더
          </button>
          <button class="btn btn-primary" @click="installSelected" :disabled="!hasChecked || isInstalling">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            {{ isInstalling ? '설치 중...' : '설치' }}
          </button>
        </div>
      </div>

      <!-- Table -->
      <div class="table-container">
        <table class="app-table">
          <thead>
            <tr>
              <th class="col-check">
                <input type="checkbox" :checked="allChecked" @change="toggleAll" class="checkbox" />
              </th>
              <th class="col-order">
                <span class="badge-num">1</span> 순서
              </th>
              <th class="col-name">
                <span class="badge-num">2</span> 애플리케이션
              </th>
              <th class="col-status">
                <span class="badge-num">3</span> 설치 상태
              </th>
              <th class="col-process">
                프로세스
              </th>
              <th class="col-progress">
                <span class="badge-num">4</span> 진행률
              </th>
              <th class="col-desc">
                <span class="badge-num">5</span> 설명
              </th>
              <th class="col-path">설치 경로</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="app in apps"
              :key="app.id"
              :class="['table-row', { 'row-selected': app.checked, 'row-installing': app.status === 'Installing', 'row-completed': app.status === 'Completed' }]"
            >
              <td class="col-check">
                <input
                  type="checkbox"
                  v-model="app.checked"
                  class="checkbox"
                  :disabled="app.status === 'Completed' || app.status === 'Installing'"
                />
              </td>
              <td class="col-order">
                <span class="order-num">{{ app.order }}</span>
              </td>
              <td class="col-name">
                <div class="app-name-cell">
                  <div class="app-icon" :style="{ background: appIconColor(app) }">
                    {{ app.name.charAt(0) }}
                  </div>
                  <div>
                    <div class="app-name">{{ app.name }}</div>
                    <div class="app-version">v{{ app.version }}</div>
                  </div>
                  <span v-if="app.required" class="required-badge">필수</span>
                </div>
              </td>
              <td class="col-status">
                <span :class="['status-badge', statusClass(app.status)]">{{ statusLabel(app.status) }}</span>
              </td>
              <td class="col-process">
                <div class="process-cell">
                  <span :class="['process-dot', app.isRunning ? 'dot-running' : 'dot-stopped']"></span>
                  <span class="process-label">{{ app.isRunning ? '실행 중' : '중지됨' }}</span>
                </div>
              </td>
              <td class="col-progress">
                <div class="progress-cell">
                  <div class="progress-bar-bg">
                    <div
                      class="progress-bar-fill"
                      :style="{ width: app.progress + '%', background: progressColor(app) }"
                    ></div>
                  </div>
                  <span class="progress-text">{{ app.progress }}%</span>
                </div>
              </td>
              <td class="col-desc">
                <span class="desc-text" :title="app.description">{{ app.description }}</span>
              </td>
              <td class="col-path">
                <div class="path-cell">
                  <span class="path-text" :title="app.installPath">{{ app.installPath }}</span>
                  <span :class="['path-status', app.isInstalled ? 'path-exists' : 'path-missing']">
                    {{ app.isInstalled ? '✓' : '✗' }}
                  </span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Detail Panel -->
      <transition name="slide">
        <div v-if="selectedApp" class="detail-panel">
          <div class="detail-header">
            <span class="detail-title">📋 설치 경로 및 프로세스 정보</span>
            <button class="detail-close" @click="selectedApp = null">✕</button>
          </div>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">설치 경로</span>
              <span class="detail-value">{{ selectedApp.installPath }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">프로세스명</span>
              <span class="detail-value">{{ selectedApp.processName }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">파일 존재</span>
              <span :class="['detail-value', selectedApp.isInstalled ? 'text-success' : 'text-danger']">
                {{ selectedApp.isInstalled ? '설치됨' : '미설치' }}
              </span>
            </div>
            <div class="detail-item">
              <span class="detail-label">프로세스 상태</span>
              <span :class="['detail-value', selectedApp.isRunning ? 'text-success' : 'text-muted']">
                {{ selectedApp.isRunning ? '실행 중' : '중지됨' }}
              </span>
            </div>
          </div>
        </div>
      </transition>

      <!-- Status Bar -->
      <div class="status-bar">
        <div class="status-left">
          <div :class="['status-dot', actionStatus === 'Ready' ? 'dot-ready' : actionStatus === 'Error' ? 'dot-error' : 'dot-working']"></div>
          <span class="status-text">Action : {{ actionStatus }}</span>
        </div>
        <div class="status-right">
          <span class="status-info">설치됨 {{ installedCount }}/{{ apps.length }}</span>
          <span class="status-divider">|</span>
          <span class="status-info">실행 중 {{ runningCount }}</span>
          <span class="status-divider">|</span>
          <span class="status-info">선택됨 {{ checkedCount }}</span>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <transition name="toast">
      <div v-if="toast.show" :class="['toast', 'toast-' + toast.type]">
        {{ toast.message }}
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { applications } from './data/applications.js'

const apps = ref(JSON.parse(JSON.stringify(applications)))
const autoRunOnRestart = ref(false)
const isScanning = ref(false)
const isInstalling = ref(false)
const actionStatus = ref('Ready')
const selectedApp = ref(null)
const toast = ref({ show: false, message: '', type: 'info' })

const hasChecked = computed(() => apps.value.some(a => a.checked))
const allChecked = computed(() => apps.value.filter(a => a.status !== 'Completed').every(a => a.checked))
const installedCount = computed(() => apps.value.filter(a => a.isInstalled).length)
const runningCount = computed(() => apps.value.filter(a => a.isRunning).length)
const checkedCount = computed(() => apps.value.filter(a => a.checked).length)

const globalStatusClass = computed(() => {
  if (isInstalling.value) return 'badge-working'
  if (isScanning.value) return 'badge-scanning'
  if (apps.value.every(a => a.status === 'Completed')) return 'badge-done'
  return 'badge-ready'
})

const globalStatusText = computed(() => {
  if (isInstalling.value) return '설치 진행 중'
  if (isScanning.value) return '스캔 중'
  if (apps.value.every(a => a.status === 'Completed')) return '모두 완료'
  return '대기 중'
})

function toggleAll(e) {
  apps.value.forEach(app => {
    if (app.status !== 'Completed' && app.status !== 'Installing') {
      app.checked = e.target.checked
    }
  })
}

function statusClass(status) {
  const map = {
    'Completed': 'status-completed',
    'Not Install': 'status-not-install',
    'Installing': 'status-installing',
    'Failed': 'status-failed',
    'Downloading': 'status-downloading'
  }
  return map[status] || 'status-not-install'
}

function statusLabel(status) {
  const map = {
    'Completed': '설치 완료',
    'Not Install': '미설치',
    'Installing': '설치 중',
    'Failed': '실패',
    'Downloading': '다운로드 중'
  }
  return map[status] || status
}

function appIconColor(app) {
  const colors = ['#6366f1','#0ea5e9','#10b981','#f59e0b','#ef4444','#8b5cf6']
  return colors[(app.id - 1) % colors.length]
}

function progressColor(app) {
  if (app.progress === 100) return '#10b981'
  if (app.status === 'Failed') return '#ef4444'
  return '#3b82f6'
}

function showToast(message, type = 'info') {
  toast.value = { show: true, message, type }
  setTimeout(() => { toast.value.show = false }, 3000)
}

async function rescan() {
  isScanning.value = true
  actionStatus.value = '스캔 중...'
  showToast('설치 상태를 확인하고 있습니다...', 'info')

  for (let i = 0; i < apps.value.length; i++) {
    await sleep(300)
    // 실제 환경에서는 파일 시스템 / 프로세스 API 호출
    // 시뮬레이션: SmartOfficeManager는 설치된 상태로 유지
    const app = apps.value[i]
    if (app.id === 1) {
      app.isInstalled = true
      app.isRunning = true
      app.status = 'Completed'
      app.progress = 100
    } else {
      // 랜덤으로 일부 프로세스 실행 중으로 시뮬레이션
      app.isRunning = Math.random() > 0.7
    }
  }

  isScanning.value = false
  actionStatus.value = 'Ready'
  showToast('스캔이 완료되었습니다.', 'success')
}

async function installSelected() {
  const targets = apps.value.filter(a => a.checked && a.status !== 'Completed')
  if (!targets.length) return

  isInstalling.value = true
  actionStatus.value = '설치 중...'

  for (const app of targets) {
    app.status = 'Downloading'
    actionStatus.value = `다운로드 중: ${app.name}`
    showToast(`${app.name} 다운로드 중...`, 'info')

    // 다운로드 시뮬레이션
    for (let p = 0; p <= 40; p += 5) {
      await sleep(80)
      app.progress = p
    }

    app.status = 'Installing'
    actionStatus.value = `설치 중: ${app.name}`
    showToast(`${app.name} 설치 중...`, 'info')

    // 설치 시뮬레이션
    for (let p = 40; p <= 100; p += 5) {
      await sleep(100)
      app.progress = p
    }

    app.status = 'Completed'
    app.isInstalled = true
    app.checked = false
    showToast(`${app.name} 설치 완료!`, 'success')
    await sleep(200)
  }

  isInstalling.value = false
  actionStatus.value = 'Ready'
}

function openDownloadFolder() {
  showToast('다운로드 폴더: C:\\Users\\Public\\Downloads\\SmartOffice', 'info')
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

onMounted(() => {
  // 마운트 시 초기 스캔
  setTimeout(() => rescan(), 500)
})
</script>

<style scoped>
.installer-wrapper {
  width: 100%;
  max-width: 1200px;
  position: relative;
}

.installer-card {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08), 0 1px 4px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

/* Header */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
  color: white;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-icon {
  width: 44px;
  height: 44px;
  background: rgba(255,255,255,0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}

.header-title {
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.3px;
}

.header-subtitle {
  font-size: 12px;
  opacity: 0.75;
  margin-top: 2px;
}

.header-badge {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  backdrop-filter: blur(4px);
}
.badge-ready { background: rgba(255,255,255,0.2); }
.badge-working { background: rgba(251,191,36,0.3); color: #fef3c7; }
.badge-scanning { background: rgba(167,243,208,0.3); color: #d1fae5; }
.badge-done { background: rgba(52,211,153,0.3); color: #d1fae5; }

/* Toolbar */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  gap: 12px;
  flex-wrap: wrap;
}

.toolbar-left {
  display: flex;
  align-items: center;
}

.toolbar-right {
  display: flex;
  gap: 8px;
  align-items: center;
}

.auto-run-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 13px;
  color: #475569;
  user-select: none;
}

.auto-run-note {
  font-size: 11px;
  color: #ef4444;
  font-weight: 500;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  transition: all 0.15s;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #ffffff;
  color: #374151;
  border: 1px solid #d1d5db;
}
.btn-secondary:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.btn-primary {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: white;
  border: 1px solid transparent;
}
.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #1d4ed8, #2563eb);
  box-shadow: 0 2px 8px rgba(37,99,235,0.4);
}

/* Table */
.table-container {
  overflow-x: auto;
}

.app-table {
  width: 100%;
  border-collapse: collapse;
}

.app-table thead tr {
  background: #f1f5f9;
}

.app-table th {
  padding: 10px 12px;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
  white-space: nowrap;
}

.badge-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  background: #dc2626;
  color: white;
  border-radius: 50%;
  font-size: 10px;
  font-weight: 700;
  margin-right: 4px;
}

.col-check { width: 40px; text-align: center; }
.col-order { width: 56px; text-align: center; }
.col-name { min-width: 200px; }
.col-status { width: 110px; }
.col-process { width: 100px; }
.col-progress { width: 140px; }
.col-desc { min-width: 200px; }
.col-path { min-width: 220px; }

.table-row {
  transition: background 0.15s;
  border-bottom: 1px solid #f1f5f9;
}

.table-row:hover {
  background: #f8fafc;
}

.row-selected {
  background: #eff6ff !important;
}

.row-installing {
  background: #f0fdf4 !important;
}

.row-completed {
  opacity: 0.75;
}

.app-table td {
  padding: 10px 12px;
  font-size: 13px;
  color: #334155;
}

.order-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #e2e8f0;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #475569;
}

.app-name-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.app-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}

.app-name {
  font-weight: 600;
  font-size: 13px;
  color: #1e293b;
}

.app-version {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 1px;
}

.required-badge {
  padding: 2px 6px;
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
}

/* Status Badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}
.status-completed { background: #dcfce7; color: #16a34a; }
.status-not-install { background: #f1f5f9; color: #64748b; }
.status-installing { background: #dbeafe; color: #2563eb; }
.status-failed { background: #fee2e2; color: #dc2626; }
.status-downloading { background: #fef9c3; color: #ca8a04; }

/* Process Cell */
.process-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.process-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot-running {
  background: #22c55e;
  box-shadow: 0 0 0 3px rgba(34,197,94,0.2);
  animation: pulse 2s infinite;
}

.dot-stopped {
  background: #cbd5e1;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 3px rgba(34,197,94,0.2); }
  50% { box-shadow: 0 0 0 5px rgba(34,197,94,0.1); }
}

.process-label {
  font-size: 12px;
  color: #64748b;
}

/* Progress */
.progress-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar-bg {
  flex: 1;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 11px;
  font-weight: 600;
  color: #64748b;
  min-width: 30px;
  text-align: right;
}

/* Description */
.desc-text {
  font-size: 12px;
  color: #64748b;
  display: block;
  max-width: 220px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Path */
.path-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.path-text {
  font-size: 11px;
  color: #94a3b8;
  font-family: 'Courier New', monospace;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 160px;
}

.path-status {
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.path-exists { color: #22c55e; }
.path-missing { color: #ef4444; }

/* Checkbox */
.checkbox {
  width: 15px;
  height: 15px;
  accent-color: #2563eb;
  cursor: pointer;
}

/* Detail Panel */
.detail-panel {
  margin: 0 24px 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: #e2e8f0;
}

.detail-title {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
}

.detail-close {
  background: none;
  border: none;
  cursor: pointer;
  color: #64748b;
  font-size: 14px;
  padding: 2px 6px;
  border-radius: 4px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  padding: 14px 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.detail-label {
  font-size: 11px;
  color: #94a3b8;
  font-weight: 500;
}

.detail-value {
  font-size: 12px;
  color: #334155;
  font-weight: 500;
  word-break: break-all;
}

.text-success { color: #16a34a !important; }
.text-danger { color: #dc2626 !important; }
.text-muted { color: #94a3b8 !important; }

/* Status Bar */
.status-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 24px;
  background: #f1f5f9;
  border-top: 1px solid #e2e8f0;
}

.status-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot-ready { background: #22c55e; }
.dot-error { background: #ef4444; }
.dot-working { background: #f59e0b; animation: pulse 1.5s infinite; }

.status-text {
  font-size: 12px;
  font-weight: 600;
  color: #475569;
}

.status-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-info {
  font-size: 12px;
  color: #64748b;
}

.status-divider {
  color: #cbd5e1;
  font-size: 12px;
}

/* Transitions */
.slide-enter-active, .slide-leave-active {
  transition: all 0.25s ease;
}
.slide-enter-from, .slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* Toast */
.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 12px 20px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  z-index: 1000;
  max-width: 360px;
}
.toast-info { background: #1e40af; color: white; }
.toast-success { background: #166534; color: white; }
.toast-error { background: #991b1b; color: white; }

.toast-enter-active, .toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from { opacity: 0; transform: translateX(40px); }
.toast-leave-to { opacity: 0; transform: translateX(40px); }
</style>
