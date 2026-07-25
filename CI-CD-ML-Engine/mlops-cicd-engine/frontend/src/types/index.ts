export type RunStatus = "queued" | "running" | "success" | "failed";
export type ModelSource = "local" | "huggingface";

export interface ModelMetric {
  id: string;
  precision: number;
  recall: number;
  f1_score: number;
  baseline_precision: number | null;
  beat_baseline: boolean;
  epoch_count: number;
}

export interface PipelineRun {
  id: string;
  repo: string;
  branch: string;
  commit_hash: string;
  commit_message: string;
  triggered_path: string;
  status: RunStatus;
  started_at: string;
  finished_at: string | null;
  duration_seconds: number | null;
  error_message: string | null;
  metrics: ModelMetric[];
}

export interface RegisteredModel {
  id: string;
  name: string;
  source: ModelSource;
  architecture_or_hf_id: string;
  version: string;
  commit_hash: string | null;
  top_precision: number;
  is_active: boolean;
  created_at: string;
}
