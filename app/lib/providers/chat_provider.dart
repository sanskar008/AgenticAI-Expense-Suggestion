import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/chat_message.dart';
import '../services/mock_data_service.dart';

class ChatNotifier extends StateNotifier<List<ChatMessage>> {
  ChatNotifier() : super(MockDataService.getInitialMessages());

  int _counter = 100;
  String get _newId => 'msg_${_counter++}';

  Future<void> sendMessage(String content) async {
    if (content.trim().isEmpty) return;

    // Add user message
    final userMsg = ChatMessage(
      id: _newId,
      content: content.trim(),
      sender: MessageSender.user,
      timestamp: DateTime.now(),
    );
    state = [...state, userMsg];

    // Add loading placeholder
    final loadingId = _newId;
    final loadingMsg = ChatMessage(
      id: loadingId,
      content: '',
      sender: MessageSender.ai,
      timestamp: DateTime.now(),
      isLoading: true,
    );
    state = [...state, loadingMsg];

    // Simulate network delay
    await Future.delayed(const Duration(milliseconds: 1200));

    final response = MockDataService.getChatResponse(content);

    state = [
      for (final m in state)
        if (m.id == loadingId)
          m.copyWith(content: response, isLoading: false)
        else
          m,
    ];
  }

  void clearHistory() {
    state = MockDataService.getInitialMessages();
  }
}

final chatProvider =
    StateNotifierProvider<ChatNotifier, List<ChatMessage>>(
  (ref) => ChatNotifier(),
);
