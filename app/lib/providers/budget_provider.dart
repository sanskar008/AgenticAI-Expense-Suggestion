import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/budget.dart';
import '../models/expense.dart';
import '../services/api_service.dart';
import 'expense_provider.dart';

class BudgetNotifier extends StateNotifier<List<Budget>> {
  BudgetNotifier() : super([]) {
    fetchBudgets();
  }

  Future<void> fetchBudgets() async {
    try {
      final res = await ApiService.getBudgets();
      if (res['success'] == true) {
        final List<dynamic> budgetsJson = res['budgets'];
        state = budgetsJson.map((b) => Budget.fromJson(b)).toList();
      }
    } catch (e) {
      print('Error fetching budgets: $e');
    }
  }

  Future<void> updateBudgetLimit(ExpenseCategory category, double amount) async {
    try {
      final res = await ApiService.setBudget(category.displayName, amount);
      if (res['success'] == true) {
        fetchBudgets();
      }
    } catch (e) {
      print('Error updating budget: $e');
    }
  }

  void syncWithExpenses(Map<ExpenseCategory, double> spending) {
    state = [
      for (final b in state)
        b.copyWith(spent: spending[b.category] ?? 0),
    ];
  }
}

final budgetProvider =
    StateNotifierProvider<BudgetNotifier, List<Budget>>((ref) {
  final notifier = BudgetNotifier();
  ref.listen<Map<ExpenseCategory, double>>(categorySpendingProvider, (_, map) {
    notifier.syncWithExpenses(map);
  });
  return notifier;
});

final totalBudgetProvider = Provider<double>((ref) {
  final budgets = ref.watch(budgetProvider);
  return budgets.fold(0.0, (sum, b) => sum + b.limit);
});

final totalSpentBudgetProvider = Provider<double>((ref) {
  final budgets = ref.watch(budgetProvider);
  return budgets.fold(0.0, (sum, b) => sum + b.spent);
});
