export interface UserProfile {
  user_id: string;
  full_name: string;
  email: string;
  employment: string;
  monthly_income: number;
  risk_preference: string;
}

export interface DashboardSummary {
  total_balance: number;
  credit_utilized: number;
  monthly_income: number;
  monthly_expenses: number;
  net_cash_flow: number;
  total_subscription_cost: number;
  potential_monthly_savings: number;
}

export interface SpendingCategory {
  category: string;
  amount: number;
  percentage: number;
}

export interface MonthlyTrend {
  month: string;
  income: number;
  expenses: number;
  net: number;
}

export interface BudgetProgress {
  category: string;
  limit: number;
  spent: number;
  remaining: number;
  percentage_used: number;
  status: 'normal' | 'warning' | 'exceeded';
}

export interface RecurringPayment {
  subscription_id: string;
  name: string;
  merchant_name: string;
  category: string;
  amount: number;
  currency: string;
  frequency: string;
  next_date: string;
  evidence_status: string;
  suggested_action?: string;
  potential_savings: number;
}

export interface TransactionItem {
  transaction_id: string;
  account_id: string;
  merchant_id?: string;
  amount: number;
  currency: string;
  type: 'income' | 'expense' | 'transfer' | 'refund' | 'fee';
  category: string;
  timestamp: string;
  description: string;
  status: 'pending' | 'completed' | 'failed' | 'refunded' | 'reversed' | 'disputed';
  payment_method: string;
  anomaly_flag: boolean;
}

export interface FinancialAlert {
  id: string;
  type: 'opportunity' | 'warning' | 'info';
  title: string;
  description: string;
}

export interface DashboardData {
  user: UserProfile;
  summary: DashboardSummary;
  spending_breakdown: SpendingCategory[];
  monthly_trends: MonthlyTrend[];
  budget_progress: BudgetProgress[];
  recurring_payments: RecurringPayment[];
  recent_transactions: TransactionItem[];
  alerts: FinancialAlert[];
  active_scenario_id: string;
}

export interface ProductItem {
  product_id: string;
  merchant_id: string;
  product_name: string;
  description: string;
  category: string;
  price: number;
  shipping_cost: number;
  total_cost: number;
  currency: string;
  availability: boolean;
  rating: number;
  review_count: number;
  delivery_days: number;
  warranty_months: number;
  specifications: Record<string, string>;
}

export interface BudgetEvaluation {
  product_id: string;
  product_name: string;
  price: number;
  shipping_cost: number;
  total_cost: number;
  category: string;
  monthly_category_limit: number;
  remaining_budget_before_purchase: number;
  remaining_budget_after_purchase: number;
  is_within_budget: boolean;
  budget_variance: number;
  recommendation: string;
}

export interface SubscriptionClassification {
  subscription_id: string;
  subscription_name: string;
  merchant: string;
  monthly_cost: number;
  annual_cost: number;
  classification: 'KEEP' | 'REDUCE' | 'REPLACE' | 'ELIMINATE' | 'INVESTIGATE' | string;
  usage_evidence: string;
  value_assessment: string;
  recommendation: string;
  explanation: string;
  confidence_score: number;
  potential_savings: number;
  unknown_information: string;
  user_confirmation_needed: boolean;
}

export interface AIResponse {
  provider: string;
  model?: string;
  status: string;
  request_status?: string;
  is_fallback?: boolean;
  fallback_reason?: string | null;
  is_subscription_audit?: boolean;
  knowledge_sufficiency?: string;
  escalated_to_ai?: boolean;
  applied_knowledge_ids?: string[];
  factual_analysis: string;
  classifications?: SubscriptionClassification[];
  estimates: Array<{ label: string; value: string }>;
  recommendations: string[];
  prioritized_actions?: string[];
  unknowns: string;
  potential_monthly_savings?: number;
  potential_annual_savings?: number;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'agent';
  text?: string;
  aiResponse?: AIResponse;
  timestamp: string;
}

export interface TestScenario {
  scenario_id: string;
  title: string;
  description: string;
  target_user_or_business_id: string;
  triggering_prompt: string;
  expected_calculation_results: Record<string, any>;
  expected_findings: string[];
  expected_warnings: string[];
  validation_rules: string[];
}

// Income Intelligence Types
export interface ExpectedIncomeStream {
  stream_id: string;
  source: string;
  type: string;
  status: 'EXPECTED' | 'ESTIMATED';
  expected_date?: string;
  projected_window?: string;
  amount: number;
  confidence_score: number;
  notes: string;
}

export interface CashFlowForecast {
  period: string;
  current_liquid_cash: number;
  received_cash: number;
  expected_inflows: number;
  estimated_variable: number;
  projected_fixed_outflows: number;
  projected_end_cash: number;
  runway_months: number;
}

export interface IncomeIntelligenceData {
  user_id: string;
  employment_type: string;
  income_summary: {
    received_income: number;
    expected_income: number;
    estimated_income: number;
    total_projected_inflow: number;
    is_money_in_hand_verified: boolean;
  };
  stability_analysis: {
    volatility_percentage: number;
    stability_rating: string;
    frequency: string;
    irregular_income_detected: boolean;
    notes: string;
  };
  source_breakdown: Array<{
    stream: string;
    amount: number;
    percentage: number;
  }>;
  expected_streams: ExpectedIncomeStream[];
  estimated_streams: ExpectedIncomeStream[];
  cash_flow_forecast: CashFlowForecast[];
  rule: string;
}

// Connected Accounts & Open Banking Types
export interface ConnectedAccountItem {
  id: string;
  user_id: string;
  institution_id: string;
  institution_name: string;
  provider_type: string;
  account_mask: string;
  account_type: string;
  connection_status: 'connected' | 'syncing' | 'action_required' | 'revoked';
  health_status: 'healthy' | 'degraded' | 'disconnected';
  last_sync: string;
  sync_frequency: string;
  permissions: string;
  is_synthetic: boolean;
}

export interface InstitutionItem {
  id: string;
  name: string;
  provider_type: string;
  icon: string;
  description: string;
}

// =========================================================================
// FINANCIAL FORMULAS & ALGORITHMS TYPES
// =========================================================================

export interface InputVariableSpec {
  name: string;
  type: string;
  unit: string;
  description: string;
  default?: any;
  min_value?: number;
  max_value?: number;
}

export interface FormulaEntry {
  unique_id: string;
  name: string;
  domain: string;
  description: string;
  equation_or_def: string;
  required_inputs: InputVariableSpec[];
  optional_inputs: InputVariableSpec[];
  expected_output: string;
  currency_requirements: string;
  time_period_requirements: string;
  preconditions: string[];
  validation_rules: string[];
  assumptions: string[];
  limitations: string[];
  jurisdiction: string;
  status: 'EXECUTABLE_TESTED' | 'EXECUTABLE_UNTESTED' | 'REFERENCE_ONLY' | 'REQUIRES_EXTERNAL_DATA' | 'NOT_IMPLEMENTED';
  test_coverage_status: string;
  knowledge_source: string;
  related_formulas: string[];
}

export interface CalculationResult {
  formula_id: string;
  formula_name: string;
  result: any;
  result_formatted: string;
  output_units: string;
  inputs: Record<string, any>;
  explanation: string;
  assumptions: string[];
  warnings: string[];
  missing_information?: string;
  data_source: string;
  confidence_score: number;
  is_exact: boolean;
}

export interface FormulaSummary {
  total_registered_formulas: number;
  executable_count: number;
  domain_breakdown: Record<string, number>;
  status_breakdown: Record<string, number>;
}

export interface CompositionRecipe {
  recipe_id: string;
  name: string;
  description: string;
  domains: string[];
}

export interface CompositionWorkflowResult {
  recipe_id: string;
  recipe_name: string;
  decision_verdict: string;
  summary_explanation: string;
  step_results: Record<string, any>;
  metrics: Record<string, any>;
  recommendations: string[];
  warnings: string[];
  confidence_score: number;
}

// =========================================================================
// AUTOMATION & FINANCIAL ACTION SAFETY TYPES
// =========================================================================

export type ActionSafetyLevel = 'LEVEL_1_READ_ONLY' | 'LEVEL_2_PREPARED' | 'LEVEL_3_USER_APPROVED' | 'LEVEL_4_RESTRICTED';
export type ActionStatus = 'PENDING_APPROVAL' | 'APPROVED' | 'EXECUTED' | 'REJECTED' | 'EXPIRED';

export interface PreparedAction {
  action_id: string;
  safety_level: ActionSafetyLevel;
  title: string;
  description: string;
  action_type: string;
  target_merchant_or_payee: string;
  amount: number;
  currency: string;
  payload: Record<string, any>;
  status: ActionStatus;
  created_at: string;
  expires_at: string;
  approved_at?: string;
  executed_at?: string;
  idempotency_key: string;
  audit_notes: string[];
}

export interface AutomationRule {
  rule_id: string;
  name: string;
  description: string;
  category: 'INCOME' | 'EXPENSE' | 'SUBSCRIPTION' | 'SAVINGS' | 'DEBT' | 'SHOPPING' | 'PROTECTION' | 'FORECASTING';
  trigger_type: string;
  conditions: Array<{ field: string; operator: string; target_value: any }>;
  action_type: string;
  safety_level: ActionSafetyLevel;
  is_enabled: boolean;
  requires_user_approval: boolean;
  schedule_interval_minutes?: number;
  execution_count: number;
  last_executed?: string;
  next_scheduled?: string;
}

export interface ExecutionLog {
  log_id: string;
  rule_id: string;
  rule_name: string;
  category: string;
  event_trigger: string;
  execution_timestamp: string;
  status: string;
  details: string;
  prepared_action_id?: string;
  metrics_snapshot: Record<string, any>;
}

export interface OptimizationOpportunity {
  opportunity_id: string;
  category: string;
  title: string;
  target_item_or_service: string;
  current_cost_monthly: number;
  current_cost_annual: number;
  proposed_cost_monthly: number;
  proposed_cost_annual: number;
  potential_gross_savings_annual: number;
  switching_or_setup_cost: number;
  first_year_net_savings: number;
  break_even_months: number;
  financial_risk_score: string;
  liquidity_impact: string;
  evidence_quality: string;
  rank_score: number;
  recommendation_summary: string;
  assumptions: string[];
  action_type: string;
  requires_user_approval: boolean;
}

