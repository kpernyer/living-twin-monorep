/**
 * Living Twin - Consistent Schema Types for React/TypeScript
 *
 * These types ensure consistency with Neo4j, Firestore, and Pub/Sub schemas
 */

// =========================
// Storage Keys
// =========================
export const STORAGE_KEYS = {
  TENANT_DATA: 'tenant_data',
  USER_DATA: 'user_data',
  TEAM_DATA: 'team_data',
  GOAL_DATA: 'goal_data',
  DOCUMENT_DATA: 'document_data',
  CHUNK_DATA: 'chunk_data',
  OFFLINE_QUEUE: 'offline_queue',
  AUTH_TOKEN: 'auth_token',
  LAST_SYNC: 'last_sync',
} as const

// =========================
// Base Types
// =========================
export type EntityStatus = 'active' | 'inactive' | 'archived' | 'suspended'
export type UserRole = 'admin' | 'member' | 'viewer'
export type GoalStatus = 'draft' | 'active' | 'completed' | 'archived'
export type GoalPriority = 'low' | 'medium' | 'high' | 'critical'
export type ProcessingStatus = 'pending' | 'processing' | 'completed' | 'failed'
export type TenantStatus = 'active' | 'suspended' | 'trial'

// =========================
// Core Entity Interfaces
// =========================

export interface BaseEntity {
  id: string
  tenant_id: string
  created_at: string // ISO 8601 timestamp
  updated_at: string // ISO 8601 timestamp
  created_by?: string
  status: string
  metadata?: Record<string, any>
}

export interface TenantSettings {
  embedding_model: 'sentence-transformers' | 'openai'
  max_chunk_size: number
  chunk_overlap: number
  allowed_file_types: string[]
  max_file_size_mb: number
  retention_days: number
}

export interface TenantData extends Omit<BaseEntity, 'tenant_id'> {
  display_name: string
  domain: string
  settings: TenantSettings
  status: TenantStatus
  subscription_tier?: 'free' | 'pro' | 'enterprise'
  billing_email?: string
}

export interface UserData extends BaseEntity {
  email: string
  display_name: string
  role: UserRole
  firebase_uid: string
  last_login?: string
  avatar_url?: string
  preferences?: {
    theme: 'light' | 'dark' | 'auto'
    notifications: boolean
    language: string
  }
}

export interface TeamData extends BaseEntity {
  display_name: string
  description?: string
  color?: string
  member_count?: number
  settings?: {
    visibility: 'public' | 'private'
    auto_assign_goals: boolean
  }
}

export interface GoalData extends BaseEntity {
  title: string
  description?: string
  status: GoalStatus
  priority: GoalPriority
  due_date?: string
  completion_date?: string
  progress_percentage?: number
  tags?: string[]
  team_id?: string
  parent_goal_id?: string
}

export interface DocumentData extends BaseEntity {
  title: string
  file_name: string
  file_type: string
  file_size: number
  gcs_path?: string
  page_count?: number
  chunk_count?: number
  processing_status: ProcessingStatus
  processing_error?: string
  tags?: string[]
  related_goal_ids?: string[]
}

export interface ChunkData extends BaseEntity {
  document_id: string
  content: string
  position: number
  page_number?: number
  start_char: number
  end_char: number
  token_count: number
  similarity_score?: number // For search results
}

// =========================
// API Request/Response Types
// =========================

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
  timestamp: string
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number
    limit: number
    total: number
    has_next: boolean
    has_prev: boolean
  }
}

export interface SearchRequest {
  query: string
  tenant_id: string
  filters?: {
    document_types?: string[]
    date_range?: {
      start: string
      end: string
    }
    goal_ids?: string[]
    tags?: string[]
  }
  limit?: number
  offset?: number
}

export interface SearchResult {
  chunk: ChunkData
  document: DocumentData
  similarity_score: number
  highlighted_content?: string
}

export interface SearchResponse extends ApiResponse<SearchResult[]> {
  query: string
  total_results: number
  processing_time_ms: number
}

// =========================
// Pub/Sub Message Types
// =========================

export interface PubSubMessage<T = any> {
  event_type: string
  tenant_id: string
  entity_id?: string
  timestamp: string
  correlation_id: string
  data: T
  metadata: {
    source: 'api' | 'worker' | 'scheduler'
    version: string
    user_id?: string
  }
}

export interface TenantEvent extends PubSubMessage<Partial<TenantData>> {
  event_type: 'tenant.created' | 'tenant.updated' | 'tenant.deleted' | 'tenant.suspended'
}

export interface UserEvent extends PubSubMessage<Partial<UserData>> {
  event_type: 'user.created' | 'user.login' | 'user.role_changed' | 'user.deleted'
}

export interface GoalEvent
  extends PubSubMessage<Partial<GoalData> & { old_status?: GoalStatus; new_status?: GoalStatus }> {
  event_type:
    | 'goal.created'
    | 'goal.updated'
    | 'goal.status_changed'
    | 'goal.completed'
    | 'goal.deleted'
}

export interface DocumentEvent
  extends PubSubMessage<Partial<DocumentData> & { processing_duration_ms?: number }> {
  event_type:
    | 'document.uploaded'
    | 'document.processing_started'
    | 'document.processing_completed'
    | 'document.processing_failed'
    | 'document.deleted'
}

// =========================
// Form Types
// =========================

export interface CreateTenantForm {
  display_name: string
  domain: string
  billing_email: string
  subscription_tier: 'free' | 'pro' | 'enterprise'
}

export interface CreateUserForm {
  email: string
  display_name: string
  role: UserRole
  send_invite: boolean
}

export interface CreateGoalForm {
  title: string
  description?: string
  priority: GoalPriority
  due_date?: string
  team_id?: string
  parent_goal_id?: string
  tags?: string[]
}

export interface UploadDocumentForm {
  file: File
  title?: string
  tags?: string[]
  related_goal_ids?: string[]
}

// =========================
// UI State Types
// =========================

export interface LoadingState {
  isLoading: boolean
  error?: string
  lastUpdated?: string
}

export interface AuthState {
  user: UserData | null
  tenant: TenantData | null
  isAuthenticated: boolean
  isLoading: boolean
  error?: string
}

export interface AppState {
  auth: AuthState
  ui: {
    theme: 'light' | 'dark' | 'auto'
    sidebarCollapsed: boolean
    notifications: PubSubMessage[]
  }
  data: {
    goals: GoalData[]
    documents: DocumentData[]
    teams: TeamData[]
    users: UserData[]
  }
  loading: {
    goals: LoadingState
    documents: LoadingState
    teams: LoadingState
    users: LoadingState
  }
}

// =========================
// Validation Schemas
// =========================

export const ID_PATTERNS = {
  TENANT: /^tenant-[a-z0-9]{6,12}$/,
  USER: /^user-[a-z0-9]{6,12}$/,
  TEAM: /^team-[a-z0-9]{6,12}$/,
  GOAL: /^goal-[a-z0-9-]{6,50}$/,
  DOCUMENT: /^doc-[a-z0-9-]{6,50}$/,
  CHUNK: /^chunk-[a-z0-9-]{6,50}$/,
} as const

export const VALIDATION_RULES = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  DOMAIN: /^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$/,
  DISPLAY_NAME: {
    MIN_LENGTH: 2,
    MAX_LENGTH: 100,
  },
  DESCRIPTION: {
    MAX_LENGTH: 1000,
  },
  FILE_SIZE: {
    MAX_MB: 100,
  },
} as const

// =========================
// Utility Types
// =========================

export type EntityType = 'tenant' | 'user' | 'team' | 'goal' | 'document' | 'chunk'

export type CreateEntityRequest<T> = Omit<T, 'id' | 'created_at' | 'updated_at'>
export type UpdateEntityRequest<T> = Partial<Omit<T, 'id' | 'tenant_id' | 'created_at'>> & {
  updated_at: string
}

// Helper type for API endpoints
export type ApiEndpoint =
  | '/auth/login'
  | '/auth/logout'
  | '/auth/whoami'
  | '/auth/invite'
  | '/tenants'
  | '/users'
  | '/teams'
  | '/goals'
  | '/documents'
  | '/search'
  | '/ingest/file'
  | '/ingest/status'
