import { useChat as useOriginalChat } from 'ai/react';
import type { Message, ChatRequestOptions } from '@/types/message';

export function useCustomChat({
  api = "/api/chat",
  body,
  ...props
}: {
  api?: string;
  id?: string;
  body?: Record<string, any>;
  initialMessages?: Message[];
  onFinish?: (message: Message) => void;
}) {
  const chatHook = useOriginalChat({
    ...props,
    api,
    body,
    sendExtraMessageFields: true,
  });

  const handleSubmit = async (
    event?: { preventDefault?: () => void },
    chatRequestOptions?: ChatRequestOptions
  ) => {
    if (event) event.preventDefault();
    if (!chatHook.input && !chatRequestOptions?.allowEmptySubmit) return;

    const message: Message = {
      id: crypto.randomUUID(),
      createdAt: new Date(),
      role: 'user',
      content: chatHook.input,
      experimental_graph_attachments: chatRequestOptions?.experimental_graph_attachments,
      tool_overrides: chatRequestOptions?.tool_overrides
    };

    await chatHook.append(message, {
      ...chatRequestOptions,
      body: {
        ...body,
        ...chatRequestOptions?.body,
      }
    });

    chatHook.setInput('');
  };

  return {
    ...chatHook,
    handleSubmit
  };
} 