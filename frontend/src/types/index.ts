// 用户相关类型
export interface User {
  id: string;
  email?: string;
  phone?: string;
  full_name?: string;
  role: 'admin' | 'job_seeker' | 'company';
  is_active: boolean;
  created_at?: string;
}

// 职位相关类型
export interface Job {
  job_id: string;
  title: string;
  company_name: string;
  location: string;
  job_type?: string;
  salary_range?: string;
  content?: string;
  requirements?: string[];
  applicants?: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

// 简历相关类型
export interface Resume {
  resume_id: string;
  user_id: string;
  title: string;
  file_name: string;
  file_path: string;
  content?: string;
  skills?: string[];
  education?: string;
  experience?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

// 匹配相关类型
export interface Match {
  match_id: string;
  job_id: string;
  resume_id: string;
  score: number;
  details?: {
    [key: string]: number;
  };
  created_at: string;
}

// API响应类型
export interface ApiResponse<T> {
  status: 'success' | 'error';
  data?: T;
  message?: string;
}

// 分页类型
export interface Pagination<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// 数字员工类型
export interface DigitalEmployee {
  id: string;
  name: string;
  type: string;
  description: string;
  capabilities: string[];
  views: number;
  likes: number;
  icon?: string;
  is_active: boolean;
}

// 匹配详情类型
export interface MatchDetails {
  skill_score: number;
  context_score: number;
  matched_skills: string[];
}

// 职位推荐类型
export interface JobRecommendation {
  job_id: string;
  title: string;
  company_name: string;
  location: string;
  job_type: string;
  salary_range?: string;
  match_score: number;
  match_details: MatchDetails;
}

// 简历推荐类型
export interface ResumeRecommendation {
  resume_id: string;
  user_id: string;
  user_name: string;
  skills?: string[];
  match_score: number;
  match_details: MatchDetails;
} 