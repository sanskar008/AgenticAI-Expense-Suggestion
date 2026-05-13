import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/goal.dart';
import '../providers/goals_provider.dart';
import '../utils/app_colors.dart';
import '../utils/formatters.dart';

class GoalsScreen extends ConsumerWidget {
  const GoalsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final goals = ref.watch(goalsProvider);
    final totalSaved = ref.watch(totalSavedProvider);
    final totalTarget = ref.watch(totalTargetProvider);

    return Scaffold(
      backgroundColor: AppColors.bg,
      appBar: AppBar(
        title: const Text('Goals'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add_rounded),
            onPressed: () => _showAddGoalSheet(context, ref),
            tooltip: 'Add Goal',
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 100),
        children: [
          // ── Summary ──────────────────────────────────────────────
          _GoalsSummaryCard(totalSaved: totalSaved, totalTarget: totalTarget)
              .animate()
              .fadeIn(duration: 400.ms)
              .slideY(begin: 0.2, end: 0, duration: 400.ms),

          const SizedBox(height: 24),

          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Your Goals',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textPrimary,
                ),
              ),
              Text(
                '${goals.length} goals',
                style: const TextStyle(
                  fontSize: 12,
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),

          const SizedBox(height: 12),

          if (goals.isEmpty)
            _EmptyGoals(onAdd: () => _showAddGoalSheet(context, ref))
          else
            ...goals.asMap().entries.map((e) => Padding(
                  padding: const EdgeInsets.only(bottom: 14),
                  child: _GoalCard(
                    goal: e.value,
                    onAddSavings: (amount) =>
                        ref.read(goalsProvider.notifier).addSavings(e.value.id, amount),
                    onDelete: () =>
                        ref.read(goalsProvider.notifier).removeGoal(e.value.id),
                  )
                      .animate(delay: Duration(milliseconds: 60 * e.key))
                      .fadeIn(duration: 300.ms)
                      .slideY(begin: 0.1, end: 0, duration: 300.ms),
                )),
        ],
      ),
    );
  }

  void _showAddGoalSheet(BuildContext context, WidgetRef ref) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppColors.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (_) => _AddGoalSheet(
        onAdd: (name, target, date, emoji) => 
            ref.read(goalsProvider.notifier).addGoal(name, target, date, emoji),
      ),
    );
  }
}

class _GoalsSummaryCard extends StatelessWidget {
  final double totalSaved;
  final double totalTarget;

  const _GoalsSummaryCard({required this.totalSaved, required this.totalTarget});

  @override
  Widget build(BuildContext context) {
    final pct = totalTarget > 0 ? (totalSaved / totalTarget).clamp(0.0, 1.0) : 0.0;

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: AppColors.greenGradient,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: AppColors.success.withOpacity(0.35),
            blurRadius: 24,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Total Savings Progress',
            style: TextStyle(fontSize: 13, color: Colors.white70),
          ),
          const SizedBox(height: 8),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                Formatters.currency(totalSaved),
                style: const TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.w800,
                  color: Colors.white,
                  letterSpacing: -1,
                ),
              ),
              Text(
                ' / ${Formatters.currency(totalTarget)}',
                style: const TextStyle(
                  fontSize: 16,
                  color: Colors.white70,
                  fontWeight: FontWeight.w500,
                ),
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
            '🎯 ${Formatters.percent(pct)} of total target reached',
            style: const TextStyle(
              fontSize: 12,
              color: Colors.white,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}

class _GoalCard extends StatelessWidget {
  final Goal goal;
  final ValueChanged<double> onAddSavings;
  final VoidCallback onDelete;

  const _GoalCard({
    required this.goal,
    required this.onAddSavings,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final pct = goal.progress;
    final color = pct >= 1.0 ? AppColors.success : AppColors.primary;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: goal.isCompleted ? AppColors.success.withOpacity(0.4) : AppColors.border,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(goal.emoji, style: const TextStyle(fontSize: 28)),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      goal.title,
                      style: const TextStyle(
                        fontWeight: FontWeight.w700,
                        fontSize: 16,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 3),
                    Text(
                      goal.isCompleted
                          ? '🎉 Goal Achieved!'
                          : '${goal.daysLeft} days left',
                      style: TextStyle(
                        fontSize: 12,
                        color: goal.isCompleted ? AppColors.success : AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              // Circular progress indicator
              SizedBox(
                width: 52,
                height: 52,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    CircularProgressIndicator(
                      value: pct,
                      backgroundColor: color.withOpacity(0.15),
                      valueColor: AlwaysStoppedAnimation<Color>(color),
                      strokeWidth: 5,
                    ),
                    Text(
                      '${(pct * 100).toStringAsFixed(0)}%',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w700,
                        color: color,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Progress details
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _StatChip(
                label: 'Saved',
                value: Formatters.currency(goal.savedAmount),
                color: AppColors.success,
              ),
              _StatChip(
                label: 'Target',
                value: Formatters.currency(goal.targetAmount),
                color: AppColors.primary,
              ),
              _StatChip(
                label: 'Weekly',
                value: Formatters.currency(goal.weeklySavingsNeeded),
                color: AppColors.warning,
              ),
            ],
          ),

          const SizedBox(height: 12),

          // Progress bar
          ClipRRect(
            borderRadius: BorderRadius.circular(6),
            child: LinearProgressIndicator(
              value: pct,
              backgroundColor: color.withOpacity(0.1),
              valueColor: AlwaysStoppedAnimation<Color>(color),
              minHeight: 8,
            ),
          ),

          const SizedBox(height: 14),

          // Action buttons
          if (!goal.isCompleted)
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _showAddSavingsDialog(context),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppColors.success,
                      side: const BorderSide(color: AppColors.success),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    icon: const Icon(Icons.add_rounded, size: 16),
                    label: const Text('Add Savings',
                        style: TextStyle(fontSize: 12)),
                  ),
                ),
                const SizedBox(width: 10),
                IconButton(
                  onPressed: onDelete,
                  icon: const Icon(Icons.delete_outline_rounded,
                      color: AppColors.textDisabled, size: 20),
                  style: IconButton.styleFrom(
                    backgroundColor: AppColors.error.withOpacity(0.1),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                ),
              ],
            )
          else
            Container(
              alignment: Alignment.center,
              padding: const EdgeInsets.symmetric(vertical: 8),
              decoration: BoxDecoration(
                color: AppColors.success.withOpacity(0.1),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: AppColors.success.withOpacity(0.3)),
              ),
              child: const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.check_circle_rounded,
                      color: AppColors.success, size: 16),
                  SizedBox(width: 6),
                  Text(
                    'Goal Achieved! 🎉',
                    style: TextStyle(
                      color: AppColors.success,
                      fontWeight: FontWeight.w600,
                      fontSize: 13,
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  void _showAddSavingsDialog(BuildContext context) {
    final ctrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('Add Savings – ${goal.title}'),
        content: TextField(
          controller: ctrl,
          autofocus: true,
          keyboardType: TextInputType.number,
          inputFormatters: [FilteringTextInputFormatter.digitsOnly],
          decoration: const InputDecoration(
            prefixText: '₹ ',
            hintText: 'Amount',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              final amount = double.tryParse(ctrl.text);
              if (amount != null && amount > 0) {
                onAddSavings(amount);
                Navigator.pop(ctx);
              }
            },
            child: const Text('Add'),
          ),
        ],
      ),
    );
  }
}

class _StatChip extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const _StatChip({required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Text(label,
            style: const TextStyle(
                fontSize: 10, color: AppColors.textDisabled)),
        const SizedBox(height: 3),
        Text(value,
            style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w700,
                color: color)),
      ],
    );
  }
}

class _EmptyGoals extends StatelessWidget {
  final VoidCallback onAdd;
  const _EmptyGoals({required this.onAdd});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 40),
        child: Column(
          children: [
            const Icon(Icons.track_changes_rounded,
                size: 72, color: AppColors.textDisabled),
            const SizedBox(height: 16),
            const Text(
              'No goals yet',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Set a savings goal to stay motivated!',
              style: TextStyle(fontSize: 13, color: AppColors.textDisabled),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: onAdd,
              icon: const Icon(Icons.add_rounded),
              label: const Text('Add First Goal'),
            ),
          ],
        ),
      ),
    );
  }
}

class _AddGoalSheet extends StatefulWidget {
  final Function(String, double, DateTime, String) onAdd;
  const _AddGoalSheet({required this.onAdd});

  @override
  State<_AddGoalSheet> createState() => _AddGoalSheetState();
}

class _AddGoalSheetState extends State<_AddGoalSheet> {
  final _formKey = GlobalKey<FormState>();
  final _titleCtrl = TextEditingController();
  final _targetCtrl = TextEditingController();
  String _selectedEmoji = '🎯';
  DateTime _deadline = DateTime.now().add(const Duration(days: 90));

  final _emojis = ['🎯', '📱', '🏖️', '🛡️', '🚗', '🏠', '✈️', '💍', '📚', '💻'];

  @override
  void dispose() {
    _titleCtrl.dispose();
    _targetCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom,
        left: 20,
        right: 20,
        top: 20,
      ),
      child: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'New Savings Goal',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 20),

            // Emoji selector
            SizedBox(
              height: 48,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                itemCount: _emojis.length,
                itemBuilder: (_, i) => GestureDetector(
                  onTap: () => setState(() => _selectedEmoji = _emojis[i]),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    margin: const EdgeInsets.only(right: 8),
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: _selectedEmoji == _emojis[i]
                          ? AppColors.primary.withOpacity(0.2)
                          : AppColors.surfaceLight,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: _selectedEmoji == _emojis[i]
                            ? AppColors.primary
                            : Colors.transparent,
                      ),
                    ),
                    alignment: Alignment.center,
                    child: Text(_emojis[i], style: const TextStyle(fontSize: 22)),
                  ),
                ),
              ),
            ),

            const SizedBox(height: 16),

            TextFormField(
              controller: _titleCtrl,
              textCapitalization: TextCapitalization.sentences,
              decoration: const InputDecoration(hintText: 'Goal name (e.g. Goa Trip)'),
              validator: (v) => (v == null || v.trim().isEmpty) ? 'Enter a name' : null,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _targetCtrl,
              keyboardType: TextInputType.number,
              inputFormatters: [FilteringTextInputFormatter.digitsOnly],
              decoration: const InputDecoration(
                prefixText: '₹ ',
                hintText: 'Target amount',
              ),
              validator: (v) {
                if (v == null || v.isEmpty) return 'Enter amount';
                if ((double.tryParse(v) ?? 0) <= 0) return 'Invalid amount';
                return null;
              },
            ),
            const SizedBox(height: 12),
            GestureDetector(
              onTap: () async {
                final d = await showDatePicker(
                  context: context,
                  initialDate: _deadline,
                  firstDate: DateTime.now().add(const Duration(days: 1)),
                  lastDate: DateTime.now().add(const Duration(days: 1825)),
                  builder: (context, child) => Theme(
                    data: Theme.of(context).copyWith(
                      colorScheme: const ColorScheme.dark(
                        primary: AppColors.primary,
                        surface: AppColors.surface,
                      ),
                    ),
                    child: child!,
                  ),
                );
                if (d != null) setState(() => _deadline = d);
              },
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                decoration: BoxDecoration(
                  color: AppColors.surfaceLight,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: AppColors.border),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.calendar_today_rounded,
                        size: 18, color: AppColors.textSecondary),
                    const SizedBox(width: 12),
                    Text(
                      'Deadline: ${_deadline.day}/${_deadline.month}/${_deadline.year}',
                      style: const TextStyle(
                          color: AppColors.textPrimary, fontSize: 14),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: () {
                  if (_formKey.currentState!.validate()) {
                    widget.onAdd(
                      _titleCtrl.text.trim(),
                      double.parse(_targetCtrl.text),
                      _deadline,
                      _selectedEmoji,
                    );
                    Navigator.pop(context);
                  }
                },
                child: const Text('Create Goal'),
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}
