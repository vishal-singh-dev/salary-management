import type {
  Employee,
  EmployeeCreateInput,
  EmployeeListResponse,
  EmployeeNextIdResponse,
  EmployeeUpdateInput,
  HealthResponse,
  MasterData,
  SalaryAnalyticsFilters,
  SalaryAnalyticsResponse,
} from "./types";

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";
const employeePageCache = new Map<string, EmployeeListResponse>();
const maxCachedEmployeePages = 3;
const employeeRecordCache = new Map<string, Employee>();
let masterDataCache: MasterData[] | null = null;
export type ApiLoadingState = {
  isLoading: boolean;
  action: "load" | "save";
};

const loadingListeners = new Set<(state: ApiLoadingState) => void>();
let activeRequestCount = 0;
let activeSaveRequestCount = 0;

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export function getApiBaseUrl(): string {
  return (process.env.PUBLIC_API_BASE_URL ?? DEFAULT_API_BASE_URL).replace(/\/$/, "");
}

export function buildUrl(
  path: string,
  params?: Record<string, string | number | boolean | null | undefined>,
) {
  const url = new URL(`${getApiBaseUrl()}${path}`);

  Object.entries(params ?? {}).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });

  return url.toString();
}

export function subscribeToApiLoading(listener: (state: ApiLoadingState) => void) {
  loadingListeners.add(listener);
  listener(currentLoadingState());

  return () => {
    loadingListeners.delete(listener);
  };
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const action = requestAction(init);
  beginApiRequest(action);
  try {
    const response = await fetch(buildUrl(path), {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init?.headers,
      },
    });

    if (!response.ok) {
      let message = `Request failed with status ${response.status}`;
      try {
        const body = (await response.json()) as { detail?: string };
        message = body.detail ?? message;
      } catch {
        // Keep the generic message when the backend does not return JSON.
      }
      throw new ApiError(message, response.status);
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return (await response.json()) as T;
  } finally {
    endApiRequest(action);
  }
}

export function getHealth() {
  return requestJson<HealthResponse>("/health");
}

export function listMasterData(category?: MasterData["category_name"], parentCode?: string) {
  if (!category && masterDataCache) {
    return Promise.resolve(masterDataCache);
  }

  if (category && masterDataCache) {
    return Promise.resolve(
      masterDataCache
        .filter((record) => record.category_name === category)
        .filter((record) => !parentCode || record.parent_code === parentCode),
    );
  }

  return requestJson<MasterData[]>(
    buildUrl("/api/v1/master-data", { category, parent_code: parentCode }).replace(
      getApiBaseUrl(),
      "",
    ),
  ).then((records) => {
    if (!category) {
      masterDataCache = records;
    }
    return records;
  });
}

export function listEmployees(options: {
  limit?: number;
  offset?: number;
  includeInactive?: boolean;
}) {
  const cacheKey = JSON.stringify({
    limit: options.limit ?? 25,
    offset: options.offset ?? 0,
    includeInactive: options.includeInactive ?? false,
  });
  const cached = employeePageCache.get(cacheKey);
  if (cached) {
    employeePageCache.delete(cacheKey);
    employeePageCache.set(cacheKey, cached);
    return Promise.resolve(cached);
  }

  return requestJson<EmployeeListResponse>(
    buildUrl("/api/v1/employees", {
      limit: options.limit ?? 25,
      offset: options.offset ?? 0,
      include_inactive: options.includeInactive ?? false,
    }).replace(getApiBaseUrl(), ""),
  ).then((response) => {
    cacheEmployeePage(cacheKey, response);
    response.items.forEach((employee) => employeeRecordCache.set(employee.id, employee));
    return response;
  });
}

export function getEmployee(employeeId: string) {
  const cached = employeeRecordCache.get(employeeId);
  if (cached) {
    return Promise.resolve(cached);
  }

  return requestJson<Employee>(`/api/v1/employees/${employeeId}`).then((employee) => {
    employeeRecordCache.set(employee.id, employee);
    return employee;
  });
}

export function getNextEmployeeId() {
  return requestJson<EmployeeNextIdResponse>("/api/v1/employees/next-id");
}

export function createEmployee(input: EmployeeCreateInput) {
  return requestJson<Employee>("/api/v1/employees", {
    method: "POST",
    body: JSON.stringify(input),
  }).then((employee) => {
    clearEmployeePageCache();
    employeeRecordCache.set(employee.id, employee);
    return employee;
  });
}

export function updateEmployee(employeeId: string, input: EmployeeUpdateInput) {
  return requestJson<Employee>(`/api/v1/employees/${employeeId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  }).then((employee) => {
    clearEmployeePageCache();
    employeeRecordCache.set(employee.id, employee);
    return employee;
  });
}

export function deleteEmployee(employeeId: string) {
  return requestJson<void>(`/api/v1/employees/${employeeId}`, {
    method: "DELETE",
  }).then((response) => {
    clearEmployeePageCache();
    employeeRecordCache.delete(employeeId);
    return response;
  });
}

export function getSalaryAnalytics(filters: SalaryAnalyticsFilters) {
  return requestJson<SalaryAnalyticsResponse>(
    buildUrl("/api/v1/analytics/salaries", {
      country_code: filters.country_code,
      department: filters.department,
      title: filters.title,
      include_inactive: filters.include_inactive ?? false,
      currency_basis: filters.currency_basis ?? "local",
    }).replace(getApiBaseUrl(), ""),
  );
}

function cacheEmployeePage(cacheKey: string, response: EmployeeListResponse) {
  employeePageCache.set(cacheKey, response);

  while (employeePageCache.size > maxCachedEmployeePages) {
    const oldestKey = employeePageCache.keys().next().value;
    if (!oldestKey) {
      break;
    }
    employeePageCache.delete(oldestKey);
  }
}

function clearEmployeePageCache() {
  employeePageCache.clear();
}

function beginApiRequest(action: ApiLoadingState["action"]) {
  activeRequestCount += 1;
  if (action === "save") {
    activeSaveRequestCount += 1;
  }
  notifyLoadingListeners();
}

function endApiRequest(action: ApiLoadingState["action"]) {
  activeRequestCount = Math.max(activeRequestCount - 1, 0);
  if (action === "save") {
    activeSaveRequestCount = Math.max(activeSaveRequestCount - 1, 0);
  }
  notifyLoadingListeners();
}

function notifyLoadingListeners() {
  const state = currentLoadingState();
  loadingListeners.forEach((listener) => listener(state));
}

function currentLoadingState(): ApiLoadingState {
  return {
    isLoading: activeRequestCount > 0,
    action: activeSaveRequestCount > 0 ? "save" : "load",
  };
}

function requestAction(init?: RequestInit): ApiLoadingState["action"] {
  const method = init?.method?.toUpperCase() ?? "GET";
  return method === "GET" ? "load" : "save";
}
