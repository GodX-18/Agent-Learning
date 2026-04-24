export type CourseTemplate = "standard" | "compact" | "detailed"

export interface Section {
  id: string
  title: string
  goals: string[]
}

export interface Chapter {
  id: string
  title: string
  summary: string
  sections: Section[]
}

export interface CourseOutline {
  title: string
  audience: string
  prerequisites: string[]
  learning_outcomes: string[]
  chapters: Chapter[]
}

export interface CourseTemplateOption {
  id: CourseTemplate
  name: string
  description: string
}

export interface CourseTreeNode {
  name: string
  type: "file" | "directory"
  path: string
  children?: CourseTreeNode[]
}

export interface CourseResult {
  task_id: string
  status: string
  meta: Record<string, unknown>
  outline: CourseOutline
  tree: CourseTreeNode[]
  markdown_files: Record<string, string>
}

export interface CourseHistoryItem {
  taskId: string
  title: string
  topic: string
  createdAt: string
}
