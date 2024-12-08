import type { Attachment } from 'ai';
import type { ChatRequestOptions as BaseChatRequestOptions, Message as BaseMessage } from 'ai';

export type CreateMessage = Omit<Message, "id"> & {
  id?: Message["id"];
}

export type Message = BaseMessage & {
  experimental_graph_attachments?: Attachment[];
  tool_overrides?: string;
};

export type ChatRequestOptions = BaseChatRequestOptions & {
  experimental_graph_attachments?: Attachment[];
  tool_overrides?: string;
};
