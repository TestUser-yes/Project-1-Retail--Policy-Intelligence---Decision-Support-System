"use client";

import { useState, useCallback } from "react";

export interface BulkOperation<T> {
  id: string;
  type: "export" | "delete" | "update" | "archive";
  items: T[];
  status: "pending" | "processing" | "completed" | "failed";
  progress: number;
  result?: {
    success: number;
    failed: number;
    errors: string[];
  };
}

export function useBulkOperations<T>() {
  const [operations, setOperations] = useState<BulkOperation<T>[]>([]);
  const [selectedItems, setSelectedItems] = useState<T[]>([]);

  const createOperation = useCallback(
    (type: BulkOperation<T>["type"], items: T[]) => {
      const operation: BulkOperation<T> = {
        id: Date.now().toString(),
        type,
        items,
        status: "pending",
        progress: 0,
      };

      setOperations((prev) => [...prev, operation]);
      return operation.id;
    },
    []
  );

  const updateProgress = useCallback((operationId: string, progress: number) => {
    setOperations((prev) =>
      prev.map((op) =>
        op.id === operationId ? { ...op, progress } : op
      )
    );
  }, []);

  const completeOperation = useCallback(
    (operationId: string, result: BulkOperation<T>["result"]) => {
      setOperations((prev) =>
        prev.map((op) =>
          op.id === operationId
            ? { ...op, status: "completed", progress: 100, result }
            : op
        )
      );
    },
    []
  );

  const failOperation = useCallback(
    (operationId: string, error: string) => {
      setOperations((prev) =>
        prev.map((op) =>
          op.id === operationId
            ? {
                ...op,
                status: "failed",
                result: { success: 0, failed: op.items.length, errors: [error] },
              }
            : op
        )
      );
    },
    []
  );

  const selectItems = useCallback((items: T[]) => {
    setSelectedItems(items);
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedItems([]);
  }, []);

  return {
    operations,
    selectedItems,
    createOperation,
    updateProgress,
    completeOperation,
    failOperation,
    selectItems,
    clearSelection,
  };
}
