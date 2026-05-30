"use client";

import { useEffect, useState } from "react";

import type { ApiLoadingState } from "@/lib/api";
import { subscribeToApiLoading } from "@/lib/api";

const loadingMessages = [
  "Preparing your data",
  "Almost there",
  "Got it",
];
const savingMessages = [
  "Saving your changes",
  "Just a moment",
  "Done",
];

export function GlobalLoader() {
  const [loaderState, setLoaderState] = useState<ApiLoadingState>({
    isLoading: false,
    action: "load",
  });
  const [messageIndex, setMessageIndex] = useState(0);
  const messages = loaderState.action === "save" ? savingMessages : loadingMessages;

  useEffect(() => subscribeToApiLoading(setLoaderState), []);

  useEffect(() => {
    if (!loaderState.isLoading) {
      setMessageIndex(0);
      return;
    }

    const interval = window.setInterval(() => {
      setMessageIndex((current) => (current + 1) % messages.length);
    }, 1200);

    return () => window.clearInterval(interval);
  }, [loaderState.isLoading, messages.length]);

  useEffect(() => {
    setMessageIndex(0);
  }, [loaderState.action]);

  if (!loaderState.isLoading) {
    return null;
  }

  return (
    <div aria-live="polite" aria-busy="true" className="loader-overlay" role="status">
      <div className="loader-panel">
        <div className="loader-mark" aria-hidden="true">
          <span>S</span>
          <span>M</span>
        </div>
        <div className="loader-content">
          <p className="loader-title">{messages[messageIndex]}</p>
          <div className="loader-track" aria-hidden="true">
            <div className="loader-bar" />
          </div>
          <p className="loader-copy">Please stay on this page</p>
        </div>
      </div>
    </div>
  );
}
