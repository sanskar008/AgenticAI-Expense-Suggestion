import 'package:go_router/go_router.dart';
import '../screens/add_expense_screen.dart';
import '../screens/budget_screen.dart';
import '../screens/chat_screen.dart';
import '../screens/main_navigation_screen.dart';
import '../screens/predictions_screen.dart';
import '../screens/splash_screen.dart';

final appRouter = GoRouter(
  initialLocation: '/splash',
  routes: [
    GoRoute(
      path: '/splash',
      builder: (context, state) => const SplashScreen(),
    ),
    GoRoute(
      path: '/',
      builder: (context, state) => const MainNavigationScreen(),
      routes: [
        GoRoute(
          path: 'add-expense',
          builder: (context, state) => const AddExpenseScreen(),
        ),
        GoRoute(
          path: 'budget',
          builder: (context, state) => const BudgetScreen(),
        ),
        GoRoute(
          path: 'predictions',
          builder: (context, state) => const PredictionsScreen(),
        ),
      ],
    ),
    GoRoute(
      path: '/chat',
      builder: (context, state) => const ChatScreen(),
    ),
  ],
);
