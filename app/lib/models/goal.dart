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

  Goal copyWith({
    String? id,
    String? title,
    String? emoji,
    double? targetAmount,
    double? savedAmount,
    DateTime? deadline,
  }) => Goal(
        id: id ?? this.id,
        title: title ?? this.title,
        emoji: emoji ?? this.emoji,
        targetAmount: targetAmount ?? this.targetAmount,
        savedAmount: savedAmount ?? this.savedAmount,
        deadline: deadline ?? this.deadline,
      );

  factory Goal.fromJson(Map<String, dynamic> json) {
    return Goal(
      id: json['id']?.toString() ?? '',
      title: json['name'] ?? json['title'] ?? 'Unnamed Goal',
      emoji: json['emoji'] ?? '💰', // Default emoji
      targetAmount: (json['target_amount'] ?? json['targetAmount'] as num).toDouble(),
      savedAmount: (json['current_amount'] ?? json['savedAmount'] ?? 0 as num).toDouble(),
      deadline: DateTime.parse(json['target_date'] ?? json['deadline'] ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': title,
      'emoji': emoji,
      'target_amount': targetAmount,
      'current_amount': savedAmount,
      'target_date': deadline.toIso8601String(),
    };
  }
}
