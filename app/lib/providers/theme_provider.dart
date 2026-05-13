import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';

class ThemeNotifier extends StateNotifier<bool> {
  ThemeNotifier() : super(true) {
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    try {
      final res = await ApiService.getSettings();
      if (res['success'] == true && res['settings'] != null) {
        state = res['settings']['dark_mode'] == 1;
      }
    } catch (e) {
      print('Error loading theme settings: $e');
    }
  }

  Future<void> toggleTheme(bool isDark) async {
    state = isDark;
    try {
      await ApiService.updateSettings({'dark_mode': isDark ? 1 : 0});
    } catch (e) {
      print('Error saving theme settings: $e');
    }
  }
}

final themeProvider = StateNotifierProvider<ThemeNotifier, bool>((ref) {
  return ThemeNotifier();
});
