"use client";

import { SearchBar } from "@/components/search-bar";
import { TopTabs } from "@/components/top-tabs";

export default function Home() {
  return (
    <div className="min-h-screen bg-background p-6">
      <main className="mx-auto max-w-4xl flex flex-col gap-8">
        <SearchBar />
        <TopTabs />
      </main>
    </div>
  );
}
