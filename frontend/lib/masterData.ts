import type { MasterData } from "./types";

export const fallbackMasterData: MasterData[] = [
  master("Country", "India", "IN", null, null, 1),
  master("Country", "China", "CHN", null, null, 2),
  master("Country", "Australia", "AUS", null, null, 3),
  master("Country", "United States", "US", null, null, 4),
  master("Country", "United Kingdom", "GB", null, null, 5),
  master("Country", "Germany", "DE", null, null, 6),
  master("Country", "Canada", "CA", null, null, 7),
  master("Department", "HR", "HR", "Country", "IN", 1),
  master("Department", "Finance", "FIN", "Country", "IN", 2),
  master("Department", "Support", "SP", "Country", "CHN", 3),
  master("Department", "Labour", "LAB", "Country", "CHN", 4),
  master("Department", "Engineering", "ENG", "Country", "AUS", 5),
  master("Department", "Product", "PROD", "Country", "AUS", 6),
  master("Department", "Engineering", "US_ENG", "Country", "US", 7),
  master("Department", "Sales", "US_SALES", "Country", "US", 8),
  master("Department", "Operations", "GB_OPS", "Country", "GB", 9),
  master("Department", "Finance", "GB_FIN", "Country", "GB", 10),
  master("Department", "Engineering", "DE_ENG", "Country", "DE", 11),
  master("Department", "Data", "DE_DATA", "Country", "DE", 12),
  master("Department", "Support", "CA_SUPPORT", "Country", "CA", 13),
  master("Department", "HR", "CA_HR", "Country", "CA", 14),
  master("JobTitle", "HR Finance", "HRF", "Department", "HR", 1),
  master("JobTitle", "HR Operations", "HRO", "Department", "HR", 2),
  master("JobTitle", "Finance Manager", "FIN_MGR", "Department", "FIN", 3),
  master("JobTitle", "Payroll Specialist", "PAYROLL", "Department", "FIN", 4),
  master("JobTitle", "Call Support", "CS", "Department", "SP", 5),
  master("JobTitle", "General Support", "GS", "Department", "SP", 6),
  master("JobTitle", "Software Engineer", "SWE", "Department", "ENG", 9),
  master("JobTitle", "Senior Software Engineer", "SR_SWE", "Department", "ENG", 10),
  master("JobTitle", "Platform Engineer", "US_PE", "Department", "US_ENG", 13),
  master("JobTitle", "Engineering Manager", "US_EM", "Department", "US_ENG", 14),
  master("Currency", "Indian Rupee", "INR", null, null, 1),
  master("Currency", "Chinese Yuan", "CNY", null, null, 2),
  master("Currency", "Australian Dollar", "AUD", null, null, 3),
  master("Currency", "United States Dollar", "USD", null, null, 4),
  master("Currency", "British Pound", "GBP", null, null, 5),
  master("Currency", "Euro", "EUR", null, null, 6),
  master("Currency", "Canadian Dollar", "CAD", null, null, 7),
];

export function optionsFor(
  masterData: MasterData[],
  categoryName: MasterData["category_name"],
  parentCode?: string,
) {
  return masterData
    .filter((record) => record.category_name === categoryName)
    .filter((record) => !parentCode || record.parent_code === parentCode)
    .sort(
      (left, right) =>
        (left.sort_order ?? 0) - (right.sort_order ?? 0) ||
        left.display_name.localeCompare(right.display_name),
    );
}

export function labelFor(
  masterData: MasterData[],
  categoryName: MasterData["category_name"],
  code: string,
) {
  return (
    masterData.find((record) => record.category_name === categoryName && record.code === code)
      ?.display_name ?? code
  );
}

function master(
  category_name: MasterData["category_name"],
  display_name: string,
  code: string,
  parent_category_name: string | null,
  parent_code: string | null,
  sort_order: number,
): MasterData {
  return {
    category_name,
    display_name,
    code,
    parent_category_name,
    parent_code,
    sort_order,
    is_active: true,
  };
}
