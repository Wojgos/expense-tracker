export interface User {
  id: string;
  email: string;
  display_name: string;
  is_active: boolean;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface Member {
  user_id: string;
  display_name: string;
  email: string;
  role: "admin" | "member";
}

export interface Group {
  id: string;
  name: string;
  description: string | null;
  created_by: string;
  created_at: string;
  members: Member[];
}

export interface GroupListItem {
  id: string;
  name: string;
  description: string | null;
  member_count: number;
  created_at: string;
}

export interface SplitDetail {
  user_id: string;
  owed_amount: string;
}

export type SplitType = "equal" | "exact" | "percent" | "shares";

export interface Expense {
  id: string;
  group_id: string;
  paid_by: string;
  payer_name: string;
  amount: string;
  currency: string;
  description: string;
  split_type: SplitType;
  expense_date: string;
  created_at: string;
  splits: SplitDetail[];
}

export interface BalanceItem {
  user_id: string;
  display_name: string;
  balance: string;
}

export interface SuggestedTransfer {
  from_user: string;
  from_name: string;
  to_user: string;
  to_name: string;
  amount: string;
}

export interface Settlement {
  id: string;
  group_id: string;
  paid_by: string;
  payer_name: string;
  paid_to: string;
  receiver_name: string;
  amount: string;
  currency: string;
  created_at: string;
}

export interface SettlementSummary {
  balances: BalanceItem[];
  suggested_transfers: SuggestedTransfer[];
  settlements: Settlement[];
}

export type RecurrenceInterval = "daily" | "weekly" | "monthly";

export interface RecurringExpense {
  id: string;
  group_id: string;
  created_by: string;
  creator_name: string;
  description: string;
  amount: string;
  currency: string;
  split_type: SplitType;
  interval: RecurrenceInterval;
  day_of_month: number | null;
  next_run: string;
  is_active: boolean;
}

export interface CurrencyConvertResponse {
  base: string;
  target: string;
  rate: number;
  original_amount: number;
  converted_amount: number;
}

export interface CurrencyConvertApiResponse {
  base: string;
  target: string;
  rate: string | number;
  original_amount: string | number;
  converted_amount: string | number;
}
