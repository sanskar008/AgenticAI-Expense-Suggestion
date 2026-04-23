import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/budget.dart';
import '../models/expense.dart';
import '../services/mock_data_service.dart';
import 'expense_provider.dart';

class BudgetNotifier extends StateNotifier<List<Budget>> {
  BudgetNotifier() : super(MockDataService.getBudgets());

  void syncWithExpenses(Map<ExpenseCategory, double> spending) {
    state = [
      for (final b in state)
        b.copyWith(spent: spending[b.category] ?? 0),
    ];
  }

  void addToSpent(ExpenseCategory category, double amount) {
    state = [
      for (final b in state)
        if (b.category == category)
          b.copyWith(spent: b.spent + amount)
        else
          b,
    ];
  }

  void updateSpent(ExpenseCategory category, double amount) => addToSpent(category, amount);
}

final budgetProvider =
    StateNotifierProvider<BudgetNotifier, List<Budget>>((ref) {
  final notifier = BudgetNotifier();
  // Keep budgets in sync with the expense list's monthly totals
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
