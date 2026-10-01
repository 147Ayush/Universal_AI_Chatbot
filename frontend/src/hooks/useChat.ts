// frontend/src/hooks/useChat.ts

import { useState, useCallback } from "react";
import { streamChatMessage } from "../services/api";

export interface Message {
  role: "user" | "assistant";
  content: string;
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (text: string, provider: string = "groq") => {
    setError(null);
    setMessages((prev) => [...prev, { role: "user", content: text }]);

    // Add an empty assistant message that we'll fill in as chunks arrive
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);
    setIsStreaming(true);

    await streamChatMessage(
      text,
      provider,
      (chunk) => {
        setMessages((prev) => {
          const updated = [...prev];
          const lastIndex = updated.length - 1;
          updated[lastIndex] = {
            ...updated[lastIndex],
            content: updated[lastIndex].content + chunk,
          };
          return updated;
        });
      },
      () => setIsStreaming(false),
      (errMsg) => {
        setError(errMsg);
        setIsStreaming(false);
      }
    );
  }, []);

  return { messages, sendMessage, isStreaming, error };
}