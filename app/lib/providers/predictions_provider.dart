import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/prediction.dart';
import '../services/api_service.dart';

class PredictionsNotifier extends StateNotifier<List<MonthlyPrediction>> {
  PredictionsNotifier() : super([]) {
    fetchPredictions();
  }

  Future<void> fetchPredictions() async {
    try {
      final res = await ApiService.getPredictions();
      if (res['success'] == true && res['prediction'] != null) {
        // Handle parsing based on API response structure
        // This is a placeholder for actual parsing logic
      }
    } catch (e) {
      print('Error fetching predictions: $e');
    }
  }
}

final monthlyPredictionsProvider = StateNotifierProvider<PredictionsNotifier, List<MonthlyPrediction>>((ref) {
  return PredictionsNotifier();
});

// Since the API returns a single object with predictions, we might need to adjust these
final categoryPredictionsProvider = Provider<List<CategoryPrediction>>((ref) {
  // Extract from monthlyPredictionsProvider if available
  return [];
});
