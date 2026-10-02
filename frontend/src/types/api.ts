export interface CaseResult {
  case_id: number
  passed: boolean
  stdout: string
  stderr: string
  timed_out: boolean
  elapsed_ms: number
}

export interface EvaluationOut {
  submission_id: number
  assignment_id: number
  score: number
  status: string
  results: CaseResult[]
}

export interface MisconceptionStat {
  misconception_type: string
  count: number
}

export interface KnowledgeStat {
  knowledge_point: string
  count: number
}

export interface StudentStat {
  user_id: number
  score: number
  misconception_type: string
}

export interface LearningReport {
  assignment_id: number
  submission_count: number
  avg_score: number
  misconception_stats: MisconceptionStat[]
  knowledge_stats: KnowledgeStat[]
  students: StudentStat[]
}
