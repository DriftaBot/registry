<template>
  <div class="status-page">

    <!-- Search -->
    <div class="sp-search-wrap">
      <input
        v-model="query"
        class="sp-search"
        placeholder="Search providers…"
        aria-label="Search"
      />
      <span v-if="query" class="sp-clear" @click="query = ''" title="Clear">✕</span>
    </div>

    <!-- ── Providers ──────────────────────────────────────────── -->
    <section class="sp-section">
      <h2 class="sp-section-title">
        Providers
        <span class="sp-count-title">{{ filteredProviders.length }}</span>
        <span v-if="driftCount" class="sp-drift-count" @click="toggleDriftFilter">
          {{ driftFilter ? 'show all' : `${driftCount} drifts` }}
        </span>
      </h2>
      <div v-if="filteredProviders.length" class="sp-provider-grid">
        <div v-for="p in filteredProviders" :key="p.name" class="sp-provider-wrap">
          <div class="sp-provider-card" @click="openModal(p)">
            <span class="sp-provider-name">{{ p.displayName }}</span>
            <span class="sp-badges">
              <span :class="['sp-badge', 'sp-badge--' + p.specType]">{{ p.specType }}</span>
              <span v-if="p.drift" class="sp-badge sp-badge--drift" @click.stop="toggleDrift(p.name)">drift</span>
            </span>
          </div>
          <div v-if="p.drift && expandedDrifts.has(p.name)" class="sp-drift-detail" v-html="renderMarkdown(p.drift)"></div>
        </div>
      </div>
      <p v-else class="sp-empty">No providers match your search.</p>
    </section>

    <!-- ── Spec Modal ─────────────────────────────────────────── -->
    <Teleport to="body">
      <div v-if="modalProvider" class="sp-modal-overlay" @click.self="closeModal">
        <div class="sp-modal">
          <div class="sp-modal-header">
            <span class="sp-modal-title">{{ modalProvider.displayName }}</span>
            <span class="sp-modal-file">{{ modalProvider.specFile }}</span>
            <span class="sp-modal-actions">
              <a v-if="modalProvider.githubUrl" :href="modalProvider.githubUrl" target="_blank" rel="noopener" class="sp-modal-github" title="View on GitHub">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
              </a>
              <button class="sp-modal-copy" @click="copySpec" :title="copied ? 'Copied!' : 'Copy to clipboard'">
                <svg v-if="!copied" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
                <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              </button>
              <button class="sp-modal-close" @click="closeModal" title="Close">✕</button>
            </span>
          </div>
          <div class="sp-modal-body">
            <pre class="sp-modal-code"><code>{{ modalProvider.specContent ?? 'No spec file found.' }}</code></pre>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import type { Provider, StatusData } from '../../status.data'

const props = defineProps<{ data: StatusData }>()

const query = ref('')
const driftFilter = ref(false)
const expandedDrifts = reactive(new Set<string>())
const modalProvider = ref<Provider | null>(null)
const copied = ref(false)

const q = computed(() => query.value.trim().toLowerCase())

const driftCount = computed(() => props.data.providers.filter(p => p.drift).length)

const filteredProviders = computed(() => {
  let list = props.data.providers
  if (driftFilter.value) list = list.filter(p => p.drift)
  if (q.value) {
    list = list.filter(p =>
      p.name.toLowerCase().includes(q.value) ||
      p.specType.toLowerCase().includes(q.value) ||
      (q.value === 'drift' && p.drift)
    )
  }
  return list
})

function toggleDriftFilter() { driftFilter.value = !driftFilter.value }
function toggleDrift(name: string) {
  expandedDrifts.has(name) ? expandedDrifts.delete(name) : expandedDrifts.add(name)
}

function openModal(p: Provider) {
  modalProvider.value = p
  copied.value = false
  document.body.style.overflow = 'hidden'
}

function closeModal() {
  modalProvider.value = null
  document.body.style.overflow = ''
}

function copySpec() {
  if (!modalProvider.value?.specContent) return
  navigator.clipboard.writeText(modalProvider.value.specContent).then(() => {
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  })
}

// Close modal on Escape
watch(modalProvider, (v) => {
  const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') closeModal() }
  if (v) window.addEventListener('keydown', handler)
  else window.removeEventListener('keydown', handler)
})

function renderMarkdown(md: string): string {
  return md
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/^### (.+)$/gm, '<h4>$1</h4>')
    .replace(/^## (.+)$/gm, '<h3>$1</h3>')
    .replace(/^# (.+)$/gm, '<h2>$1</h2>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
    .replace(/\n{2,}/g, '<br/><br/>')
    .replace(/\n/g, '<br/>')
}
</script>

<style scoped>
.status-page {
  margin-top: 1.5rem;
}

/* ── Search ─────────────────────────────────────────────────── */
.sp-search-wrap {
  position: relative;
  margin-bottom: 1.25rem;
}
.sp-search {
  width: 100%;
  padding: 0.55rem 2.2rem 0.55rem 0.85rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}
.sp-search:focus {
  border-color: var(--vp-c-brand-1);
}
.sp-clear {
  position: absolute;
  right: 0.7rem;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: var(--vp-c-text-3);
  font-size: 0.8rem;
  user-select: none;
}
.sp-clear:hover { color: var(--vp-c-text-1); }

/* ── Section ─────────────────────────────────────────────────── */
.sp-section { margin-bottom: 2.5rem; }
.sp-section-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--vp-c-text-1);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border: none;
  padding: 0;
}
.sp-count-title {
  font-size: 0.78rem;
  background: var(--vp-c-bg-mute);
  padding: 0.1rem 0.45rem;
  border-radius: 10px;
  color: var(--vp-c-text-2);
  font-weight: 400;
}
.sp-empty {
  color: var(--vp-c-text-3);
  font-size: 0.9rem;
}

/* ── Drift filter toggle ────────────────────────────────────── */
.sp-drift-count {
  font-size: 0.72rem;
  background: #fff7ed;
  color: #c2410c;
  padding: 0.1rem 0.5rem;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 500;
  user-select: none;
  transition: background 0.2s;
}
.sp-drift-count:hover { background: #fed7aa; }
.dark .sp-drift-count { background: #431407; color: #fdba74; }
.dark .sp-drift-count:hover { background: #7c2d12; }

/* ── Provider grid ───────────────────────────────────────────── */
.sp-provider-wrap { display: contents; }
.sp-provider-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 0.6rem;
}
.sp-provider-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  background: var(--vp-c-bg-soft);
  gap: 0.5rem;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}
.sp-provider-card:hover {
  border-color: var(--vp-c-brand-1);
  background: var(--vp-c-bg-elv);
}
.sp-provider-name {
  font-size: 0.85rem;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ── Badges ──────────────────────────────────────────────────── */
.sp-badges {
  display: flex;
  gap: 0.3rem;
  flex-shrink: 0;
}
.sp-badge {
  font-size: 0.7rem;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
}
.sp-badge--openapi { background: #dbeafe; color: #1d4ed8; }
.sp-badge--graphql { background: #fce7f3; color: #be185d; }
.sp-badge--grpc    { background: #dcfce7; color: #15803d; }
.sp-badge--drift   { background: #fff7ed; color: #c2410c; cursor: pointer; }
.sp-badge--drift:hover { background: #fed7aa; }

/* ── Drift detail panel ─────────────────────────────────────── */
.sp-drift-detail {
  grid-column: 1 / -1;
  padding: 0.75rem 1rem;
  border: 1px solid #fed7aa;
  border-radius: 8px;
  background: #fffbeb;
  font-size: 0.82rem;
  line-height: 1.5;
  color: var(--vp-c-text-1);
  overflow-x: auto;
}
.sp-drift-detail code {
  background: var(--vp-c-bg-mute);
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
  font-size: 0.78rem;
}

/* ── Modal ───────────────────────────────────────────────────── */
.sp-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 999;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}
.sp-modal {
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  width: 100%;
  max-width: 900px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}
.sp-modal-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--vp-c-divider);
  flex-shrink: 0;
}
.sp-modal-title {
  font-weight: 600;
  font-size: 1rem;
  color: var(--vp-c-text-1);
}
.sp-modal-file {
  font-size: 0.78rem;
  color: var(--vp-c-text-3);
  font-family: var(--vp-font-family-mono);
}
.sp-modal-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.sp-modal-github {
  color: var(--vp-c-text-2);
  display: flex;
  transition: color 0.2s;
}
.sp-modal-github:hover { color: var(--vp-c-text-1); }
.sp-modal-copy {
  background: none;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  padding: 0.3rem 0.4rem;
  cursor: pointer;
  color: var(--vp-c-text-2);
  display: flex;
  align-items: center;
  transition: color 0.2s, border-color 0.2s;
}
.sp-modal-copy:hover {
  color: var(--vp-c-brand-1);
  border-color: var(--vp-c-brand-1);
}
.sp-modal-close {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--vp-c-text-3);
  font-size: 1rem;
  padding: 0.2rem 0.4rem;
  line-height: 1;
}
.sp-modal-close:hover { color: var(--vp-c-text-1); }
.sp-modal-body {
  overflow: auto;
  padding: 0;
}
.sp-modal-code {
  margin: 0;
  padding: 1rem;
  font-size: 0.78rem;
  line-height: 1.6;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  white-space: pre;
  overflow-x: auto;
  border-radius: 0 0 12px 12px;
}

/* ── Dark mode overrides ─────────────────────────────────────── */
.dark .sp-badge--openapi { background: #1e3a5f; color: #93c5fd; }
.dark .sp-badge--graphql { background: #500724; color: #f9a8d4; }
.dark .sp-badge--grpc    { background: #14532d; color: #86efac; }
.dark .sp-badge--drift   { background: #431407; color: #fdba74; }
.dark .sp-badge--drift:hover { background: #7c2d12; }
.dark .sp-drift-detail   { background: #1c1007; border-color: #7c2d12; }
</style>
