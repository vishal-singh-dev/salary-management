import { PageHeader } from "@/components/PageHeader";
import { SalaryDetailsClient } from "./SalaryDetailsClient";

type SalaryDetailsPageProps = {
  params: Promise<{ id: string }>;
};

export default async function SalaryDetailsPage({ params }: SalaryDetailsPageProps) {
  const { id } = await params;

  return (
    <>
      <PageHeader
        eyebrow="Employee management"
        title="Manage salary"
      />
      <SalaryDetailsClient employeeId={id} />
    </>
  );
}
