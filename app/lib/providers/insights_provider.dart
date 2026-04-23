import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/insight.dart';
import '../services/mock_data_service.dart';

final insightsProvider = Provider<List<Insight>>((ref) {
  return MockDataService.getInsights();
});

final filteredInsightsProvider =
    Provider.family<List<Insight>, InsightType?>((ref, type) {
  final insights = ref.watch(insightsProvider);
  if (type == null) return insights;
  return insights.where((i) => i.type == type).toList();
});
