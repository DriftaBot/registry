import { readdirSync, readFileSync, existsSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const ROOT = join(__dirname, '..')   // registry root

export interface Provider {
  name: string
  displayName: string
  specType: string
  githubUrl: string | null
  repoSlug: string | null
  drift: string | null
}

export interface StatusData {
  providers: Provider[]
}

/**
 * Parse provider.companies.yaml line-by-line to extract name → githubUrl and displayName.
 * Reads the first `repo:` entry under each company's `specs:` block.
 */
function loadProviderMeta(): Map<string, { displayName: string; githubUrl: string; repoSlug: string }> {
  const yamlPath = join(ROOT, 'provider.companies.yaml')
  if (!existsSync(yamlPath)) return new Map()

  const map = new Map<string, { displayName: string; githubUrl: string; repoSlug: string }>()
  let name = ''
  let displayName = ''
  let inSpecs = false

  for (const raw of readFileSync(yamlPath, 'utf-8').split('\n')) {
    const line = raw.trimEnd()
    const nameMatch = line.match(/^ {2}- name:\s+(.+)/)
    if (nameMatch) { name = nameMatch[1].trim(); displayName = ''; inSpecs = false; continue }

    const dnMatch = line.match(/^ {4}display_name:\s+(.+)/)
    if (dnMatch && name) { displayName = dnMatch[1].trim(); continue }

    if (/^ {4}specs:/.test(line)) { inSpecs = true; continue }

    if (inSpecs && name && !map.has(name)) {
      const repoMatch = line.match(/repo:\s+(.+)/)
      if (repoMatch) {
        const repoSlug = repoMatch[1].trim()
        map.set(name, {
          displayName: displayName || name,
          githubUrl: `https://github.com/${repoSlug}`,
          repoSlug,
        })
        inSpecs = false
      }
    }
  }
  return map
}

function loadDrifts(): Map<string, string> {
  const driftsDir = join(ROOT, 'drifts')
  if (!existsSync(driftsDir)) return new Map()

  const map = new Map<string, string>()
  for (const org of readdirSync(driftsDir, { withFileTypes: true })) {
    if (!org.isDirectory()) continue
    const orgDir = join(driftsDir, org.name)
    for (const repo of readdirSync(orgDir, { withFileTypes: true })) {
      if (!repo.isDirectory()) continue
      const resultPath = join(orgDir, repo.name, 'result.md')
      if (existsSync(resultPath)) {
        const content = readFileSync(resultPath, 'utf-8').trim()
        if (content) map.set(`${org.name}/${repo.name}`, content)
      }
    }
  }
  return map
}

export default {
  load(): StatusData {
    const meta        = loadProviderMeta()
    const drifts      = loadDrifts()
    const providersDir = join(ROOT, 'companies/providers')
    const providers: Provider[] = []
    if (existsSync(providersDir)) {
      for (const entry of readdirSync(providersDir, { withFileTypes: true })) {
        if (!entry.isDirectory()) continue
        const sub      = readdirSync(join(providersDir, entry.name), { withFileTypes: true })
        const specType = sub.find(e => e.isDirectory())?.name ?? 'openapi'
        const m        = meta.get(entry.name)
        const repoSlug = m?.repoSlug ?? null
        providers.push({
          name:        entry.name,
          displayName: m?.displayName ?? entry.name,
          specType,
          githubUrl:   m?.githubUrl ?? null,
          repoSlug,
          drift:       repoSlug ? (drifts.get(repoSlug) ?? null) : null,
        })
      }
    }
    providers.sort((a, b) => a.name.localeCompare(b.name))

    return { providers }
  },
}
