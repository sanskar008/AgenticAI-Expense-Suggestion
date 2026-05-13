import 'package:flutter/material.dart';
import '../models/budget.dart';
import '../utils/app_colors.dart';
import '../utils/formatters.dart';
import 'category_icon.dart';

class BudgetProgressCard extends StatelessWidget {
  final Budget budget;
  final VoidCallback? onTap;

  const BudgetProgressCard({super.key, required this.budget, this.onTap});

  Color get _barColor {
    final pct = budget.percentageClamped;
    if (pct >= 1.0) return AppColors.error;
    if (pct >= 0.8) return AppColors.warning;
    return AppColors.success;
  }

  @override
  Widget build(BuildContext context) {
    final pct = budget.percentageClamped;
    final isOver = budget.isOverBudget;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isOver ? AppColors.error.withOpacity(0.4) : AppColors.border,
          ),
        ),
        child: Column(
          children: [
            Row(
              children: [
                CategoryIcon(category: budget.category, size: 40),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            budget.category.displayName,
                            style: const TextStyle(
                              fontWeight: FontWeight.w600,
                              fontSize: 14,
                              color: AppColors.textPrimary,
                            ),
                          ),
                          const Spacer(),
                          if (isOver)
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: AppColors.error.withOpacity(0.15),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: const Text(
                                'OVER',
                                style: TextStyle(
                                  fontSize: 9,
                                  color: AppColors.error,
                                  fontWeight: FontWeight.w700,
                                  letterSpacing: 0.5,
                                ),
                              ),
                            ),
                        ],
                      ),
                      const SizedBox(height: 2),
                      Text(
                        isOver
                            ? '${Formatters.currency(budget.spent)} / ${Formatters.currency(budget.limit)} — ₹${budget.overAmount.toStringAsFixed(0)} over'
                            : '${Formatters.currency(budget.spent)} / ${Formatters.currency(budget.limit)} remaining: ${Formatters.currency(budget.remaining)}',
                        style: TextStyle(
                          fontSize: 11,
                          color: isOver ? AppColors.error : AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  Formatters.percent(pct),
                  style: TextStyle(
                    fontWeight: FontWeight.w700,
                    fontSize: 13,
                    color: _barColor,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: LinearProgressIndicator(
                value: pct,
                backgroundColor: _barColor.withOpacity(0.12),
                valueColor: AlwaysStoppedAnimation<Color>(_barColor),
                minHeight: 7,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
