import axios from 'axios'
import type { LeadPayload, WebhookResponse, PipelineJob } from '../types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15_000,
})

export async function submitLead(payload: LeadPayload): Promise<WebhookResponse> {
  const { data } = await api.post<WebhookResponse>('/webhook/lead', payload)
  return data
}

export async function getJob(jobId: string): Promise<PipelineJob> {
  const { data } = await api.get<PipelineJob>(`/jobs/${jobId}`)
  return data
}

export async function checkHealth(): Promise<{ status: string }> {
  const { data } = await api.get<{ status: string }>('/health')
  return data
}
