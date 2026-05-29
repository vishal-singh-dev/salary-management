export type CurrencyBasis = "local" | "usd";

export type HealthResponse = {
  status: string;
  environment: string;
};

export type MasterData = {
  category: "country" | "department" | "job_title";
  description: string;
  value: string;
};

export type SalaryRecord = {
  id: string;
  employee_id: string;
  currency_code: string;
  base_amount: string;
  variable_amount: string;
  hra_allowance_amount: string;
  pf_amount: string;
  gratuity_amount: string;
  effective_from: string;
  effective_to: string | null;
  exchange_rate_id: string;
  created_at: string;
};

export type Employee = {
  id: string;
  employee_id: string;
  full_name: string;
  title: string;
  department: string;
  country_code: string;
  from_date: string;
  to_date: string | null;
  created_at: string;
  current_salary: SalaryRecord | null;
};

export type EmployeeListResponse = {
  items: Employee[];
  total: number;
  limit: number;
  offset: number;
};

export type EmployeeNextIdResponse = {
  employee_id: string;
};

export type EmployeeCreateInput = {
  employee_id: string;
  full_name: string;
  title: string;
  department: string;
  country_code: string;
  from_date: string;
  initial_salary: {
    currency_code: string;
    base_amount: string;
    variable_amount: string;
    hra_allowance_amount: string;
    pf_amount: string;
    gratuity_amount: string;
    effective_from: string;
  };
};

export type EmployeeUpdateInput = Partial<
  Pick<Employee, "full_name" | "title" | "department" | "country_code" | "from_date" | "to_date">
>;

export type SalaryAnalyticsFilters = {
  country_code?: string;
  department?: string;
  title?: string;
  include_inactive?: boolean;
  currency_basis?: CurrencyBasis;
};

export type SalaryAnalyticsResponse = {
  filters: {
    country_code: string | null;
    department: string | null;
    title: string | null;
    include_inactive: boolean;
    currency_basis: CurrencyBasis;
  };
  employee_count: number;
  currency_code: string | null;
  min_base_salary: string | null;
  max_base_salary: string | null;
  mean_base_salary: string | null;
  median_base_salary: string | null;
  mode_base_salary: string | null;
};
