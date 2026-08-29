const DEFAULT_FIELDS = ['TRDPRC_1', 'SETTLE', 'OPINT_1']
const FIELD_OPTIONS = [
  { group: 'Prices', code: 'TRDPRC_1', label: 'Trade price', description: 'Last traded level' },
  { group: 'Prices', code: 'SETTLE', label: 'Settlement', description: 'Exchange settlement' },
  { group: 'Prices', code: 'BID', label: 'Bid', description: 'Highest displayed bid' },
  { group: 'Prices', code: 'ASK', label: 'Ask', description: 'Lowest displayed offer' },
  { group: 'Prices', code: 'OPEN_PRC', label: 'Open price', description: 'Session open' },
  { group: 'Prices', code: 'HIGH_1', label: 'High price', description: 'Session high' },
  { group: 'Prices', code: 'LOW_1', label: 'Low price', description: 'Session low' },
  { group: 'Activity', code: 'OPINT_1', label: 'Open interest', description: 'Open contracts' },
  { group: 'Activity', code: 'ACVOL_1', label: 'Accumulated volume', description: 'Contract activity' },
]
const CHART_COLORS = ['#ef8e55', '#63c7b2', '#8ca4ff', '#e7c66b', '#d983b8', '#9ccf72']
const PAGE_SIZE = 25

const state = {
  datasets: [],
  selectedName: null,
  dataset: null,
  loading: true,
  detailLoading: false,
  error: '',
  fetching: false,
  fetchMessage: '',
  fetchMessageType: '',
  fileSearch: '',
  fieldPickerOpen: false,
  page: 0,
  selectedSeries: [],
  instruments: ['VXc1', 'VXc2'],
  fields: DEFAULT_FIELDS.slice(),
  start: threeYearsAgo(),
  end: today(),
}

function today() {
  return new Date().toISOString().slice(0, 10)
}

function threeYearsAgo() {
  const date = new Date()
  date.setFullYear(date.getFullYear() - 3)
  return date.toISOString().slice(0, 10)
}

async function requestJson(url, options) {
  const response = await fetch(url, options)
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.detail || `Request failed (${response.status})`)
  }
  return response.json()
}

async function loadDatasets(preferredName = null) {
  state.loading = true
  render()
  try {
    const result = await requestJson('/datasets')
    state.datasets = result.datasets
    const nextName = preferredName || state.selectedName || result.datasets[0]?.name || null
    state.selectedName = nextName
    if (nextName) await loadDataset(nextName, false)
    state.error = ''
  } catch (error) {
    state.error = error.message
  } finally {
    state.loading = false
    render()
  }
}

async function loadDataset(name, shouldRender = true) {
  state.selectedName = name
  state.detailLoading = true
  state.page = 0
  if (shouldRender) render()
  try {
    const result = await requestJson(`/datasets/${encodeURIComponent(name)}`)
    state.dataset = result
    state.selectedSeries = result.columns.filter((column) => column.type === 'number').map((column) => column.key)
    state.error = ''
  } catch (error) {
    state.error = error.message
  } finally {
    state.detailLoading = false
    if (shouldRender) render()
  }
}

async function submitFetch(event) {
  event.preventDefault()
  if (!state.instruments.length || !state.fields.length || !state.start || !state.end) {
    state.error = 'Add at least one ticker, one field, and both dates before fetching.'
    render()
    return
  }
  if (state.start > state.end) {
    state.error = 'The start date must be before the end date.'
    render()
    return
  }

  state.fetching = true
  state.fetchMessage = 'Connecting to Workspace...'
  state.fetchMessageType = 'loading'
  state.error = ''
  render()

  try {
    const result = await requestJson('/history', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        instruments: state.instruments,
        fields: state.fields,
        start: state.start,
        end: state.end,
        interval: '1D',
      }),
    })
    state.fetchMessage = `Saved ${result.row_count.toLocaleString()} rows`
    state.fetchMessageType = 'success'
    await loadDatasets(result.output_file.split('/').pop())
  } catch (error) {
    state.error = error.message
    state.fetchMessage = `Fetch failed: ${error.message}`
    state.fetchMessageType = 'error'
  } finally {
    state.fetching = false
    render()
  }
}

function render() {
  const app = document.querySelector('#app')
  const dataset = state.dataset
  const chartColumns = dataset?.columns.filter((column) => column.type === 'number') || []
  const dateColumn = dataset?.columns.find((column) => column.type === 'date') || dataset?.columns[0]
  const pageCount = dataset ? Math.max(1, Math.ceil(dataset.rows.length / PAGE_SIZE)) : 1
  const tableRows = dataset?.rows.slice(state.page * PAGE_SIZE, (state.page + 1) * PAGE_SIZE) || []
  const filteredDatasets = state.datasets.filter((item) => item.name.toLowerCase().includes(state.fileSearch.toLowerCase()))

  app.innerHTML = `<div class="app-shell">
    <header class="topbar">
      <a class="brand" href="/"><span class="brand-mark">${activityIcon()}</span><span>Signal Desk</span></a>
      <div class="topbar-meta"><span class="live-dot"></span><span>Workspace connected locally</span></div>
    </header>
    <main class="page-content">
      <section class="intro-row">
        <div><p class="eyebrow">${sparklesIcon()} Market data workspace</p><h1>Explore the curve.</h1><p class="intro-copy">Fetch, compare, and inspect your LSEG datasets in one calm place.</p></div>
        <div class="metric-strip"><div><strong>${state.datasets.length}</strong><span>datasets</span></div><div><strong>${dataset ? dataset.row_count.toLocaleString() : '—'}</strong><span>rows selected</span></div><div><strong>${dataset?.columns.length || '—'}</strong><span>columns</span></div></div>
      </section>
      ${state.error ? `<div class="alert error">${alertIcon()}<span>${escapeHtml(state.error)}</span><button data-action="dismiss-error" aria-label="Dismiss error">${xIcon()}</button></div>` : ''}
      <div class="workspace-grid">
        <aside class="control-column">
          <section class="panel fetch-panel">
            <div class="panel-heading"><div><span class="section-number">01</span><h2>Fetch history</h2></div>${slidersIcon()}</div>
            <p class="panel-note">Choose the instruments, fields, and period to request from Workspace.</p>
            <form id="fetch-form">
              ${instrumentPicker()}
              ${fieldPicker()}
              <div class="date-grid"><label class="field-label">Start date<input id="start-date" type="date" value="${escapeHtml(state.start)}"></label><label class="field-label">End date<input id="end-date" type="date" value="${escapeHtml(state.end)}"></label></div>
              <button class="primary-button" type="submit" ${state.fetching ? 'disabled' : ''}>${state.fetching ? loaderIcon() : plusIcon()}${state.fetching ? 'Fetching data...' : 'Fetch dataset'}</button>
              ${state.fetchMessage ? `<p class="fetch-message ${state.fetchMessageType}">${state.fetchMessageType === 'error' ? alertIcon() : checkIcon()}${escapeHtml(state.fetchMessage)}</p>` : ''}
            </form>
          </section>
          <section class="panel tips-panel"><div class="tips-icon">${databaseIcon()}</div><div><strong>Local by design</strong><p>Files stay in your configured <code>DATA_DIR</code>. Repeating a request refreshes the same CSV.</p></div></section>
        </aside>
        <section class="content-column">
          <section class="panel library-panel"><div class="panel-heading library-heading"><div><span class="section-number">02</span><h2>Dataset library</h2></div><button class="icon-button" data-action="refresh-datasets" title="Refresh datasets">${refreshIcon()}</button></div><div class="search-box">${searchIcon()}<input id="file-search" value="${escapeHtml(state.fileSearch)}" placeholder="Search CSV files"></div><div class="dataset-list">${state.loading ? `<div class="empty-state">${loaderIcon()}Loading datasets...</div>` : filteredDatasets.length ? filteredDatasets.map(datasetCard).join('') : `<div class="empty-state">${fileIcon()}No CSV datasets found.</div>`}</div></section>
          <section class="panel data-panel">${!dataset && !state.detailLoading ? blankSlate() : state.detailLoading ? `<div class="blank-slate">${loaderIcon()}<p>Opening dataset...</p></div>` : datasetView(dataset, chartColumns, dateColumn, tableRows, pageCount)}</section>
        </section>
      </div>
    </main>
    <footer><span>Financial Engineering</span><span>Data stays on this machine</span></footer>
  </div>`
  bindEvents()
}

function instrumentPicker() {
  return `<div class="token-field"><span class="field-label">Tickers</span><div class="token-box">${state.instruments.map((token) => `<span class="token">${escapeHtml(token)}<button type="button" data-remove-instrument="${escapeHtml(token)}" aria-label="Remove ${escapeHtml(token)}">${xIcon(12)}</button></span>`).join('')}<input id="instrument-input" placeholder="${state.instruments.length ? 'Add another' : 'Add RIC, press Enter'}"></div></div>`
}

function fieldPicker() {
  const selectedLabels = FIELD_OPTIONS.filter((option) => state.fields.includes(option.code)).map((option) => option.label)
  const groups = [...new Set(FIELD_OPTIONS.map((option) => option.group))]
  const menu = state.fieldPickerOpen ? `<div class="field-picker-menu"><div class="field-picker-menu-heading"><span>Choose data fields</span><button type="button" data-action="close-fields">Done</button></div>${groups.map((group) => `<div class="field-group"><span class="field-group-label">${group}</span>${FIELD_OPTIONS.filter((option) => option.group === group).map((option) => `<label class="field-option"><input type="checkbox" data-field="${option.code}" ${state.fields.includes(option.code) ? 'checked' : ''}><span class="fake-checkbox">${checkIcon(11)}</span><span><strong>${option.label}</strong><small>${option.description} · <code>${option.code}</code></small></span></label>`).join('')}</div>`).join('')}</div>` : ''
  return `<div class="field-picker"><span class="field-label">Fields</span><button type="button" class="field-picker-trigger ${state.fieldPickerOpen ? 'open' : ''}" data-action="toggle-fields"><span class="field-picker-copy"><strong>${state.fields.length} selected</strong><span>${escapeHtml(selectedLabels.join(', ') || 'Choose fields')}</span></span>${chevronDownIcon()}</button>${menu}</div>`
}

function datasetCard(dataset) {
  return `<button class="dataset-card ${dataset.name === state.selectedName ? 'active' : ''}" data-dataset="${escapeHtml(dataset.name)}"><span class="file-icon">${fileIcon()}</span><span class="dataset-card-copy"><strong>${escapeHtml(dataset.name)}</strong><span>${dataset.row_count.toLocaleString()} rows · ${dataset.columns.length} columns</span></span>${chevronRightIcon()}</button>`
}

function datasetView(dataset, chartColumns, dateColumn, tableRows, pageCount) {
  return `<div class="dataset-title-row"><div><p class="eyebrow">Selected dataset</p><h2>${escapeHtml(dataset.name)}</h2><p class="dataset-subtitle">${dataset.row_count.toLocaleString()} rows · ${dataset.date_range ? `${escapeHtml(dataset.date_range.start)} → ${escapeHtml(dataset.date_range.end)}` : 'No date range detected'}</p></div><a class="download-button" href="/datasets/${encodeURIComponent(dataset.name)}/download" download>${downloadIcon()}Download CSV</a></div>${chartPanel(dataset, chartColumns, dateColumn)}${tablePanel(dataset, tableRows, pageCount)}`
}

function chartPanel(dataset, columns, dateColumn) {
  return `<div class="chart-section"><div class="subsection-heading"><div><span class="eyebrow">03 · Visual view</span><h3>Series explorer</h3></div><span class="chart-hint">Select any numeric column</span></div>${columns.length ? `<div class="series-picker">${columns.map((column, index) => `<button class="series-toggle ${state.selectedSeries.includes(column.key) ? 'selected' : ''}" data-series="${escapeHtml(column.key)}"><span style="background-color:${CHART_COLORS[index % CHART_COLORS.length]}"></span>${escapeHtml(column.label)}</button>`).join('')}</div><div class="chart-wrap">${chartSvg(dataset.rows, columns, dateColumn)}</div>` : '<div class="chart-empty">No numeric columns were detected in this CSV.</div>'}</div>`
}

function chartSvg(rows, columns, dateColumn) {
  const selected = columns.filter((column) => state.selectedSeries.includes(column.key))
  if (!selected.length || !dateColumn) return '<div class="chart-empty">Select at least one series to draw the chart.</div>'
  const width = 900
  const height = 300
  const left = 58
  const right = 14
  const top = 14
  const bottom = 30
  const chartWidth = width - left - right
  const chartHeight = height - top - bottom
  const values = rows.flatMap((row) => selected.map((column) => Number(row[column.key]))).filter(Number.isFinite)
  if (!values.length) return '<div class="chart-empty">Selected columns contain no numeric values.</div>'
  let min = Math.min(...values)
  let max = Math.max(...values)
  if (min === max) { min -= 1; max += 1 }
  const x = (index) => left + (rows.length <= 1 ? 0 : (index / (rows.length - 1)) * chartWidth)
  const y = (value) => top + ((max - value) / (max - min)) * chartHeight
  const grid = Array.from({ length: 5 }, (_, index) => {
    const value = max - ((max - min) * index) / 4
    const lineY = top + (chartHeight * index) / 4
    return `<line class="chart-grid-line" x1="${left}" x2="${width - right}" y1="${lineY}" y2="${lineY}"></line><text class="chart-axis-label" x="${left - 8}" y="${lineY + 4}" text-anchor="end">${escapeHtml(formatValue(value))}</text>`
  }).join('')
  const labels = [0, Math.floor((rows.length - 1) / 2), rows.length - 1].filter((index, position, list) => index >= 0 && list.indexOf(index) === position).map((index) => `<text class="chart-axis-label" x="${x(index)}" y="${height - 8}" text-anchor="${index === 0 ? 'start' : index === rows.length - 1 ? 'end' : 'middle'}">${escapeHtml(String(rows[index][dateColumn.key] || '').slice(0, 10))}</text>`).join('')
  const paths = selected.map((column) => {
    let path = ''
    let connected = false
    rows.forEach((row, index) => {
      const value = Number(row[column.key])
      if (!Number.isFinite(value)) { connected = false; return }
      path += `${connected ? ' L' : ' M'} ${x(index).toFixed(2)} ${y(value).toFixed(2)}`
      connected = true
    })
    const color = CHART_COLORS[columns.findIndex((item) => item.key === column.key) % CHART_COLORS.length]
    return `<path class="chart-line" d="${path}" stroke="${color}"><title>${escapeHtml(column.label)}</title></path>`
  }).join('')
  return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Selected data series chart">${grid}${labels}${paths}</svg>`
}

function tablePanel(dataset, rows, pageCount) {
  const previousDisabled = state.page === 0 ? 'disabled' : ''
  const nextDisabled = state.page >= pageCount - 1 ? 'disabled' : ''
  return `<div class="table-section"><div class="subsection-heading"><div><span class="eyebrow">04 · Raw data</span><h3>Browse rows</h3></div><span class="chart-hint">Page ${state.page + 1} of ${pageCount}</span></div><div class="table-scroll"><table><thead><tr>${dataset.columns.map((column) => `<th>${escapeHtml(column.label)}</th>`).join('')}</tr></thead><tbody>${rows.map((row, rowIndex) => `<tr>${dataset.columns.map((column) => `<td class="${column.type === 'number' ? 'number-cell' : ''}">${escapeHtml(formatValue(row[column.key]))}</td>`).join('')}</tr>`).join('')}</tbody></table></div><div class="pagination"><span>${dataset.row_count.toLocaleString()} rows total</span><div><button data-action="previous-page" ${previousDisabled} aria-label="Previous page">${chevronLeftIcon()}</button><button data-action="next-page" ${nextDisabled} aria-label="Next page">${chevronRightIcon()}</button></div></div></div>`
}

function blankSlate() {
  return `<div class="blank-slate">${barChartIcon()}<h2>Select a dataset</h2><p>Fetch a new history or choose a CSV from the library to begin exploring.</p></div>`
}

function bindEvents() {
  document.querySelector('#fetch-form')?.addEventListener('submit', submitFetch)
  document.querySelector('#start-date')?.addEventListener('change', (event) => { state.start = event.target.value })
  document.querySelector('#end-date')?.addEventListener('change', (event) => { state.end = event.target.value })
  document.querySelector('#file-search')?.addEventListener('input', (event) => {
    state.fileSearch = event.target.value
    renderDatasetList()
  })
  document.querySelector('#instrument-input')?.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ',') {
      event.preventDefault()
      addInstrument(event.target.value)
    }
  })
  document.querySelectorAll('[data-remove-instrument]').forEach((button) => button.addEventListener('click', () => {
    state.instruments = state.instruments.filter((instrument) => instrument !== button.dataset.removeInstrument)
    render()
  }))
  document.querySelectorAll('[data-dataset]').forEach((button) => button.addEventListener('click', () => loadDataset(button.dataset.dataset)))
  document.querySelectorAll('[data-series]').forEach((button) => button.addEventListener('click', () => {
    const key = button.dataset.series
    state.selectedSeries = state.selectedSeries.includes(key) ? state.selectedSeries.filter((item) => item !== key) : [...state.selectedSeries, key]
    render()
  }))
  document.querySelectorAll('[data-field]').forEach((input) => input.addEventListener('change', () => {
    const code = input.dataset.field
    state.fields = state.fields.includes(code) ? state.fields.filter((field) => field !== code) : [...state.fields, code]
    state.fieldPickerOpen = true
    render()
  }))
  document.querySelectorAll('[data-action]').forEach((element) => element.addEventListener('click', () => handleAction(element.dataset.action)))
}

function renderDatasetList() {
  const list = document.querySelector('.dataset-list')
  if (!list) return
  const filteredDatasets = state.datasets.filter((item) => item.name.toLowerCase().includes(state.fileSearch.toLowerCase()))
  list.innerHTML = filteredDatasets.length ? filteredDatasets.map(datasetCard).join('') : '<div class="empty-state">No CSV datasets found.</div>'
  list.querySelectorAll('[data-dataset]').forEach((button) => button.addEventListener('click', () => loadDataset(button.dataset.dataset)))
}

function handleAction(action) {
  if (action === 'toggle-fields') state.fieldPickerOpen = !state.fieldPickerOpen
  if (action === 'close-fields') state.fieldPickerOpen = false
  if (action === 'dismiss-error') state.error = ''
  if (action === 'refresh-datasets') loadDatasets()
  if (action === 'previous-page') state.page = Math.max(0, state.page - 1)
  if (action === 'next-page') state.page = Math.min(Math.ceil(state.dataset.rows.length / PAGE_SIZE) - 1, state.page + 1)
  if (['toggle-fields', 'close-fields', 'dismiss-error', 'previous-page', 'next-page'].includes(action)) render()
}

function addInstrument(value) {
  const instrument = value.trim()
  if (!instrument || state.instruments.includes(instrument)) return
  state.instruments.push(instrument)
  render()
}

function formatValue(value) {
  if (value === null || value === undefined || value === '') return '—'
  if (typeof value === 'number') return value.toLocaleString(undefined, { maximumFractionDigits: 4 })
  return String(value)
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character]))
}

function icon(path, viewBox = '0 0 24 24') {
  return `<svg class="inline-icon" viewBox="${viewBox}" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${path}</svg>`
}

function activityIcon() { return icon('<path d="M3 12h4l3-8 4 16 3-8h4"/>') }
function sparklesIcon() { return icon('<path d="m12 3-1.2 4.8L6 9l4.8 1.2L12 15l1.2-4.8L18 9l-4.8-1.2L12 3Z"/><path d="m19 15-.6 2.4L16 18l2.4.6L19 21l.6-2.4L22 18l-2.4-.6L19 15Z"/>') }
function slidersIcon() { return icon('<path d="M4 6h16M4 12h16M4 18h16"/><circle cx="8" cy="6" r="2"/><circle cx="16" cy="12" r="2"/><circle cx="10" cy="18" r="2"/>') }
function alertIcon() { return icon('<circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/>') }
function xIcon(size = 15) { return `<svg class="inline-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>` }
function checkIcon(size = 14) { return `<svg class="inline-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 4 4L19 6"/></svg>` }
function loaderIcon() { return icon('<path d="M12 3a9 9 0 1 1-6.36 2.64"/>') }
function plusIcon() { return icon('<path d="M12 5v14M5 12h14"/>') }
function databaseIcon() { return icon('<ellipse cx="12" cy="5" rx="7" ry="3"/><path d="M5 5v7c0 1.66 3.13 3 7 3s7-1.34 7-3V5M5 12v7c0 1.66 3.13 3 7 3s7-1.34 7-3v-7"/>') }
function refreshIcon() { return icon('<path d="M20 11a8 8 0 0 0-14.9-3L3 11M4 4v4h4M4 13a8 8 0 0 0 14.9 3L21 13M20 20v-4h-4"/>') }
function searchIcon() { return icon('<circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 5 5"/>') }
function fileIcon() { return icon('<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>') }
function downloadIcon() { return icon('<path d="M12 3v12M7 10l5 5 5-5M5 21h14"/>') }
function chevronDownIcon() { return icon('<path d="m6 9 6 6 6-6"/>') }
function chevronRightIcon() { return icon('<path d="m9 18 6-6-6-6"/>') }
function chevronLeftIcon() { return icon('<path d="m15 18-6-6 6-6"/>') }
function barChartIcon() { return icon('<path d="M4 19V5M4 19h16M8 16v-4M12 16V8M16 16v-7"/>') }

render()
loadDatasets()
