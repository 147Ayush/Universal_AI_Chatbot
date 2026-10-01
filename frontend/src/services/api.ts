// frontend/src/services/api.ts

const API_BASE_URL = "http://127.0.0.1:8000";

export interface ChatStreamChunk {
  content?: string;
  error?: string;
  done?: boolean;
}

/**
 * Sends a message and streams the reply token-by-token.
 * Calls `onChunk` for each piece of text as it arrives.
 */
export async function streamChatMessage(
  message: string,
  provider: string,
  onChunk: (text: string) => void,
  onDone: () => void,
  onError: (message: string) => void
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, provider }),
  });

  if (!response.body) {
    onError("No response body from server");
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // SSE events are separated by a blank line ("\n\n")
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? ""; // keep any incomplete event for next loop

    for (const event of events) {
      const line = event.replace(/^data:\s*/, "");
      if (!line) continue;

      const parsed: ChatStreamChunk = JSON.parse(line);

      if (parsed.error) {
        onError(parsed.error);
      } else if (parsed.done) {
        onDone();
      } else if (parsed.content) {
        onChunk(parsed.content);
      }
    }
  }
}