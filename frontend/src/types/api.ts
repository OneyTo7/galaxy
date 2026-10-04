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
  mastery_summary: MasterySummaryItem[]
  students: StudentStat[]
}

export interface MasterySummaryItem {
  knowledge_point_id: number
  code: string
  name: string
  category: string
  avg_mastery: number
  student_count: number
  at_risk_count: number
}

export interface DiagnoseOut {
  submission_id: number
  misconception_type: string
  evidence: string
  knowledge_point: string
  knowledge_point_code: string
  knowledge_point_id: number | null
  confidence: number
  evidence_validated: boolean
  status: string
}

export interface MisconceptionOut extends DiagnoseOut {
  id: number
  created_at: string
}

export interface VariantOut {
  id: number
  submission_id: number
  title: string
  description: string
  cases: { input: string; expected_output: string }[]
  scoring_points: string[]
  lang: string
  difficulty: string
  practice_assignment_id: number | null
}

export interface SubmissionOut {
  id: number
  user_id: number
  assignment_id: number
  lang: string
  status: string
  score: number
  created_at: string
}

export interface AssignmentOut {
  id: number
  teacher_id: number | null
  course_id: number | null
  title: string
  description: string
  lang: string
  scoring_rubric: string
  reference_code: string
  status: string
  kind: string
  assigned_user_id: number | null
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

export interface CheatingReportOut {
  id: number
  submission_id: number
  student_id: number
  check_type: string
  score: number
  detail: string
  meta: Record<string, unknown> | null
  status: string
  created_at: string
}

export interface KnowledgePointOut {
  id: number
  code: string
  name: string
  category: string
  sort_order: number
}

export interface KnowledgeTagOut {
  knowledge_point_id: number
  code: string
  name: string
  category: string
  weight: number
}

export interface MasteryCellOut {
  user_id: number
  knowledge_point_id: number
  code: string
  name: string
  category: string
  mastery: number | null
  attempts: number
  correct: number
  status: string
}

export interface MatrixStudentOut {
  user_id: number
  display_name: string
}

export interface MasteryMatrixOut {
  course_id: number
  students: MatrixStudentOut[]
  cells: MasteryCellOut[]
}

export interface MasteryEventOut {
  id: number
  knowledge_point_id: number
  code: string
  name: string
  source: string
  observed: boolean
  mastery_before: number
  mastery_after: number
  submission_id: number
  created_at: string
}

export interface StudentMasteryOut {
  course_id: number
  user_id: number
  points: MasteryCellOut[]
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

export interface EnrollmentOut {
  id: number
  class_id: number
  student_id: number
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
