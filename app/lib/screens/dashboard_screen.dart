import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../models/expense.dart';
import '../providers/budget_provider.dart';
import '../providers/expense_provider.dart';
import '../providers/insights_provider.dart';
import '../utils/app_colors.dart';
import '../utils/formatters.dart';
import '../widgets/expense_tile.dart';
import '../widgets/insight_card.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final total = ref.watch(totalSpendingProvider);
    final totalBudget = ref.watch(totalBudgetProvider);
    final recentExpenses = ref.watch(recentExpensesProvider);
    final categorySpending = ref.watch(categorySpendingProvider);
    final insights = ref.watch(insightsProvider);
    final topInsight = insights.isNotEmpty ? insights.first : null;

    return Scaffold(
      backgroundColor: AppColors.bg,
      body: CustomScrollView(
        slivers: [
          // ── App Bar ─────────────────────────────────────────────
          SliverAppBar(
            backgroundColor: AppColors.bg,
            floating: true,
            pinned: false,
            elevation: 0,
            title: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Good ${_greeting()}, Sanskar 👋',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  Formatters.monthYear(DateTime.now()),
                  style: const TextStyle(
                    fontSize: 11,
                    color: AppColors.textSecondary,
                    fontWeight: FontWeight.w400,
                  ),
                ),
              ],
            ),
            actions: [
              IconButton(
                icon: const Icon(Icons.chat_bubble_rounded, size: 22),
                onPressed: () => context.push('/chat'),
                tooltip: 'AI Chat',
              ),
              IconButton(
                icon: const Icon(Icons.notifications_rounded, size: 22),
                onPressed: () {},
                tooltip: 'Notifications',
              ),
              const SizedBox(width: 4),
            ],
          ),

          SliverPadding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                // ── Total Spending Card ──────────────────────────
                _SpendingCard(total: total, totalBudget: totalBudget)
                    .animate()
                    .fadeIn(duration: 400.ms)
                    .slideY(begin: 0.2, end: 0, duration: 400.ms),

                const SizedBox(height: 24),

                // ── Section: Overview ────────────────────────────
                if (categorySpending.isNotEmpty) ...[
                  _SectionHeader(title: "This Month's Overview"),
                  const SizedBox(height: 12),
                  _CategoryPieChart(data: categorySpending)
                      .animate(delay: 100.ms)
                      .fadeIn(duration: 400.ms),
                  const SizedBox(height: 24),
                ],

                // ── Section: AI Insight ──────────────────────────
                if (topInsight != null) ...[
                  _SectionHeader(title: 'AI Insight', trailing: 'See All'),
                  const SizedBox(height: 12),
                  InsightCard(insight: topInsight)
                      .animate(delay: 150.ms)
                      .fadeIn(duration: 400.ms),
                  const SizedBox(height: 24),
                ],

                // ── Section: Recent Transactions ─────────────────
                _SectionHeader(
                  title: 'Recent Transactions',
                  trailing: 'See All',
                  onTrailingTap: () {},
                ),
                const SizedBox(height: 12),

                if (recentExpenses.isEmpty)
                  _EmptyState()
                else
                  ...recentExpenses.take(5).map((e) => ExpenseTile(
                        expense: e,
                        onDelete: () =>
                            ref.read(expenseProvider.notifier).removeExpense(e.id),
                      )),

                const SizedBox(height: 100),
              ]),
            ),
          ),
        ],
      ),
    );
  }

  String _greeting() {
    final h = DateTime.now().hour;
    if (h < 12) return 'Morning';
    if (h < 17) return 'Afternoon';
    return 'Evening';
  }
}

// ── Sub-widgets ────────────────────────────────────────────────────────────

class _SpendingCard extends StatelessWidget {
  final double total;
  final double totalBudget;

  const _SpendingCard({required this.total, required this.totalBudget});

  @override
  Widget build(BuildContext context) {
    final pct = totalBudget > 0 ? (total / totalBudget).clamp(0.0, 1.0) : 0.0;
    final overBudget = total > totalBudget;

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: AppColors.primaryGradient,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withOpacity(0.35),
            blurRadius: 24,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Total Spending',
            style: TextStyle(
              fontSize: 13,
              color: Colors.white70,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            Formatters.currency(total),
            style: const TextStyle(
              fontSize: 36,
              fontWeight: FontWeight.w800,
              color: Colors.white,
              letterSpacing: -1,
            ),
          ),
          const SizedBox(height: 18),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Budget Used',
                          style: TextStyle(
                            fontSize: 11,
                            color: Colors.white.withOpacity(0.7),
                          ),
                        ),
                        Text(
                          '${Formatters.currency(total)} / ${Formatters.currency(totalBudget)}',
                          style: const TextStyle(
                            fontSize: 11,
                            color: Colors.white,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(6),
                      child: LinearProgressIndicator(
                        value: pct,
                        backgroundColor: Colors.white.withOpacity(0.2),
                        valueColor: AlwaysStoppedAnimation<Color>(
                          overBudget ? AppColors.error : Colors.white,
                        ),
                        minHeight: 8,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            overBudget
                ? '⚠️ Over budget by ${Formatters.currency(total - totalBudget)}'
                : '✅ ${Formatters.currency(totalBudget - total)} remaining this month',
            style: TextStyle(
              fontSize: 11,
              color: Colors.white.withOpacity(0.85),
            ),
          ),
        ],
      ),
    );
  }
}

class _CategoryPieChart extends StatefulWidget {
  final Map<ExpenseCategory, double> data;
  const _CategoryPieChart({required this.data});

  @override
  State<_CategoryPieChart> createState() => _CategoryPieChartState();
}

class _CategoryPieChartState extends State<_CategoryPieChart> {
  int _touchedIndex = -1;

  @override
  Widget build(BuildContext context) {
    final total = widget.data.values.fold(0.0, (a, b) => a + b);
    final entries = widget.data.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        children: [
          SizedBox(
            height: 200,
            child: Row(
              children: [
                Expanded(
                  child: PieChart(
                    PieChartData(
                      pieTouchData: PieTouchData(
                        touchCallback: (event, pieTouchResponse) {
                          setState(() {
                            if (!event.isInterestedForInteractions ||
                                pieTouchResponse == null ||
                                pieTouchResponse.touchedSection == null) {
                              _touchedIndex = -1;
                              return;
                            }
                            _touchedIndex = pieTouchResponse
                                .touchedSection!.touchedSectionIndex;
                          });
                        },
                      ),
                      sections: entries.asMap().entries.map((e) {
                        final idx = e.key;
                        final cat = e.value.key;
                        final val = e.value.value;
                        final isTouched = idx == _touchedIndex;
                        final radius = isTouched ? 80.0 : 68.0;
                        final pct = total > 0 ? (val / total * 100) : 0;
                        return PieChartSectionData(
                          value: val,
                          color: cat.color,
                          radius: radius,
                          title: isTouched ? '${pct.toStringAsFixed(1)}%' : '',
                          titleStyle: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                            color: Colors.white,
                          ),
                        );
                      }).toList(),
                      centerSpaceRadius: 44,
                      sectionsSpace: 3,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                // Legend
                Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: entries.take(6).map((entry) {
                    final pct = total > 0 ? entry.value / total * 100 : 0;
                    return Padding(
                      padding: const EdgeInsets.symmetric(vertical: 3),
                      child: Row(
                        children: [
                          Container(
                            width: 10,
                            height: 10,
                            decoration: BoxDecoration(
                              color: entry.key.color,
                              shape: BoxShape.circle,
                            ),
                          ),
                          const SizedBox(width: 7),
                          Text(
                            entry.key.displayName,
                            style: const TextStyle(
                              fontSize: 11,
                              color: AppColors.textSecondary,
                            ),
                          ),
                          const SizedBox(width: 6),
                          Text(
                            '${pct.toStringAsFixed(0)}%',
                            style: const TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                              color: AppColors.textPrimary,
                            ),
                          ),
                        ],
                      ),
                    );
                  }).toList(),
                ),
              ],
            ),
          ),
          const Divider(height: 24),
          // Category amounts row
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: entries.map((entry) => _CatChip(entry: entry)).toList(),
          ),
        ],
      ),
    );
  }
}

class _CatChip extends StatelessWidget {
  final MapEntry<ExpenseCategory, double> entry;
  const _CatChip({required this.entry});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: entry.key.color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: entry.key.color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(entry.key.icon, size: 12, color: entry.key.color),
          const SizedBox(width: 5),
          Text(
            Formatters.currency(entry.value),
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: entry.key.color,
            ),
          ),
        ],
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String title;
  final String? trailing;
  final VoidCallback? onTrailingTap;

  const _SectionHeader({required this.title, this.trailing, this.onTrailingTap});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w700,
            color: AppColors.textPrimary,
          ),
        ),
        if (trailing != null)
          GestureDetector(
            onTap: onTrailingTap,
            child: Text(
              trailing!,
              style: const TextStyle(
                fontSize: 12,
                color: AppColors.primary,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
      ],
    );
  }
}

class _EmptyState extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(32),
      alignment: Alignment.center,
      child: Column(
        children: [
          const Icon(Icons.receipt_long_rounded, size: 48, color: AppColors.textDisabled),
          const SizedBox(height: 12),
          const Text(
            'No expenses yet',
            style: TextStyle(color: AppColors.textSecondary, fontSize: 14),
          ),
          const SizedBox(height: 4),
          const Text(
            'Tap + to add your first expense',
            style: TextStyle(color: AppColors.textDisabled, fontSize: 12),
          ),
        ],
      ),
    );
  }
}
