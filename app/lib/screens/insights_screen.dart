import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../models/insight.dart';
import '../providers/insights_provider.dart';
import '../utils/app_colors.dart';
import '../widgets/insight_card.dart';

class InsightsScreen extends ConsumerStatefulWidget {
  const InsightsScreen({super.key});

  @override
  ConsumerState<InsightsScreen> createState() => _InsightsScreenState();
}

class _InsightsScreenState extends ConsumerState<InsightsScreen> {
  InsightType? _filter;

  @override
  Widget build(BuildContext context) {
    final insights = ref.watch(filteredInsightsProvider(_filter));

    return Scaffold(
      backgroundColor: AppColors.bg,
      appBar: AppBar(
        title: const Text('AI Insights'),
        actions: [
          IconButton(
            icon: const Icon(Icons.chat_bubble_rounded, size: 22),
            onPressed: () => context.push('/chat'),
            tooltip: 'Ask AI',
          ),
          const SizedBox(width: 4),
        ],
      ),
      body: CustomScrollView(
        slivers: [
          // ── Filter Row ─────────────────────────────────────────
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 4, 16, 0),
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    _TypeChip(label: 'All', selected: _filter == null, color: AppColors.primary, onTap: () => setState(() => _filter = null)),
                    const SizedBox(width: 8),
                    _TypeChip(label: '⚠️ Alerts', selected: _filter == InsightType.alert, color: AppColors.error, onTap: () => setState(() => _filter = InsightType.alert)),
                    const SizedBox(width: 8),
                    _TypeChip(label: '💡 Tips', selected: _filter == InsightType.tip, color: AppColors.warning, onTap: () => setState(() => _filter = InsightType.tip)),
                    const SizedBox(width: 8),
                    _TypeChip(label: '📈 Trends', selected: _filter == InsightType.trend, color: AppColors.primary, onTap: () => setState(() => _filter = InsightType.trend)),
                    const SizedBox(width: 8),
                    _TypeChip(label: 'ℹ️ Info', selected: _filter == InsightType.info, color: AppColors.info, onTap: () => setState(() => _filter = InsightType.info)),
                  ],
                ),
              ),
            ),
          ),

          const SliverToBoxAdapter(child: SizedBox(height: 16)),

          // ── AI Chat CTA ────────────────────────────────────────
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: _ChatCTA(onTap: () => context.push('/chat'))
                  .animate()
                  .fadeIn(duration: 400.ms),
            ),
          ),

          const SliverToBoxAdapter(child: SizedBox(height: 16)),

          // ── Insights List ──────────────────────────────────────
          SliverPadding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 100),
            sliver: insights.isEmpty
                ? const SliverFillRemaining(child: _EmptyInsights())
                : SliverList(
                    delegate: SliverChildBuilderDelegate(
                      (context, index) => Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: InsightCard(insight: insights[index])
                            .animate(
                              delay: Duration(milliseconds: 50 * index),
                            )
                            .fadeIn(duration: 300.ms)
                            .slideY(begin: 0.15, end: 0, duration: 300.ms),
                      ),
                      childCount: insights.length,
                    ),
                  ),
          ),
        ],
      ),
    );
  }
}

class _TypeChip extends StatelessWidget {
  final String label;
  final bool selected;
  final Color color;
  final VoidCallback onTap;

  const _TypeChip({
    required this.label,
    required this.selected,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
        decoration: BoxDecoration(
          color: selected ? color.withOpacity(0.18) : AppColors.surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: selected ? color : AppColors.border,
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 12,
            fontWeight: selected ? FontWeight.w600 : FontWeight.w400,
            color: selected ? color : AppColors.textSecondary,
          ),
        ),
      ),
    );
  }
}

class _ChatCTA extends StatelessWidget {
  final VoidCallback onTap;
  const _ChatCTA({required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          gradient: AppColors.primaryGradient,
          borderRadius: BorderRadius.circular(18),
          boxShadow: [
            BoxShadow(
              color: AppColors.primary.withOpacity(0.3),
              blurRadius: 16,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: const Row(
          children: [
            Icon(Icons.smart_toy_rounded, color: Colors.white, size: 32),
            SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Ask your AI Copilot',
                    style: TextStyle(
                      fontWeight: FontWeight.w700,
                      fontSize: 15,
                      color: Colors.white,
                    ),
                  ),
                  SizedBox(height: 3),
                  Text(
                    '"Where did I spend most this month?"',
                    style: TextStyle(fontSize: 12, color: Colors.white70),
                  ),
                ],
              ),
            ),
            Icon(Icons.arrow_forward_ios_rounded, size: 16, color: Colors.white70),
          ],
        ),
      ),
    );
  }
}

class _EmptyInsights extends StatelessWidget {
  const _EmptyInsights();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.auto_graph_rounded, size: 64, color: AppColors.textDisabled),
          SizedBox(height: 16),
          Text(
            'No insights for this filter',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }
}
