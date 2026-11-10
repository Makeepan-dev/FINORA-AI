import {
  DashboardData, ProductItem, BudgetEvaluation, AIResponse,
  TestScenario, IncomeIntelligenceData, ConnectedAccountItem, InstitutionItem,
  FormulaEntry, CalculationResult, FormulaSummary, CompositionRecipe,
  CompositionWorkflowResult, AutomationRule, ExecutionLog, PreparedAction,
  OptimizationOpportunity
} from '../types';

const API_BASE = '/api';

export const api = {
  // Dashboard & Analytics
  async getDashboard(userId: string = 'usr_alex_chen'): Promise<DashboardData> {
    const res = await fetch(`${API_BASE}/analytics/dashboard?user_id=${userId}`);
    if (!res.ok) throw new Error('Failed to load dashboard data');
    return res.json();
  },

  // Income Intelligence
  async getIncomeIntelligence(userId: string = 'usr_alex_chen'): Promise<IncomeIntelligenceData> {
    const res = await fetch(`${API_BASE}/income/intelligence?user_id=${userId}`);
    if (!res.ok) throw new Error('Failed to load income intelligence data');
    return res.json();
  },

  // Connected Financial Accounts
  async getConnectedAccounts(userId: string = 'usr_alex_chen'): Promise<ConnectedAccountItem[]> {
    const res = await fetch(`${API_BASE}/connections/?user_id=${userId}`);
    if (!res.ok) throw new Error('Failed to load connected accounts');
    return res.json();
  },

  async getSupportedInstitutions(): Promise<InstitutionItem[]> {
    const res = await fetch(`${API_BASE}/connections/institutions`);
    if (!res.ok) throw new Error('Failed to load supported institutions');
    return res.json();
  },

  async connectAccount(institutionId: string, accountType: string = 'checking', userId: string = 'usr_alex_chen') {
    const res = await fetch(`${API_BASE}/connections/connect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ institution_id: institutionId, account_type: accountType, user_id: userId })
    });
    if (!res.ok) throw new Error('Failed to connect financial institution');
    return res.json();
  },

  async syncConnection(connectionId: string) {
    const res = await fetch(`${API_BASE}/connections/${connectionId}/sync`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to trigger synchronization');
    return res.json();
  },

  async revokeConnection(connectionId: string) {
    const res = await fetch(`${API_BASE}/connections/${connectionId}/revoke`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to revoke connection permissions');
    return res.json();
  },

  async getSyncHistory(userId: string = 'usr_alex_chen') {
    const res = await fetch(`${API_BASE}/connections/history?user_id=${userId}`);
    if (!res.ok) throw new Error('Failed to fetch sync audit logs');
    return res.json();
  },

  // Transactions
  async getTransactions(userId?: string, category?: string, limit: number = 100, offset: number = 0) {
    let url = `${API_BASE}/demo-data/transactions?limit=${limit}&offset=${offset}`;
    if (userId) url += `&user_id=${userId}`;
    if (category) url += `&category=${category}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to load transactions');
    return res.json();
  },

  // Financial Guardian Agent
  async chatWithGuardian(prompt: string, userId: string = 'usr_alex_chen'): Promise<{
    prompt: string;
    ai_response: AIResponse;
    metrics_snapshot: any;
  }> {
    const res = await fetch(`${API_BASE}/guardian/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, user_id: userId })
    });
    if (!res.ok) throw new Error('Failed to receive Guardian response');
    return res.json();
  },

  // Shopping Agent
  async searchProducts(query?: string, category?: string, maxPrice?: number): Promise<ProductItem[]> {
    let url = `${API_BASE}/shopping/products?`;
    if (query) url += `query=${encodeURIComponent(query)}&`;
    if (category && category !== 'all') url += `category=${encodeURIComponent(category)}&`;
    if (maxPrice) url += `max_price=${maxPrice}&`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to search products');
    return res.json();
  },

  async evaluateBudget(productId: string, userId: string = 'usr_alex_chen'): Promise<BudgetEvaluation> {
    const res = await fetch(`${API_BASE}/shopping/evaluate-budget`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: productId, user_id: userId })
    });
    if (!res.ok) throw new Error('Failed to evaluate budget');
    return res.json();
  },

  async compareProducts(productIds: string[], targetBudget?: number) {
    const res = await fetch(`${API_BASE}/shopping/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_ids: productIds, target_budget: targetBudget })
    });
    if (!res.ok) throw new Error('Failed to compare products');
    return res.json();
  },

  // PayPal Sandbox Payments
  async createPayPalOrder(productId: string, userId: string = 'usr_alex_chen') {
    const res = await fetch(`${API_BASE}/payments/create-order`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: productId, user_id: userId })
    });
    if (!res.ok) throw new Error('Failed to create PayPal order');
    return res.json();
  },

  async capturePayPalOrder(orderId: string) {
    const res = await fetch(`${API_BASE}/payments/capture-order`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ order_id: orderId })
    });
    if (!res.ok) throw new Error('Failed to capture PayPal order');
    return res.json();
  },

  async testPayPalConnection() {
    const res = await fetch(`${API_BASE}/payments/test-connection`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to test PayPal Sandbox connection');
    return res.json();
  },

  async getPaymentHistory() {
    const res = await fetch(`${API_BASE}/payments/history`);
    if (!res.ok) throw new Error('Failed to fetch payment history');
    return res.json();
  },

  async getPaymentConfigStatus() {
    const res = await fetch(`${API_BASE}/payments/config-status`);
    if (!res.ok) throw new Error('Failed to fetch payment config status');
    return res.json();
  },

  async getPayPalOrder(orderId: string) {
    const res = await fetch(`${API_BASE}/payments/orders/${orderId}`);
    if (!res.ok) throw new Error('Failed to fetch PayPal order status');
    return res.json();
  },

  async refundPayPalPayment(captureId: string, amount?: number, note?: string) {
    const res = await fetch(`${API_BASE}/payments/refund`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ capture_id: captureId, amount, note })
    });
    if (!res.ok) throw new Error('Failed to refund PayPal payment');
    return res.json();
  },

  // Demo Data Bank & Scenarios
  async getScenarios(): Promise<TestScenario[]> {
    const res = await fetch(`${API_BASE}/demo-data/scenarios`);
    if (!res.ok) throw new Error('Failed to load scenarios');
    return res.json();
  },

  async loadScenario(scenarioId: string) {
    const res = await fetch(`${API_BASE}/demo-data/load-scenario`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario_id: scenarioId })
    });
    if (!res.ok) throw new Error('Failed to activate scenario');
    return res.json();
  },

  async validateDataBank() {
    const res = await fetch(`${API_BASE}/demo-data/validate`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to validate data bank');
    return res.json();
  },

  async regenerateDataBank(seed: number = 42) {
    const res = await fetch(`${API_BASE}/demo-data/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ seed })
    });
    if (!res.ok) throw new Error('Failed to regenerate data bank');
    return res.json();
  },

  async resetDataBank() {
    const res = await fetch(`${API_BASE}/demo-data/reset`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to reset data bank');
    return res.json();
  },

  async getSystemSettings() {
    const res = await fetch(`${API_BASE}/settings/status`);
    if (!res.ok) throw new Error('Failed to fetch system settings');
    return res.json();
  },

  // =========================================================================
  // FINANCIAL FORMULAS & CALCULATION ENGINE
  // =========================================================================
  async getFormulas(domain?: string, search?: string): Promise<FormulaEntry[]> {
    let url = `${API_BASE}/formulas?`;
    if (domain) url += `domain=${encodeURIComponent(domain)}&`;
    if (search) url += `search=${encodeURIComponent(search)}&`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch formula catalogue');
    return res.json();
  },

  async getFormulaCatalogSummary(): Promise<FormulaSummary> {
    const res = await fetch(`${API_BASE}/formulas/catalog/summary`);
    if (!res.ok) throw new Error('Failed to fetch formula catalog summary');
    return res.json();
  },

  async executeFormula(formulaId: string, inputs: Record<string, any>): Promise<CalculationResult> {
    const res = await fetch(`${API_BASE}/formulas/${formulaId}/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(inputs)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Calculation failed' }));
      throw new Error(err.detail || 'Calculation failed');
    }
    return res.json();
  },

  // =========================================================================
  // MULTI-FORMULA DECISION COMPOSITION
  // =========================================================================
  async getCompositionRecipes(): Promise<CompositionRecipe[]> {
    const res = await fetch(`${API_BASE}/composition/recipes`);
    if (!res.ok) throw new Error('Failed to fetch composition recipes');
    return res.json();
  },

  async evaluateSubscriptionDecision(payload: {
    subscription_name: string;
    monthly_cost: number;
    recorded_uses_90_days?: number;
    alternative_monthly_price?: number;
    alternative_name?: string;
  }): Promise<CompositionWorkflowResult> {
    const res = await fetch(`${API_BASE}/composition/subscription-decision`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to evaluate subscription decision');
    return res.json();
  },

  async evaluatePurchaseAffordability(payload: {
    item_name: string;
    price: number;
    shipping?: number;
    tax_pct?: number;
    available_liquid_cash: number;
    monthly_income: number;
    monthly_expenses: number;
    essential_expenses: number;
  }): Promise<CompositionWorkflowResult> {
    const res = await fetch(`${API_BASE}/composition/purchase-affordability`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to evaluate purchase affordability');
    return res.json();
  },

  async evaluateLoanEarlyPayoff(payload: {
    loan_principal: number;
    annual_interest_rate_pct: number;
    remaining_months: number;
    extra_monthly_repayment: number;
    liquid_cash_reserves: number;
    monthly_essential_expenses: number;
  }): Promise<CompositionWorkflowResult> {
    const res = await fetch(`${API_BASE}/composition/loan-early-payoff`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to evaluate loan early payoff');
    return res.json();
  },

  async compareDeposits(payload: {
    principal: number;
    tenure_months: number;
    option_a_name: string;
    option_a_rate_pct: number;
    option_a_compound_freq: number;
    option_b_name: string;
    option_b_rate_pct: number;
    option_b_compound_freq: number;
    marginal_tax_rate_pct?: number;
  }): Promise<CompositionWorkflowResult> {
    const res = await fetch(`${API_BASE}/composition/deposit-comparison`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to compare deposits');
    return res.json();
  },

  // =========================================================================
  // FINANCIAL AUTOMATION & ACTION SAFETY
  // =========================================================================
  async getAutomationRules(): Promise<AutomationRule[]> {
    const res = await fetch(`${API_BASE}/automation/rules`);
    if (!res.ok) throw new Error('Failed to load automation rules');
    return res.json();
  },

  async toggleAutomationRule(ruleId: string, enabled: boolean) {
    const res = await fetch(`${API_BASE}/automation/rules/${ruleId}/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled })
    });
    if (!res.ok) throw new Error('Failed to toggle automation rule');
    return res.json();
  },

  async triggerAutomationTest(ruleId: string, context?: any) {
    const res = await fetch(`${API_BASE}/automation/rules/${ruleId}/trigger`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(context || {})
    });
    if (!res.ok) throw new Error('Failed to trigger automation test');
    return res.json();
  },

  async getAutomationHistory(): Promise<ExecutionLog[]> {
    const res = await fetch(`${API_BASE}/automation/history`);
    if (!res.ok) throw new Error('Failed to load automation history');
    return res.json();
  },

  async getPendingActions(): Promise<PreparedAction[]> {
    const res = await fetch(`${API_BASE}/automation/pending-actions`);
    if (!res.ok) throw new Error('Failed to load pending actions');
    return res.json();
  },

  async approveAction(actionId: string, userId: string = 'usr_alex_chen') {
    const res = await fetch(`${API_BASE}/automation/actions/${actionId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId })
    });
    if (!res.ok) throw new Error('Failed to approve action');
    return res.json();
  },

  async rejectAction(actionId: string, reason?: string) {
    const res = await fetch(`${API_BASE}/automation/actions/${actionId}/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reason: reason || 'Declined by user' })
    });
    if (!res.ok) throw new Error('Failed to reject action');
    return res.json();
  },

  // =========================================================================
  // FINANCIAL OPTIMIZATION ENGINE
  // =========================================================================
  async getOptimizationOpportunities(userId: string = 'usr_alex_chen'): Promise<OptimizationOpportunity[]> {
    const res = await fetch(`${API_BASE}/optimization/opportunities?user_id=${userId}`);
    if (!res.ok) throw new Error('Failed to load optimization opportunities');
    return res.json();
  },

  // =========================================================================
  // HACKATHON MVP: PERSISTENT TRANSACTIONS & CSV IMPORT
  // =========================================================================
  async getPersistedTransactions(userId: string = 'usr_alex_chen', category?: string, search?: string, dataScope: string = 'auto') {
    let url = `${API_BASE}/v1/transactions?user_id=${encodeURIComponent(userId)}&data_scope=${encodeURIComponent(dataScope)}`;
    if (category && category !== 'all') url += `&category=${encodeURIComponent(category)}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch persisted transactions');
    return res.json();
  },

  async addManualTransaction(userId: string, payload: {
    date?: string;
    merchant: string;
    description?: string;
    amount: number;
    transaction_type?: string;
    category?: string;
    is_recurring?: boolean;
  }) {
    const res = await fetch(`${API_BASE}/v1/transactions?user_id=${encodeURIComponent(userId)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to add transaction');
    return res.json();
  },

  async deleteTransaction(userId: string, txId: string) {
    const res = await fetch(`${API_BASE}/v1/transactions/${encodeURIComponent(txId)}?user_id=${encodeURIComponent(userId)}`, {
      method: 'DELETE'
    });
    if (!res.ok) throw new Error('Failed to delete transaction');
    return res.json();
  },

  async previewCsvImport(userId: string, csvText: string) {
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('csv_text', csvText);
    const res = await fetch(`${API_BASE}/v1/transactions/import-csv/preview`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) throw new Error('Failed to preview CSV import');
    return res.json();
  },

  async confirmCsvImport(userId: string, records: any[], skipDuplicates: boolean = true) {
    const res = await fetch(`${API_BASE}/v1/transactions/import-csv/confirm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, records, skip_duplicates: skipDuplicates })
    });
    if (!res.ok) throw new Error('Failed to confirm CSV import');
    return res.json();
  },

  async getFinancialSummary(userId: string = 'usr_alex_chen', month?: string, dataScope: string = 'auto') {
    let url = `${API_BASE}/v1/transactions/summary?user_id=${encodeURIComponent(userId)}&data_scope=${encodeURIComponent(dataScope)}`;
    if (month) url += `&month=${encodeURIComponent(month)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch financial summary');
    return res.json();
  },

  // =========================================================================
  // HACKATHON MVP: GPS & NEARBY PLACES INTELLIGENCE
  // =========================================================================
  async getLocationStatus(userId: string = 'usr_alex_chen') {
    const res = await fetch(`${API_BASE}/v1/location/status?user_id=${encodeURIComponent(userId)}`);
    if (!res.ok) throw new Error('Failed to fetch location status');
    return res.json();
  },

  async updateLocationPermission(payload: {
    user_id?: string;
    is_granted: boolean;
    precision_mode?: string;
    access_type?: string;
    latitude?: number;
    longitude?: number;
    city?: string;
    postal_code?: string;
    location_source?: string;
  }) {
    const res = await fetch(`${API_BASE}/v1/location/permission`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to update location permission');
    return res.json();
  },

  async discoverNearbyPlaces(
    category: string = 'fitness',
    userId: string = 'usr_alex_chen',
    maxDistanceMiles: number = 10.0,
    allowDemoBenchmark: boolean = false
  ) {
    const res = await fetch(
      `${API_BASE}/v1/location/nearby?category=${encodeURIComponent(category)}&user_id=${encodeURIComponent(userId)}&max_distance_miles=${maxDistanceMiles}&allow_demo_benchmark=${allowDemoBenchmark}`
    );
    if (!res.ok) throw new Error('Failed to discover nearby places');
    return res.json();
  },

  async discoverLiveOsmPlaces(latitude: number, longitude: number, category: string = 'groceries', radiusMeters: number = 3000) {
    const res = await fetch(
      `${API_BASE}/v1/location/live-osm?latitude=${latitude}&longitude=${longitude}&category=${encodeURIComponent(category)}&radius_meters=${radiusMeters}`
    );
    if (!res.ok) throw new Error('Failed to query OpenStreetMap places');
    return res.json();
  },

  async getGymScenario(userId: string = 'usr_alex_chen') {
    const res = await fetch(`${API_BASE}/v1/location/gym-scenario?user_id=${encodeURIComponent(userId)}`);
    if (!res.ok) throw new Error('Failed to fetch gym cross-module scenario');
    return res.json();
  },

  // =========================================================================
  // HACKATHON MVP: DAILY MONEY-SAVING INTELLIGENCE
  // =========================================================================
  async getSavingsDashboard(userId: string = 'usr_alex_chen') {
    const res = await fetch(`${API_BASE}/v1/savings/dashboard?user_id=${encodeURIComponent(userId)}`);
    if (!res.ok) throw new Error('Failed to fetch savings dashboard');
    return res.json();
  },

  async updateRecommendationDecision(recId: string, decision: string, userId: string = 'usr_alex_chen') {
    const res = await fetch(`${API_BASE}/v1/savings/recommendations/${encodeURIComponent(recId)}/decision`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ decision, user_id: userId })
    });
    if (!res.ok) throw new Error('Failed to update recommendation decision');
    return res.json();
  }
};
