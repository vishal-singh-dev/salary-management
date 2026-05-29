import { PageHeader } from "@/components/PageHeader";
import { DashboardClient } from "./DashboardClient";

export default function DashboardPage() {
  return (
    <>
      <PageHeader
        eyebrow="Salary insights"
        title="Compensation dashboard"
      />
      <DashboardClient />
    </>
  );
}
