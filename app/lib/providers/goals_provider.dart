import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/goal.dart';
import '../services/api_service.dart';

class GoalsNotifier extends StateNotifier<List<Goal>> {
  GoalsNotifier() : super([]) {
    fetchGoals();
  }

  Future<void> fetchGoals() async {
    try {
      final res = await ApiService.getGoals();
      if (res['success'] == true && res['goals'] != null) {
        final List<dynamic> goalsJson = res['goals'];
        state = goalsJson.map((g) => Goal.fromJson(g)).toList();
      }
    } catch (e) {
      print('Error fetching goals: $e');
    }
  }

  void addGoal(Goal goal) {
    // Ideally call API here
    state = [goal, ...state];
  }

  void removeGoal(String id) {
    state = state.where((g) => g.id != id).toList();
  }

  void addSavings(String id, double amount) {
    state = [
      for (final g in state)
        if (g.id == id)
          g.copyWith(savedAmount: (g.savedAmount + amount).clamp(0, g.targetAmount))
        else
          g,
    ];
  }
}

final goalsProvider =
    StateNotifierProvider<GoalsNotifier, List<Goal>>(
  (ref) => GoalsNotifier(),
);

final totalSavedProvider = Provider<double>((ref) {
  final goals = ref.watch(goalsProvider);
  return goals.fold(0.0, (sum, g) => sum + g.savedAmount);
});

final totalTargetProvider = Provider<double>((ref) {
  final goals = ref.watch(goalsProvider);
  return goals.fold(0.0, (sum, g) => sum + g.targetAmount);
});
