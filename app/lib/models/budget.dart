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

  factory Budget.fromJson(Map<String, dynamic> json) {
    return Budget(
      id: json['id']?.toString() ?? '',
      category: _parseCategory(json['category']),
      limit: (json['budget'] as num).toDouble(),
      spent: (json['spent'] as num).toDouble(),
    );
  }

  static ExpenseCategory _parseCategory(String? category) {
    if (category == null) return ExpenseCategory.other;
    final lower = category.toLowerCase();
    for (final cat in ExpenseCategory.values) {
      if (cat.displayName.toLowerCase() == lower) return cat;
    }
    return ExpenseCategory.other;
  }
}
