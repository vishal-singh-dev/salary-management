export function formatMoney(value: string | null, currencyCode?: string | null): string {
  if (value === null) {
    return "Not available";
  }

  const amount = Number(value);
  if (Number.isNaN(amount)) {
    return value;
  }

  return new Intl.NumberFormat("en-US", {
    style: currencyCode ? "currency" : "decimal",
    currency: currencyCode ?? undefined,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-US").format(value);
}

export function salaryRange(minValue: string | null, maxValue: string | null): string | null {
  if (minValue === null || maxValue === null) {
    return null;
  }

  return String(Number(maxValue) - Number(minValue));
}

export function meanMedianDifference(meanValue: string | null, medianValue: string | null) {
  if (meanValue === null || medianValue === null) {
    return null;
  }

  return String(Number(meanValue) - Number(medianValue));
}
