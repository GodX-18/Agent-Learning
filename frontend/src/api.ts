const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface Document {
  doc_id: string
  filename: string
}

export interface DocumentPreview extends Document {
  file_type?: string
  content: string
}

export interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp?: number
}

// ── 文档接口 ─────────────────────────────────────────────────────────────────

export async function uploadDocument(file: File): Promise<{ doc_id: string; filename: string; chunks: number }> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE_URL}/documents/upload`, { method: 'POST', body: form })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || '上传失败')
  }
  return res.json()
}

export async function fetchDocuments(): Promise<Document[]> {
  const res = await fetch(`${BASE_URL}/documents`)
  if (!res.ok) throw new Error('获取文档列表失败')
  const data = await res.json()
  return data.documents
}

export async function deleteDocument(docId: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/documents/${docId}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('删除失败')
}

export async function fetchDocumentPreview(docId: string): Promise<DocumentPreview> {
  const res = await fetch(`${BASE_URL}/documents/${docId}/preview`)
  if (!res.ok) {
    const err = await res.json().catch(() => null)
    throw new Error(err?.detail || '获取文档预览失败')
  }
  return res.json()
}

export function getDocumentFileUrl(docId: string): string {
  return `${BASE_URL}/documents/${docId}/file`
}

// ── 对话接口 ─────────────────────────────────────────────────────────────────

export async function* streamChat(
  message: string,
  sessionId: string,
): AsyncGenerator<{ chunk?: string; done?: boolean; error?: string; session_id?: string }> {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId, stream: true }),
  })

  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || '请求失败')
  }

  const reader = res.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const json = line.slice(6).trim()
        if (!json) continue
        try {
          yield JSON.parse(json)
        } catch {
          // ignore
        }
      }
    }
  }
}

export async function clearSession(sessionId: string): Promise<void> {
  await fetch(`${BASE_URL}/sessions/${sessionId}`, { method: 'DELETE' })
}

export async function healthCheck(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE_URL}/health`)
    return res.ok
  } catch {
    return false
  }
}
