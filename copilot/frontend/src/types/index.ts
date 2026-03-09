export interface Broker {
  id: string;
  name: string;
  code: string;
  status: 'active' | 'pending' | 'inactive';
  accuracy_score: number;
  entry_count: number;
  exception_rate: number;
  last_file_date: string;
  schema_mapping: Record<string, string>;
  performance_trend: number[];
}

export interface Exception {
  id: string;
  broker_id: string;
  broker_name: string;
  entry_number: string;
  entry_date: string;
  line_number: number;
  part_number: string;
  hts_code: string;
  gtm_hts_code: string;
  country_of_origin: string;
  declared_value: number;
  duty_amount: number;
  validation_type: 'part_number' | 'hts_code' | 'add_cvd' | 'anomaly';
  status: 'open' | 'resolved' | 'escalated';
  audit_comments: string;
  created_at: string;
  resolved_at?: string;
  resolved_by?: string;
}

export interface Rule {
  id: string;
  name: string;
  description: string;
  rule_type: 'validation' | 'ai_discovered' | 'compliance';
  category: string;
  status: 'active' | 'pending' | 'rejected' | 'disabled';
  confidence: number;
  created_at: string;
  approved_by?: string;
  conditions: RuleCondition[];
  estimated_impact: {
    entries_affected: number;
    duty_at_risk: number;
  };
}

export interface RuleCondition {
  field: string;
  operator: 'equals' | 'contains' | 'starts_with' | 'in' | 'greater_than' | 'less_than';
  value: string | number | string[];
}

export interface KPI {
  label: string;
  value: number | string;
  change?: number;
  trend?: 'up' | 'down' | 'neutral';
  format?: 'percent' | 'currency' | 'number';
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sql?: string;
  data?: Record<string, unknown>[];
  chart?: ChartSpec;
  thinking?: string[];
}

export interface ChartSpec {
  type: 'bar' | 'line' | 'pie' | 'table';
  data: Record<string, unknown>[];
  config?: Record<string, unknown>;
}

export interface DashboardData {
  kpis: {
    pass_rate: number;
    total_exceptions: number;
    anomalies_detected: number;
    duty_at_risk: number;
  };
  recent_exceptions: Exception[];
  broker_scores: {
    broker: string;
    accuracy: number;
    volume: number;
  }[];
  pending_rules: number;
  trends: {
    date: string;
    exceptions: number;
    entries: number;
  }[];
}

export interface ApiResponse<T> {
  data: T;
  status: 'success' | 'error';
  message?: string;
}
