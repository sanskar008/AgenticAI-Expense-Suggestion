import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/expense.dart';
import '../services/mock_data_service.dart';
import '../services/api_service.dart';

class ExpenseNotifier extends StateNotifier<List<Expense>> {
  ExpenseNotifier() : super([]) {
    fetchExpenses();
  }

  Future<void> fetchExpenses() async {
    try {
      final res = await ApiService.getExpenses();
      if (res['success'] == true) {
        final List<dynamic> expensesJson = res['expenses'];
        state = expensesJson.map((e) => Expense.fromJson(e)).toList();
      }
    } catch (e) {
      print('Error fetching expenses: $e');
    }
  }

  Future<void> addExpense(Expense expense) async {
    try {
      final res = await ApiService.addExpenses([expense.toJson()]);
      if (res['success'] == true) {
        // Refresh or just update local state
        fetchExpenses();
      }
    } catch (e) {
      print('Error adding expense: $e');
      // Optimistic update fallback or error handling
    }
  }

  void removeExpense(String id) {
    // Implement delete API call if needed
    state = state.where((e) => e.id != id).toList();
  }
}

final expenseProvider =
    StateNotifierProvider<ExpenseNotifier, List<Expense>>(
  (ref) => ExpenseNotifier(),
);

// ── Derived providers ──────────────────────────────────────────────────────

final currentMonthExpensesProvider = Provider<List<Expense>>((ref) {
  final expenses = ref.watch(expenseProvider);
  final now = DateTime.now();
  return expenses
      .where((e) => e.date.month == now.month && e.date.year == now.year)
      .toList()
    ..sort((a, b) => b.date.compareTo(a.date));
});

final totalSpendingProvider = Provider<double>((ref) {
  final expenses = ref.watch(currentMonthExpensesProvider);
  return expenses.fold(0.0, (sum, e) => sum + e.amount);
});

final categorySpendingProvider = Provider<Map<ExpenseCategory, double>>((ref) {
  final expenses = ref.watch(currentMonthExpensesProvider);
  final map = <ExpenseCategory, double>{};
  for (final e in expenses) {
    map[e.category] = (map[e.category] ?? 0) + e.amount;
  }
  return map;
});

final recentExpensesProvider = Provider<List<Expense>>((ref) {
  final expenses = ref.watch(expenseProvider);
  final sorted = [...expenses]..sort((a, b) => b.date.compareTo(a.date));
  return sorted.take(8).toList();
});

final filteredExpensesProvider =
    Provider.family<List<Expense>, ExpenseCategory?>((ref, category) {
  final expenses = ref.watch(expenseProvider);
  final sorted = [...expenses]..sort((a, b) => b.date.compareTo(a.date));
  if (category == null) return sorted;
  return sorted.where((e) => e.category == category).toList();
});
