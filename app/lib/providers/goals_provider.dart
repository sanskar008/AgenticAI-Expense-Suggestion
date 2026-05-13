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

  Future<void> addGoal(String name, double targetAmount, DateTime deadline, String emoji) async {
    try {
      final res = await ApiService.createGoal({
        'name': name,
        'target_amount': targetAmount,
        'target_date': deadline.toIso8601String(),
        'emoji': emoji,
      });
      if (res['success'] == true) {
        fetchGoals();
      }
    } catch (e) {
      print('Error creating goal: $e');
    }
  }

  Future<void> removeGoal(String id) async {
    // Backend doesn't have a specific goal delete endpoint yet, 
    // but we can update local state for now.
    state = state.where((g) => g.id != id).toList();
  }

  Future<void> addSavings(String id, double amount) async {
    try {
      final intId = int.tryParse(id);
      if (intId != null) {
        final res = await ApiService.addGoalSavings(intId, amount);
        if (res['success'] == true) {
          fetchGoals();
        }
      }
    } catch (e) {
      print('Error adding savings: $e');
    }
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
