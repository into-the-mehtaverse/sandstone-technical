"use client";

import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useDocuments, useCreateFromTemplate } from "@/hooks/use-documents";
import { TemplateList } from "@/components/template-list";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export function TopTabs() {
  const router = useRouter();
  const { documents: templates, loading: templatesLoading, error: templatesError } =
    useDocuments({ doc_type: "template" });
  const { documents: allDocs, loading: allDocsLoading, error: allDocsError } =
    useDocuments();
  const { createFromTemplate, creating, error: createError } = useCreateFromTemplate();

  async function handleSelectTemplate(templateId: string) {
    const doc = await createFromTemplate(templateId);
    if (doc) {
      router.push(`/document/${doc.id}`);
    } else if (createError) {
      toast.error(createError);
    }
  }

  return (
    <Tabs defaultValue="templates" className="w-full">
      <TabsList className="w-full max-w-[240px]">
        <TabsTrigger value="templates" className="flex-1">
          Templates
        </TabsTrigger>
        <TabsTrigger value="all" className="flex-1">
          All docs
        </TabsTrigger>
      </TabsList>

      <TabsContent value="templates" className="mt-6">
        <h1 className="text-2xl font-semibold text-foreground mb-4">Templates</h1>
        {templatesLoading && (
          <p className="text-muted-foreground text-sm">Loading templates…</p>
        )}
        {templatesError && (
          <p className="text-sm text-destructive" role="alert">
            {templatesError}
          </p>
        )}
        {!templatesLoading && !templatesError && (
          <TemplateList
            templates={templates}
            onSelectTemplate={handleSelectTemplate}
            disabled={creating}
          />
        )}
        {creating && (
          <p className="text-sm text-muted-foreground mt-2">Creating document…</p>
        )}
      </TabsContent>

      <TabsContent value="all" className="mt-6">
        <h1 className="text-2xl font-semibold text-foreground mb-4">All docs</h1>
        {allDocsLoading && (
          <p className="text-muted-foreground text-sm">Loading documents…</p>
        )}
        {allDocsError && (
          <p className="text-sm text-destructive" role="alert">
            {allDocsError}
          </p>
        )}
        {!allDocsLoading && !allDocsError && (
          <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3 list-none p-0 m-0">
            {allDocs.length === 0 ? (
              <p className="text-muted-foreground text-sm col-span-full">No documents.</p>
            ) : (
              allDocs.map((doc) => (
                <li key={doc.id}>
                  <button
                    type="button"
                    onClick={() => router.push(`/document/${doc.id}`)}
                    className="w-full text-left rounded-md border border-border bg-muted/30 hover:bg-muted/50 px-4 py-3 text-sm transition focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  >
                    <span className="font-medium text-foreground block truncate">
                      {doc.title}
                    </span>
                    <span className="text-xs text-muted-foreground">{doc.id}</span>
                  </button>
                </li>
              ))
            )}
          </ul>
        )}
      </TabsContent>
    </Tabs>
  );
}
