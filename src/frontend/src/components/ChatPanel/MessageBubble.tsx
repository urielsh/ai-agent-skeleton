interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
}

export function MessageBubble({ role, content }: MessageBubbleProps) {
  return (
    <div className={`message-bubble message-${role}`}>
      <div className="message-role">{role === "user" ? "You" : "Assistant"}</div>
      <div className="message-content">{content}</div>
    </div>
  );
}
