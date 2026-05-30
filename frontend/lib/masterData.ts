import type { MasterData } from "./types";

export const fallbackMasterData: MasterData[] = [
  { category: "country", description: "INDIA", value: "IN" },
  { category: "country", description: "UNITED STATES", value: "US" },
  { category: "country", description: "UNITED KINGDOM", value: "GB" },
  { category: "country", description: "GERMANY", value: "DE" },
  { category: "country", description: "CANADA", value: "CA" },
  { category: "country", description: "AUSTRALIA", value: "AU" },
  { category: "department", description: "Engineering", value: "ENG" },
  { category: "department", description: "Product", value: "PROD" },
  { category: "department", description: "Data", value: "DATA" },
  { category: "department", description: "Human Resources", value: "HR" },
  { category: "department", description: "Finance", value: "FIN" },
  { category: "department", description: "Sales", value: "SALES" },
  { category: "department", description: "Support", value: "SUPPORT" },
  { category: "job_title", description: "Software Engineer", value: "SWE" },
  { category: "job_title", description: "Senior Software Engineer", value: "SR_SWE" },
  { category: "job_title", description: "Product Manager", value: "PM" },
  { category: "job_title", description: "Data Analyst", value: "DA" },
  { category: "job_title", description: "HR Business Partner", value: "HRBP" },
  { category: "job_title", description: "Finance Manager", value: "FIN_MGR" },
  { category: "job_title", description: "Sales Executive", value: "SALES_EXEC" },
  { category: "job_title", description: "Support Specialist", value: "SUPPORT_SPEC" },
];

export function optionsFor(masterData: MasterData[], category: MasterData["category"]) {
  return masterData
    .filter((record) => record.category === category)
    .sort((left, right) => left.description.localeCompare(right.description));
}

export function labelFor(
  masterData: MasterData[],
  category: MasterData["category"],
  value: string,
) {
  return masterData.find((record) => record.category === category && record.value === value)
    ?.description ?? value;
}
