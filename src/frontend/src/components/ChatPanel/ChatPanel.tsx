import { useRef, useEffect } from "react";
import { useSessionStore } from "@/stores/sessionStore";
import { useSendChat } from "@/api/hooks";
import { ChatInput } from "./ChatInput";
import { MessageBubble } from "./MessageBubble";

interface ChatPanelProps {
  sessionId: string;
}

export function ChatPanel({ sessionId }: ChatPanelProps) {
  const messages = useSessionStore((s) => s.messages);
  const addMessage = useSessionStore((s) => s.addMessage);
  const setDraftInput = useSessionStore((s) => s.setDraftInput);
  const setMissingFields = useSessionStore((s) => s.setMissingFields);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const chatMutation = useSendChat(sessionId);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = (text: string) => {
    const userMsg = { id: crypto.randomUUID(), role: "user" as const, content: text };
    addMessage(userMsg);

    chatMutation.mutate(
      { message: text },
      {
        onSuccess: (data) => {
          addMessage({
            id: crypto.randomUUID(),
            role: "assistant",
            content: data.reply,
          });
          if (data.draft_input) setDraftInput(data.draft_input);
          setMissingFields(data.missing_fields);
        },
      }
    );
  };

  return (
    <div className="chat-panel">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            Start by describing your argument or claim.
          </div>
        )}
        {messages.map((msg) => (
          <MessageBubble key={msg.id} role={msg.role} content={msg.content} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      <ChatInput onSend={handleSend} disabled={chatMutation.isPending} />
    </div>
  );
}
