"use client";

import { useState, useEffect, useCallback } from "react";
import {
  listDocuments,
  getDocument,
  createFromTemplate as createFromTemplateApi,
  patchDocument as patchDocumentApi,
  type ListDocumentsFilters,
  type DocumentSummary,
  type Document,
  type DocumentChange,
} from "@/lib/documents";

export function useDocuments(filters: ListDocumentsFilters = {}) {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const list = await listDocuments(filters);
      setDocuments(list);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load documents");
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  }, [filters.party_id, filters.party_name, filters.doc_type]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    listDocuments(filters)
      .then((list) => {
        if (!cancelled) setDocuments(list);
      })
      .catch((e) => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to load documents");
          setDocuments([]);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [filters.party_id, filters.party_name, filters.doc_type]);

  return { documents, loading, error, refetch };
}

export function useDocument(id: string | null) {
  const [document, setDocument] = useState<Document | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    if (!id) {
      setDocument(null);
      setLoading(false);
      setError(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const doc = await getDocument(id);
      setDocument(doc);
      if (doc === null) {
        setError("Document not found");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load document");
      setDocument(null);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (!id) {
      setDocument(null);
      setLoading(false);
      setError(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    getDocument(id)
      .then((doc) => {
        if (!cancelled) {
          setDocument(doc);
          if (doc === null) setError("Document not found");
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to load document");
          setDocument(null);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  return { document, loading, error, refetch };
}

export function useCreateFromTemplate() {
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createFromTemplate = useCallback(
    async (templateId: string, title?: string): Promise<Document | null> => {
      setCreating(true);
      setError(null);
      try {
        const doc = await createFromTemplateApi(templateId, title);
        return doc;
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Failed to create document";
        setError(msg);
        return null;
      } finally {
        setCreating(false);
      }
    },
    []
  );

  const resetError = useCallback(() => setError(null), []);

  return { createFromTemplate, creating, error, resetError };
}

export function usePatchDocument() {
  const [patching, setPatching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const patch = useCallback(
    async (
      id: string,
      version: number,
      changes: DocumentChange[],
      options?: { title?: string }
    ): Promise<Document | null> => {
      setPatching(true);
      setError(null);
      try {
        const doc = await patchDocumentApi(id, version, changes, options);
        return doc;
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Save failed";
        setError(msg);
        return null;
      } finally {
        setPatching(false);
      }
    },
    []
  );

  const resetError = useCallback(() => setError(null), []);

  return { patch, patching, error, resetError };
}
