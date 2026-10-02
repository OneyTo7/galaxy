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

export interface DiagnoseOut {
  submission_id: number
  misconception_type: string
  evidence: string
  knowledge_point: string
  confidence: number
}

export interface VariantOut {
  id: number
  submission_id: number
  title: string
  description: string
  cases: { input: string; expected_output: string }[]
  scoring_points: string[]
  lang: string
}

export interface AssignmentOut {
  id: number
  teacher_id: number
  course_id: number | null
  title: string
  description: string
  lang: string
  scoring_rubric: string
  reference_code: string
  status: string
  created_at: string
  test_cases: {
    id: number
    assignment_id: number
    name: string
    input: string
    expected_output: string
    is_hidden: boolean
    weight: number
    order: number
  }[]
}

export interface AppealOut {
  id: number
  submission_id: number
  student_id: number
  reason: string
  status: string
  approved: boolean | null
  review_comment: string
  reviewer_id: number | null
  new_score: number | null
  created_at: string
  reviewed_at: string | null
}

export interface CheatingReportOut {
  id: number
  submission_id: number
  student_id: number
  check_type: string
  score: number
  detail: string
  status: string
  created_at: string
}

export interface GradeOut {
  id: number
  assignment_id: number
  student_id: number
  final_score: number
  status: string
  note: string
  created_at: string
  updated_at: string
}
