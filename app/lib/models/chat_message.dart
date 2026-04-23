enum MessageSender { user, ai }

class ChatMessage {
  final String id;
  final String content;
  final MessageSender sender;
  final DateTime timestamp;
  final bool isLoading;

  const ChatMessage({
    required this.id,
    required this.content,
    required this.sender,
    required this.timestamp,
    this.isLoading = false,
  });

  ChatMessage copyWith({
    String? content,
    bool? isLoading,
  }) =>
      ChatMessage(
        id: id,
        content: content ?? this.content,
        sender: sender,
        timestamp: timestamp,
        isLoading: isLoading ?? this.isLoading,
      );
}
