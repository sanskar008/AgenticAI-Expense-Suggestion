import 'package:intl/intl.dart';

class Formatters {
  static final _inr = NumberFormat.currency(
    locale: 'en_IN',
    symbol: '₹',
    decimalDigits: 0,
  );

  static final _compact = NumberFormat.compact(locale: 'en_IN');

  static String currency(double amount) => _inr.format(amount);

  static String compactAmount(double amount) {
    if (amount >= 1000) return '₹${_compact.format(amount)}';
    return '₹${amount.toStringAsFixed(0)}';
  }

  static String date(DateTime d) => DateFormat('dd MMM yyyy').format(d);
  static String shortDate(DateTime d) => DateFormat('dd MMM').format(d);
  static String monthYear(DateTime d) => DateFormat('MMMM yyyy').format(d);
  static String monthShort(DateTime d) => DateFormat('MMM').format(d);

  static String relativeDate(DateTime d) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final target = DateTime(d.year, d.month, d.day);
    final diff = today.difference(target).inDays;
    if (diff == 0) return 'Today';
    if (diff == 1) return 'Yesterday';
    if (diff < 7) return '$diff days ago';
    return shortDate(d);
  }

  static String percent(double value) => '${(value * 100).toStringAsFixed(0)}%';
}
