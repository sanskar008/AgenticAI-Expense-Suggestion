import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../screens/add_expense_screen.dart';
import '../screens/budget_screen.dart';
import '../screens/chat_screen.dart';
import '../screens/main_navigation_screen.dart';
import '../screens/predictions_screen.dart';
import '../screens/splash_screen.dart';
import '../screens/login_screen.dart';
import '../screens/landing_screen.dart';
import '../providers/auth_provider.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authProvider);
  final isAuthenticated = authState.isAuthenticated;
  final isFirstTime = authState.isFirstTime;
  final isLoading = authState.isLoading;

  return GoRouter(
    initialLocation: '/splash',
    redirect: (context, state) {
      final isSplash = state.matchedLocation == '/splash';
      final isLanding = state.matchedLocation == '/landing';
      final isLogin = state.matchedLocation == '/login';

      // If still loading initial auth state, stay on splash
      if (isSplash && isLoading) return null;

      // Logic for Onboarding/Landing
      if (isFirstTime && !isLanding && !isSplash) {
        return '/landing';
      }

      // Logic for Auth
      if (!isAuthenticated) {
        // If not authenticated, we either go to landing (if first time) or login
        if (isFirstTime) {
          if (!isLanding && !isSplash) return '/landing';
        } else {
          if (!isLogin && !isSplash && !isLanding) return '/login';
        }
      } else {
        // If authenticated, don't allow landing or login
        if (isLogin || isLanding || isSplash) return '/';
      }

      return null;
    },
    routes: [
      GoRoute(
        path: '/splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/landing',
        builder: (context, state) => const LandingScreen(),
      ),
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
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
});
