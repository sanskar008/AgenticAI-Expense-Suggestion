import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/insight.dart';
import '../services/mock_data_service.dart';

import '../services/api_service.dart';

class InsightsNotifier extends StateNotifier<List<Insight>> {
  InsightsNotifier() : super([]) {
    fetchInsights();
  }

  Future<void> fetchInsights() async {
    try {
      final res = await ApiService.getInsights();
      if (res['success'] == true) {
        final List<dynamic> insightsJson = res['insights'];
        state = insightsJson.map((i) => Insight.fromJson(i)).toList();
      }
    } catch (e) {
      print('Error fetching insights: $e');
    }
  }
}

final insightsProvider = StateNotifierProvider<InsightsNotifier, List<Insight>>((ref) {
  return InsightsNotifier();
});

final filteredInsightsProvider =
    Provider.family<List<Insight>, InsightType?>((ref, type) {
  final insights = ref.watch(insightsProvider);
  if (type == null) return insights;
  return insights.where((i) => i.type == type).toList();
});
