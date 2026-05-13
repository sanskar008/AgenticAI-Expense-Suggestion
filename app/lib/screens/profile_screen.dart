import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/auth_provider.dart';
import '../providers/expense_provider.dart';
import '../providers/goals_provider.dart';
import '../providers/theme_provider.dart';
import '../services/api_service.dart';
import '../utils/app_colors.dart';
import '../utils/formatters.dart';
import 'package:url_launcher/url_launcher.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isDark = ref.watch(themeProvider);
    final authState = ref.watch(authProvider);
    final user = authState.user;
    
    final total = ref.watch(totalSpendingProvider);
    final totalSaved = ref.watch(totalSavedProvider);
    final expenseCount = ref.watch(currentMonthExpensesProvider).length;

    return Scaffold(
      backgroundColor: AppColors.bg,
      appBar: AppBar(title: const Text('Profile')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 100),
        children: [
          // ── Profile Card ─────────────────────────────────────────
          _ProfileCard(user: user)
              .animate()
              .fadeIn(duration: 400.ms)
              .slideY(begin: 0.2, end: 0, duration: 400.ms),

          const SizedBox(height: 24),

          // ── Stats Row ────────────────────────────────────────────
          Row(
            children: [
              Expanded(
                child: _StatCard(
                  label: 'This Month',
                  value: Formatters.compactAmount(total),
                  icon: Icons.receipt_long_rounded,
                  color: AppColors.error,
                ).animate(delay: 50.ms).fadeIn(duration: 300.ms),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _StatCard(
                  label: 'Total Saved',
                  value: Formatters.compactAmount(totalSaved),
                  icon: Icons.savings_rounded,
                  color: AppColors.success,
                ).animate(delay: 100.ms).fadeIn(duration: 300.ms),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _StatCard(
                  label: 'Expenses',
                  value: '$expenseCount',
                  icon: Icons.list_alt_rounded,
                  color: AppColors.primary,
                ).animate(delay: 150.ms).fadeIn(duration: 300.ms),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // ── Settings ─────────────────────────────────────────────
          const _SectionLabel(label: 'Settings'),
          const SizedBox(height: 8),

          _SettingsTile(
            icon: Icons.dark_mode_rounded,
            iconColor: AppColors.primary,
            title: 'Dark Mode',
            trailing: Switch(
              value: isDark,
              onChanged: (v) => ref.read(themeProvider.notifier).toggleTheme(v),
              activeColor: AppColors.primary,
            ),
          ),

          _SettingsTile(
            icon: Icons.notifications_rounded,
            iconColor: AppColors.warning,
            title: 'Budget Alerts',
            trailing: Switch(
              value: true,
              onChanged: (_) {},
              activeColor: AppColors.primary,
            ),
          ),

          const SizedBox(height: 20),

          const _SectionLabel(label: 'Data & Account'),
          const SizedBox(height: 8),

          _SettingsTile(
            icon: Icons.edit_rounded,
            iconColor: AppColors.primary,
            title: 'Edit Profile',
            subtitle: 'Update your name and email',
            onTap: () => _showEditProfile(context, ref, user),
          ),

          _SettingsTile(
            icon: Icons.download_rounded,
            iconColor: AppColors.info,
            title: 'Export Data (CSV)',
            subtitle: 'Download your expense history',
            onTap: () => _launchUrl(ApiService.exportUrl),
          ),

          _SettingsTile(
            icon: Icons.delete_sweep_rounded,
            iconColor: AppColors.error,
            title: 'Reset Account',
            subtitle: 'Wipe all data from the server',
            onTap: () => _showResetDialog(context, ref),
          ),

          const SizedBox(height: 20),

          const _SectionLabel(label: 'About'),
          const SizedBox(height: 8),

          _SettingsTile(
            icon: Icons.info_rounded,
            iconColor: AppColors.textSecondary,
            title: 'Version',
            subtitle: 'FinTrack AI v1.1.0 (Live Backend)',
          ),

          const SizedBox(height: 24),

          Center(
            child: TextButton(
              onPressed: () => ref.read(authProvider.notifier).logout(),
              child: const Text('LOGOUT', style: TextStyle(color: AppColors.error, fontWeight: FontWeight.bold)),
            ),
          ),
        ],
      ),
    );
  }

  void _launchUrl(String url) async {
    final uri = Uri.parse(url);
    if (!await launchUrl(uri)) {
      debugPrint('Could not launch $url');
    }
  }

  void _showEditProfile(BuildContext context, WidgetRef ref, Map<String, dynamic>? user) {
    final nameController = TextEditingController(text: user?['name'] ?? '');
    final emailController = TextEditingController(text: user?['email'] ?? '');

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Edit Profile'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(controller: nameController, decoration: const InputDecoration(labelText: 'Full Name')),
            TextField(controller: emailController, decoration: const InputDecoration(labelText: 'Email')),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              await ref.read(authProvider.notifier).updateProfile(nameController.text, emailController.text);
              Navigator.pop(ctx);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  void _showResetDialog(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Reset All Data?'),
        content: const Text('This will permanently delete all your expenses, budgets, and goals from the server.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              await ApiService.resetAccount();
              ref.read(authProvider.notifier).logout();
              Navigator.pop(ctx);
            },
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.error),
            child: const Text('Reset Everything'),
          ),
        ],
      ),
    );
  }
}

class _ProfileCard extends StatelessWidget {
  final Map<String, dynamic>? user;
  const _ProfileCard({this.user});

  @override
  Widget build(BuildContext context) {
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
      child: Row(
        children: [
          Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Icon(Icons.person_rounded, color: Colors.white, size: 34),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  user?['name'] ?? 'FinTrack User',
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.w800,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  user?['email'] ?? user?['phone_number'] ?? 'No email set',
                  style: const TextStyle(fontSize: 13, color: Colors.white70),
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '✨ ${user?['membership_status'] ?? 'Free Member'}',
                    style: const TextStyle(
                      fontSize: 11,
                      color: Colors.white,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color color;

  const _StatCard({
    required this.label,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 22),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w800,
              color: color,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: const TextStyle(
              fontSize: 10,
              color: AppColors.textDisabled,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

class _SectionLabel extends StatelessWidget {
  final String label;
  const _SectionLabel({required this.label});

  @override
  Widget build(BuildContext context) {
    return Text(
      label.toUpperCase(),
      style: const TextStyle(
        fontSize: 11,
        fontWeight: FontWeight.w700,
        color: AppColors.textDisabled,
        letterSpacing: 1,
      ),
    );
  }
}

class _SettingsTile extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String title;
  final String? subtitle;
  final Widget? trailing;
  final VoidCallback? onTap;

  const _SettingsTile({
    required this.icon,
    required this.iconColor,
    required this.title,
    this.subtitle,
    this.trailing,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: AppColors.border),
        ),
        child: Row(
          children: [
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: iconColor.withOpacity(0.12),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: iconColor, size: 18),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  if (subtitle != null) ...[
                    const SizedBox(height: 2),
                    Text(
                      subtitle!,
                      style: const TextStyle(
                        fontSize: 11,
                        color: AppColors.textDisabled,
                      ),
                    ),
                  ],
                ],
              ),
            ),
            trailing ??
                (onTap != null
                    ? const Icon(Icons.chevron_right_rounded,
                        color: AppColors.textDisabled, size: 20)
                    : const SizedBox.shrink()),
          ],
        ),
      ),
    );
  }
}
