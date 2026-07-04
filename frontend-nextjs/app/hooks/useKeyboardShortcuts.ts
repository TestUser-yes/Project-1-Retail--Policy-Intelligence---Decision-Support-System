"use client";

import { useEffect, useCallback } from "react";

export interface KeyboardShortcut {
  key: string;
  ctrlKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
  callback: () => void;
}

export function useKeyboardShortcuts(shortcuts: KeyboardShortcut[]) {
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      shortcuts.forEach((shortcut) => {
        const matchesKey = event.key.toLowerCase() === shortcut.key.toLowerCase();
        const matchesCtrl = (shortcut.ctrlKey ?? false) === event.ctrlKey;
        const matchesShift = (shortcut.shiftKey ?? false) === event.shiftKey;
        const matchesAlt = (shortcut.altKey ?? false) === event.altKey;

        if (matchesKey && matchesCtrl && matchesShift && matchesAlt) {
          event.preventDefault();
          shortcut.callback();
        }
      });
    };

    window.addEventListener("keydown", handleKeyPress);
    return () => window.removeEventListener("keydown", handleKeyPress);
  }, [shortcuts]);
}

// Common shortcuts
export const SHORTCUTS = {
  FOCUS_SEARCH: { key: "/", callback: () => {} },
  SUBMIT_QUERY: { key: "Enter", ctrlKey: true, callback: () => {} },
  CLEAR_CHAT: { key: "l", ctrlKey: true, shiftKey: true, callback: () => {} },
  EXPORT_DATA: { key: "e", ctrlKey: true, shiftKey: true, callback: () => {} },
  TOGGLE_THEME: { key: "t", ctrlKey: true, shiftKey: true, callback: () => {} },
};
