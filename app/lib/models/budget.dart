import 'expense.dart';

class Budget {
  final String id;
  final ExpenseCategory category;
  final double limit;
  final double spent;

  const Budget({
    required this.id,
    required this.category,
    required this.limit,
    this.spent = 0,
  });

  double get percentage => limit > 0 ? (spent / limit).clamp(0.0, 2.0) : 0;
  double get percentageClamped => limit > 0 ? (spent / limit).clamp(0.0, 1.0) : 0;
  bool get isOverBudget => spent > limit;
  double get remaining => (limit - spent).clamp(0.0, double.infinity);
  double get overAmount => isOverBudget ? spent - limit : 0;

  Budget copyWith({double? spent}) => Budget(
        id: id,
        category: category,
        limit: limit,
        spent: spent ?? this.spent,
      );
}
