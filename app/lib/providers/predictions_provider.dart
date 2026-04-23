import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/prediction.dart';
import '../services/mock_data_service.dart';

final monthlyPredictionsProvider = Provider<List<MonthlyPrediction>>((ref) {
  return MockDataService.getMonthlyPredictions();
});

final categoryPredictionsProvider = Provider<List<CategoryPrediction>>((ref) {
  return MockDataService.getCategoryPredictions();
});
