import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/prediction.dart';
import '../services/api_service.dart';

class PredictionsNotifier extends StateNotifier<Map<String, dynamic>> {
  PredictionsNotifier() : super({'predicted_total': 0.0, 'category_forecast': {}, 'confidence': 'low'}) {
    fetchPredictions();
  }

  Future<void> fetchPredictions() async {
    try {
      final res = await ApiService.getPredictions();
      if (res['success'] == true && res['prediction'] != null) {
        state = res['prediction'];
      }
    } catch (e) {
      print('Error fetching predictions: $e');
    }
  }
}

final predictionsProvider = StateNotifierProvider<PredictionsNotifier, Map<String, dynamic>>((ref) {
  return PredictionsNotifier();
});

final monthlyPredictionsProvider = Provider<List<MonthlyPrediction>>((ref) {
  final data = ref.watch(predictionsProvider);
  final predictedTotal = (data['predicted_total'] as num?)?.toDouble() ?? 0.0;
  
  // For the chart, we'll show the current month with the predicted value
  return [
    MonthlyPrediction(
      month: DateTime.now(),
      predicted: predictedTotal,
      actual: null, // You could fetch actual from expense_provider if needed
    )
  ];
});

final categoryPredictionsProvider = Provider<List<CategoryPrediction>>((ref) {
  final data = ref.watch(predictionsProvider);
  final forecasts = data['category_forecast'] as Map<String, dynamic>? ?? {};
  
  return forecasts.entries.map((e) {
    final predictedValue = (e.value as num).toDouble();
    // In a real app, you'd compare with actual spending
    return CategoryPrediction(
      category: e.key,
      currentSpending: predictedValue * 0.8, // Dummy current for comparison
      predictedSpending: predictedValue,
      changePercent: 5.0, // Dummy change
    );
  }).toList();
});
