class Goal {
  final String id;
  final String title;
  final String emoji;
  final double targetAmount;
  final double savedAmount;
  final DateTime deadline;

  const Goal({
    required this.id,
    required this.title,
    required this.emoji,
    required this.targetAmount,
    required this.savedAmount,
    required this.deadline,
  });

  double get progress => (savedAmount / targetAmount).clamp(0.0, 1.0);
  int get daysLeft => deadline.difference(DateTime.now()).inDays.clamp(0, 9999);
  double get weeksLeft => daysLeft / 7;
  double get weeklySavingsNeeded {
    final remaining = targetAmount - savedAmount;
    if (remaining <= 0 || weeksLeft <= 0) return 0;
    return remaining / weeksLeft;
  }

  bool get isCompleted => savedAmount >= targetAmount;
  double get remainingAmount => (targetAmount - savedAmount).clamp(0.0, double.infinity);

  Goal copyWith({double? savedAmount}) => Goal(
        id: id,
        title: title,
        emoji: emoji,
        targetAmount: targetAmount,
        savedAmount: savedAmount ?? this.savedAmount,
        deadline: deadline,
      );
}
