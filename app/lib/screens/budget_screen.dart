import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/budget_provider.dart';
import '../utils/app_colors.dart';
import '../utils/formatters.dart';
import '../widgets/budget_progress_bar.dart';

class BudgetScreen extends ConsumerWidget {
  const BudgetScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final budgets = ref.watch(budgetProvider);
    final totalBudget = ref.watch(totalBudgetProvider);
    final totalSpent = ref.watch(totalSpentBudgetProvider);

    return Scaffold(
      backgroundColor: AppColors.bg,
      appBar: AppBar(title: const Text('Budget')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 100),
        children: [
          // ── Header Summary Card ──────────────────────────────────
          _BudgetSummaryCard(totalBudget: totalBudget, totalSpent: totalSpent)
              .animate()
              .fadeIn(duration: 400.ms)
              .slideY(begin: 0.2, end: 0, duration: 400.ms),

          const SizedBox(height: 24),

          const Text(
            'Category Budgets',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w700,
              color: AppColors.textPrimary,
            ),
          ),

          const SizedBox(height: 12),

          // ── Budget Items ─────────────────────────────────────────
          ...budgets.asMap().entries.map((e) => Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: BudgetProgressCard(budget: e.value)
                    .animate(delay: Duration(milliseconds: 50 * e.key))
                    .fadeIn(duration: 300.ms)
                    .slideX(begin: 0.1, end: 0, duration: 300.ms),
              )),

          const SizedBox(height: 16),

          // ── Tips Card ────────────────────────────────────────────
          _TipsCard(),
        ],
      ),
    );
  }
}

class _BudgetSummaryCard extends StatelessWidget {
  final double totalBudget;
  final double totalSpent;

  const _BudgetSummaryCard({required this.totalBudget, required this.totalSpent});

  @override
  Widget build(BuildContext context) {
    final pct = totalBudget > 0 ? (totalSpent / totalBudget).clamp(0.0, 1.0) : 0.0;
    final remaining = (totalBudget - totalSpent).clamp(0.0, double.infinity);
    final isOver = totalSpent > totalBudget;

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: isOver
            ? LinearGradient(
                colors: [
                  AppColors.error.withOpacity(0.8),
                  AppColors.error.withOpacity(0.4)
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              )
            : AppColors.primaryGradient,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: (isOver ? AppColors.error : AppColors.primary).withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Total Budget',
                    style: TextStyle(fontSize: 12, color: Colors.white70),
                  ),
                  Text(
                    Formatters.currency(totalBudget),
                    style: const TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.w800,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
              const Spacer(),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  const Text(
                    'Spent',
                    style: TextStyle(fontSize: 12, color: Colors.white70),
                  ),
                  Text(
                    Formatters.currency(totalSpent),
                    style: const TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.w700,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 16),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: pct,
              backgroundColor: Colors.white.withOpacity(0.2),
              valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
              minHeight: 9,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            isOver
                ? '⚠️ Over budget by ${Formatters.currency(totalSpent - totalBudget)}'
                : '✅ ${Formatters.currency(remaining)} remaining (${Formatters.percent(1 - pct)})',
            style: const TextStyle(fontSize: 12, color: Colors.white, fontWeight: FontWeight.w500),
          ),
        ],
      ),
    );
  }
}

class _TipsCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppColors.primary.withOpacity(0.08),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.primary.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.lightbulb_rounded, color: AppColors.warning, size: 18),
              SizedBox(width: 8),
              Text(
                'Budget Tips',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                  color: AppColors.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ...[
            '🛍️ Shopping is over budget — pause non-essential purchases',
            '📋 Bills are at 90% — be cautious this week',
            '💊 Health costs are high — check for generic alternatives',
          ].map(
            (tip) => Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: Text(
                tip,
                style: const TextStyle(
                  fontSize: 12,
                  color: AppColors.textSecondary,
                  height: 1.4,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
