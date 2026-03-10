"use client";

import { TopTabs } from "@/components/top-tabs";

export default function Home() {
  return (
    <div className="min-h-screen bg-background p-6">
      <main className="mx-auto max-w-4xl flex flex-col gap-6">
        <TopTabs />
      </main>
    </div>
  );
}
