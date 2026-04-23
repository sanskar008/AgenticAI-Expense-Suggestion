class MonthlyPrediction {
  final DateTime month;
  final double predicted;
  final double? actual;

  const MonthlyPrediction({
    required this.month,
    required this.predicted,
    this.actual,
  });

  bool get hasActual => actual != null;
}

class CategoryPrediction {
  final String category;
  final double currentSpending;
  final double predictedSpending;
  final double changePercent;

  const CategoryPrediction({
    required this.category,
    required this.currentSpending,
    required this.predictedSpending,
    required this.changePercent,
  });

  bool get isIncreasing => changePercent > 0;
}
