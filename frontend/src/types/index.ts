export type FunnelStage = 'awareness' | 'consideration' | 'decision'
export type Channel     = 'linkedin' | 'instagram' | 'meta_ads'
export type JobStatus   = 'queued' | 'running' | 'stitching' | 'publishing' | 'completed' | 'failed'

export interface ManualScene {
  order:            number
  narration?:       string
  veo_prompt:       string
  duration_seconds?: number
}

export interface ManualScript {
  video_title: string
  scenes:      ManualScene[]
  cta?:        string
}

export interface LeadPayload {
  name:    string
  company: string

  // Required only when use_claude=true
  industry?:    string
  pain_point?:  string
  funnel_stage: FunnelStage

  // Script step
  use_claude:    boolean
  manual_script?: ManualScript

  // Publish step — empty = skip publishing
  target_channel: Channel[]
}

export interface Scene {
  order:            number
  narration:        string
  veo_prompt:       string
  duration_seconds: number
}

export interface VideoScript {
  video_title: string
  scenes:      Scene[]
  cta:         string
}

export interface PipelineJob {
  job_id:          string
  status:          JobStatus
  lead_name:       string
  lead_company:    string | null
  script:          VideoScript | null
  clips:           string[] | null
  final_video_url: string | null
  error_message:   string | null
  created_at:      string | null
  completed_at:    string | null
}

export interface JobSummary {
  job_id:       string
  status:       JobStatus
  lead_name:    string
  lead_company: string | null
  created_at:   string | null
  completed_at: string | null
}

export interface WebhookResponse {
  job_id: string
  status: 'queued'
}
