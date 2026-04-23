import 'package:flutter/material.dart';

enum InsightType { alert, tip, trend, info }

class Insight {
  final String id;
  final String title;
  final String description;
  final InsightType type;
  final String? category;
  final double? changePercent;

  const Insight({
    required this.id,
    required this.title,
    required this.description,
    required this.type,
    this.category,
    this.changePercent,
  });

  IconData get icon {
    switch (type) {
      case InsightType.alert:
        return Icons.warning_rounded;
      case InsightType.tip:
        return Icons.lightbulb_rounded;
      case InsightType.trend:
        return Icons.trending_up_rounded;
      case InsightType.info:
        return Icons.info_rounded;
    }
  }

  Color get color {
    switch (type) {
      case InsightType.alert:
        return const Color(0xFFFF6B6B);
      case InsightType.tip:
        return const Color(0xFFFFD93D);
      case InsightType.trend:
        return const Color(0xFF6C5CE7);
      case InsightType.info:
        return const Color(0xFF74B9FF);
    }
  }
}
