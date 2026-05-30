import { PageHeader } from "@/components/PageHeader";
import { SalaryDetailsClient } from "./SalaryDetailsClient";

type SalaryDetailsPageProps = {
  searchParams: Promise<{ id?: string }>;
};

export default async function SalaryDetailsPage({ searchParams }: SalaryDetailsPageProps) {
  const { id } = await searchParams;

  return (
    <>
      <PageHeader eyebrow="Employee management" title="Manage salary" />
      {id ? (
        <SalaryDetailsClient employeeId={id} />
      ) : (
        <div className="status-message status-error">Employee id is required.</div>
      )}
    </>
  );
}
