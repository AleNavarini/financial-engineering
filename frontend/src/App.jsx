import { useEffect, useState } from 'react'
import {
  Activity,
  CircleAlert,
  ArrowDownToLine,
  BarChart3,
  CalendarDays,
  Check,
  ChevronLeft,
  ChevronRight,
  Database,
  FileSpreadsheet,
  LoaderCircle,
  Plus,
  RefreshCw,
  Search,
  SlidersHorizontal,
  Sparkles,
  X,
} from 'lucide-react'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

const DEFAULT_FIELDS = ['TRDPRC_1', 'SETTLE', 'OPINT_1']
const CHART_COLORS = ['#ef8e55', '#63c7b2', '#8ca4ff', '#e7c66b', '#d983b8', '#9ccf72']
const PAGE_SIZE = 25

function isoToday() {
  return new Date().toISOString().slice(0, 10)
}

function isoThreeYearsAgo() {
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

function App() {
  const [datasets, setDatasets] = useState([])
  const [selectedName, setSelectedName] = useState(null)
  const [dataset, setDataset] = useState(null)
  const [loading, setLoading] = useState(true)
  const [detailLoading, setDetailLoading] = useState(false)
  const [error, setError] = useState('')
  const [fetching, setFetching] = useState(false)
  const [fetchMessage, setFetchMessage] = useState('')
  const [fetchMessageType, setFetchMessageType] = useState('')
  const [fileSearch, setFileSearch] = useState('')
  const [page, setPage] = useState(0)
  const [selectedSeries, setSelectedSeries] = useState([])
  const [instruments, setInstruments] = useState(['VXc1', 'VXc2'])
  const [instrumentInput, setInstrumentInput] = useState('')
  const [fields, setFields] = useState(DEFAULT_FIELDS)
  const [fieldInput, setFieldInput] = useState('')
  const [start, setStart] = useState(isoThreeYearsAgo)
  const [end, setEnd] = useState(isoToday)

  async function loadDatasets(preferredName = null) {
    setLoading(true)
    try {
      const result = await requestJson('/datasets')
      setDatasets(result.datasets)
      const nextName = preferredName || selectedName || result.datasets[0]?.name || null
      if (nextName) {
        setSelectedName(nextName)
      }
      setError('')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  async function loadDataset(name) {
    if (!name) return
    setSelectedName(name)
    setDetailLoading(true)
    setPage(0)
    try {
      const result = await requestJson(`/datasets/${encodeURIComponent(name)}`)
      setDataset(result)
      setSelectedSeries(result.columns.filter((column) => column.type === 'number').slice(0, 3).map((column) => column.key))
      setError('')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setDetailLoading(false)
    }
  }

  useEffect(() => {
    loadDatasets()
  }, [])

  useEffect(() => {
    if (selectedName && selectedName !== dataset?.name) {
      loadDataset(selectedName)
    }
  }, [selectedName])

  function addToken(value, setter, setInput) {
    const token = value.trim()
    if (!token) return
    setter((current) => current.includes(token) ? current : [...current, token])
    setInput('')
  }

  function removeToken(token, setter) {
    setter((current) => current.filter((item) => item !== token))
  }

  async function submitFetch(event) {
    event.preventDefault()
    if (!instruments.length || !fields.length || !start || !end) {
      setError('Add at least one ticker, one field, and both dates before fetching.')
      return
    }
    if (start > end) {
      setError('The start date must be before the end date.')
      return
    }
    setFetching(true)
    setFetchMessage('Connecting to Workspace...')
    setFetchMessageType('loading')
    setError('')
    try {
      const result = await requestJson('/history', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ instruments, fields, start, end, interval: '1D' }),
      })
      const name = result.output_file.split('/').pop()
      setFetchMessage(`Saved ${result.row_count.toLocaleString()} rows`)
      setFetchMessageType('success')
      await loadDatasets(name)
      await loadDataset(name)
    } catch (requestError) {
      setError(requestError.message)
      setFetchMessage(`Fetch failed: ${requestError.message}`)
      setFetchMessageType('error')
    } finally {
      setFetching(false)
    }
  }

  const filteredDatasets = datasets.filter((item) => item.name.toLowerCase().includes(fileSearch.toLowerCase()))
  const chartColumns = dataset?.columns.filter((column) => column.type === 'number') || []
  const dateColumn = dataset?.columns.find((column) => column.type === 'date') || dataset?.columns[0]
  const tableRows = dataset?.rows.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE) || []
  const pageCount = dataset ? Math.max(1, Math.ceil(dataset.rows.length / PAGE_SIZE)) : 1

  function toggleSeries(key) {
    setSelectedSeries((current) => current.includes(key) ? current.filter((item) => item !== key) : [...current, key])
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">
          <span className="brand-mark"><Activity size={18} /></span>
          <span>Signal Desk</span>
        </a>
        <div className="topbar-meta">
          <span className="live-dot" />
          <span>Workspace connected locally</span>
          <a href="/docs" target="_blank" rel="noreferrer">API docs</a>
        </div>
      </header>

      <main className="page-content">
        <section className="intro-row">
          <div>
            <p className="eyebrow"><Sparkles size={14} /> Market data workspace</p>
            <h1>Explore the curve.</h1>
            <p className="intro-copy">Fetch, compare, and inspect your LSEG datasets in one calm place.</p>
          </div>
          <div className="metric-strip">
            <div><strong>{datasets.length}</strong><span>datasets</span></div>
            <div><strong>{dataset?.row_count?.toLocaleString() || '—'}</strong><span>rows selected</span></div>
            <div><strong>{dataset?.columns?.length || '—'}</strong><span>columns</span></div>
          </div>
        </section>

        {error && <div className="alert error"><X size={17} /><span>{error}</span><button onClick={() => setError('')} aria-label="Dismiss error"><X size={15} /></button></div>}

        <div className="workspace-grid">
          <aside className="control-column">
            <section className="panel fetch-panel">
              <div className="panel-heading">
                <div><span className="section-number">01</span><h2>Fetch history</h2></div>
                <SlidersHorizontal size={17} />
              </div>
              <p className="panel-note">Choose the instruments, fields, and period to request from Workspace.</p>
              <form onSubmit={submitFetch}>
                <TokenInput label="Tickers" tokens={instruments} input={instrumentInput} setInput={setInstrumentInput} setTokens={setInstruments} placeholder="Add RIC, press Enter" onAdd={() => addToken(instrumentInput, setInstruments, setInstrumentInput)} onRemove={(token) => removeToken(token, setInstruments)} />
                <TokenInput label="Fields" tokens={fields} input={fieldInput} setInput={setFieldInput} setTokens={setFields} placeholder="Add field, press Enter" onAdd={() => addToken(fieldInput, setFields, setFieldInput)} onRemove={(token) => removeToken(token, setFields)} />
                <div className="date-grid">
                  <label className="field-label">Start date<input type="date" value={start} onChange={(event) => setStart(event.target.value)} /></label>
                  <label className="field-label">End date<input type="date" value={end} onChange={(event) => setEnd(event.target.value)} /></label>
                </div>
                <button className="primary-button" type="submit" disabled={fetching}>
                  {fetching ? <LoaderCircle className="spin" size={17} /> : <Plus size={17} />}
                  {fetching ? 'Fetching data...' : 'Fetch dataset'}
                </button>
                {fetchMessage && <p className={`fetch-message ${fetchMessageType}`}>
                  {fetchMessageType === 'error' ? <CircleAlert size={14} /> : <Check size={14} />}
                  {fetchMessage}
                </p>}
              </form>
            </section>

            <section className="panel tips-panel">
              <div className="tips-icon"><Database size={18} /></div>
              <div><strong>Local by design</strong><p>Files stay in your configured <code>DATA_DIR</code>. Repeating a request refreshes the same CSV.</p></div>
            </section>
          </aside>

          <section className="content-column">
            <section className="panel library-panel">
              <div className="panel-heading library-heading">
                <div><span className="section-number">02</span><h2>Dataset library</h2></div>
                <button className="icon-button" onClick={() => loadDatasets()} title="Refresh datasets"><RefreshCw size={16} /></button>
              </div>
              <div className="search-box"><Search size={16} /><input value={fileSearch} onChange={(event) => setFileSearch(event.target.value)} placeholder="Search CSV files" /></div>
              <div className="dataset-list">
                {loading ? <div className="empty-state"><LoaderCircle className="spin" size={19} />Loading datasets...</div> : filteredDatasets.length ? filteredDatasets.map((item) => <DatasetCard key={item.name} dataset={item} active={item.name === selectedName} onClick={() => setSelectedName(item.name)} />) : <div className="empty-state"><FileSpreadsheet size={19} />No CSV datasets found.</div>}
              </div>
            </section>

            <section className="panel data-panel">
              {!dataset && !detailLoading ? <div className="blank-slate"><BarChart3 size={34} /><h2>Select a dataset</h2><p>Fetch a new history or choose a CSV from the library to begin exploring.</p></div> : detailLoading ? <div className="blank-slate"><LoaderCircle className="spin" size={30} /><p>Opening dataset...</p></div> : <>
                <div className="dataset-title-row">
                  <div><p className="eyebrow">Selected dataset</p><h2>{dataset.name}</h2><p className="dataset-subtitle">{dataset.row_count.toLocaleString()} rows · {dataset.date_range ? `${dataset.date_range.start} → ${dataset.date_range.end}` : 'No date range detected'}</p></div>
                  <a className="download-button" href={`/datasets/${encodeURIComponent(dataset.name)}/download`} download><ArrowDownToLine size={16} />Download CSV</a>
                </div>
                <ChartPanel dataset={dataset} columns={chartColumns} dateColumn={dateColumn} selectedSeries={selectedSeries} onToggle={toggleSeries} />
                <TablePanel dataset={dataset} rows={tableRows} page={page} pageCount={pageCount} onPageChange={setPage} />
              </>}
            </section>
          </section>
        </div>
      </main>
      <footer><span>Financial Engineering</span><span>Data stays on this machine</span></footer>
    </div>
  )
}

function TokenInput({ label, tokens, input, setInput, placeholder, onAdd, onRemove }) {
  function handleKeyDown(event) {
    if (event.key === 'Enter' || event.key === ',') {
      event.preventDefault()
      onAdd()
    }
  }
  return <div className="token-field"><span className="field-label">{label}</span><div className="token-box">{tokens.map((token) => <span className="token" key={token}>{token}<button type="button" onClick={() => onRemove(token)} aria-label={`Remove ${token}`}><X size={12} /></button></span>)}<input value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={handleKeyDown} onBlur={onAdd} placeholder={tokens.length ? 'Add another' : placeholder} /></div></div>
}

function DatasetCard({ dataset, active, onClick }) {
  return <button className={`dataset-card ${active ? 'active' : ''}`} onClick={onClick}><span className="file-icon"><FileSpreadsheet size={18} /></span><span className="dataset-card-copy"><strong>{dataset.name}</strong><span>{dataset.row_count.toLocaleString()} rows · {dataset.columns.length} columns</span></span><ChevronRight className="card-arrow" size={16} /></button>
}

function ChartPanel({ dataset, columns, dateColumn, selectedSeries, onToggle }) {
  const chartRows = dataset.rows.filter((row) => row[dateColumn.key]).map((row) => ({ ...row, [dateColumn.key]: String(row[dateColumn.key]).slice(0, 10) }))
  return <div className="chart-section"><div className="subsection-heading"><div><span className="eyebrow">03 · Visual view</span><h3>Series explorer</h3></div><span className="chart-hint">Select any numeric column</span></div>{columns.length ? <><div className="series-picker">{columns.map((column, index) => <button key={column.key} className={`series-toggle ${selectedSeries.includes(column.key) ? 'selected' : ''}`} onClick={() => onToggle(column.key)}><span style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }} />{column.label}</button>)}</div><div className="chart-wrap"><ResponsiveContainer width="100%" height={300}><LineChart data={chartRows} margin={{ top: 10, right: 12, left: -16, bottom: 4 }}><CartesianGrid strokeDasharray="3 5" stroke="#d9dfdc" vertical={false} /><XAxis dataKey={dateColumn.key} tick={{ fill: '#71807d', fontSize: 11 }} tickLine={false} axisLine={false} minTickGap={38} /><YAxis tick={{ fill: '#71807d', fontSize: 11 }} tickLine={false} axisLine={false} width={50} domain={['auto', 'auto']} /><Tooltip content={<ChartTooltip />} /><Legend verticalAlign="top" align="right" height={32} wrapperStyle={{ fontSize: 11, color: '#526360' }} />{selectedSeries.map((key) => { const index = columns.findIndex((column) => column.key === key); return <Line key={key} type="monotone" dataKey={key} name={columns[index]?.label || key} stroke={CHART_COLORS[index % CHART_COLORS.length]} strokeWidth={2} dot={false} connectNulls /> })}</LineChart></ResponsiveContainer></div></> : <div className="chart-empty">No numeric columns were detected in this CSV.</div>}</div>
}

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return <div className="chart-tooltip"><strong>{label}</strong>{payload.map((item) => <span key={item.dataKey}><i style={{ backgroundColor: item.color }} />{item.name}: {formatValue(item.value)}</span>)}</div>
}

function TablePanel({ dataset, rows, page, pageCount, onPageChange }) {
  return <div className="table-section"><div className="subsection-heading"><div><span className="eyebrow">04 · Raw data</span><h3>Browse rows</h3></div><span className="chart-hint">Page {page + 1} of {pageCount}</span></div><div className="table-scroll"><table><thead><tr>{dataset.columns.map((column) => <th key={column.key}>{column.label}</th>)}</tr></thead><tbody>{rows.map((row, rowIndex) => <tr key={`${page}-${rowIndex}`}>{dataset.columns.map((column) => <td key={column.key} className={column.type === 'number' ? 'number-cell' : ''}>{formatValue(row[column.key])}</td>)}</tr>)}</tbody></table></div><div className="pagination"><span>{dataset.row_count.toLocaleString()} rows total</span><div><button onClick={() => onPageChange(Math.max(0, page - 1))} disabled={page === 0} aria-label="Previous page"><ChevronLeft size={16} /></button><button onClick={() => onPageChange(Math.min(pageCount - 1, page + 1))} disabled={page >= pageCount - 1} aria-label="Next page"><ChevronRight size={16} /></button></div></div></div>
}

function formatValue(value) {
  if (value === null || value === undefined || value === '') return '—'
  if (typeof value === 'number') return value.toLocaleString(undefined, { maximumFractionDigits: 4 })
  return String(value)
}

export default App
