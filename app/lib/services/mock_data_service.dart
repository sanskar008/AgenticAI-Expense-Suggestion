import '../models/budget.dart';
import '../models/chat_message.dart';
import '../models/expense.dart';
import '../models/goal.dart';
import '../models/insight.dart';
import '../models/prediction.dart';

class MockDataService {
  static List<Expense> getExpenses() {
    final now = DateTime.now();

    Expense e(
      String id,
      String title,
      double amount,
      ExpenseCategory cat,
      int daysAgo, [
      String? note,
    ]) =>
        Expense(
          id: id,
          title: title,
          amount: amount,
          category: cat,
          date: now.subtract(Duration(days: daysAgo)),
          note: note,
        );

    return [
      // ── This Month ─────────────────────────────────────────
      e('1', 'Swiggy Order', 450, ExpenseCategory.food, 0),
      e('2', 'Zomato Dinner', 780, ExpenseCategory.food, 1),
      e('3', 'Metro Card Recharge', 500, ExpenseCategory.travel, 2),
      e('4', 'Netflix Subscription', 649, ExpenseCategory.entertainment, 3),
      e('5', 'Big Basket Grocery', 2340, ExpenseCategory.food, 4),
      e('6', 'Amazon – Headphones', 3200, ExpenseCategory.shopping, 5),
      e('7', 'Electricity Bill', 1800, ExpenseCategory.bills, 6),
      e('8', 'Ola Ride', 320, ExpenseCategory.travel, 7),
      e('9', 'Restaurant Dinner', 1450, ExpenseCategory.food, 8),
      e('10', 'Myntra Kurta', 1500, ExpenseCategory.shopping, 9),
      e('11', 'Internet Bill', 1499, ExpenseCategory.bills, 10),
      e('12', 'Medical Store', 450, ExpenseCategory.health, 11),
      e('13', 'Cafe Coffee Day', 380, ExpenseCategory.food, 12),
      e('14', 'Movie Tickets – PVR', 600, ExpenseCategory.entertainment, 13),
      e('15', 'Monthly Bus Pass', 600, ExpenseCategory.travel, 14),
      e('16', 'Gas Bill', 1200, ExpenseCategory.bills, 15),
      e('17', 'Flipkart – Shoes', 2499, ExpenseCategory.shopping, 16),
      e('18', 'Gym Membership', 2000, ExpenseCategory.health, 17),
      e('19', 'Dunzo Order', 890, ExpenseCategory.food, 18),
      e('20', 'Spotify Premium', 119, ExpenseCategory.entertainment, 19),
      // ── Last Month ──────────────────────────────────────────
      e('21', 'Zomato Lunch', 540, ExpenseCategory.food, 35),
      e('22', 'IndiGo Flight', 4800, ExpenseCategory.travel, 37),
      e('23', 'H&M – Jeans', 2999, ExpenseCategory.shopping, 38),
      e('24', 'Water Bill', 320, ExpenseCategory.bills, 40),
      e('25', 'Doctor Visit', 800, ExpenseCategory.health, 42),
      e('26', 'Swiggy Weekend', 1200, ExpenseCategory.food, 44),
      e('27', 'Amazon Prime', 299, ExpenseCategory.entertainment, 45),
      e('28', 'Rapido Ride', 180, ExpenseCategory.travel, 46),
      e('29', 'Grocery – DMart', 1980, ExpenseCategory.food, 48),
      e('30', 'Phone Cover', 349, ExpenseCategory.shopping, 50),
    ];
  }

  static List<Budget> getBudgets() {
    return [
      const Budget(id: 'b1', category: ExpenseCategory.food, limit: 8000, spent: 6290),
      const Budget(id: 'b2', category: ExpenseCategory.travel, limit: 3000, spent: 1420),
      const Budget(id: 'b3', category: ExpenseCategory.shopping, limit: 5000, spent: 7199),
      const Budget(id: 'b4', category: ExpenseCategory.entertainment, limit: 2000, spent: 1368),
      const Budget(id: 'b5', category: ExpenseCategory.bills, limit: 5000, spent: 4499),
      const Budget(id: 'b6', category: ExpenseCategory.health, limit: 3000, spent: 2450),
    ];
  }

  static List<Goal> getGoals() {
    final now = DateTime.now();
    return [
      Goal(
        id: 'g1',
        title: 'Emergency Fund',
        emoji: '🛡️',
        targetAmount: 50000,
        savedAmount: 23000,
        deadline: now.add(const Duration(days: 180)),
      ),
      Goal(
        id: 'g2',
        title: 'New iPhone 16',
        emoji: '📱',
        targetAmount: 80000,
        savedAmount: 35000,
        deadline: now.add(const Duration(days: 90)),
      ),
      Goal(
        id: 'g3',
        title: 'Goa Trip',
        emoji: '🏖️',
        targetAmount: 30000,
        savedAmount: 18000,
        deadline: now.add(const Duration(days: 60)),
      ),
    ];
  }

  static List<Insight> getInsights() {
    return const [
      Insight(
        id: 'i1',
        title: 'Shopping Budget Exceeded!',
        description:
            'You\'ve spent ₹7,199 on Shopping — that\'s ₹2,199 over your ₹5,000 limit. Consider pausing non-essential purchases.',
        type: InsightType.alert,
        category: 'Shopping',
        changePercent: 43.98,
      ),
      Insight(
        id: 'i2',
        title: 'Bills Are 90% of Budget',
        description:
            'Bills have consumed ₹4,499 of your ₹5,000 limit with days still left in the month.',
        type: InsightType.alert,
        category: 'Bills',
        changePercent: 89.98,
      ),
      Insight(
        id: 'i3',
        title: 'Food Spending on Track',
        description:
            'Great job! Food spending is at ₹6,290 against a ₹8,000 budget — you\'re at 79% with a comfortable buffer.',
        type: InsightType.info,
        category: 'Food',
        changePercent: 78.6,
      ),
      Insight(
        id: 'i4',
        title: 'Cut Subscriptions to Save ₹768',
        description:
            'You\'re spending ₹768/month on Netflix + Spotify. Sharing a family plan could halve this cost.',
        type: InsightType.tip,
        changePercent: -50,
      ),
      Insight(
        id: 'i5',
        title: 'Entertainment Spending Rose 45%',
        description:
            'Entertainment jumped from ₹946 last month to ₹1,368 this month — mainly due to movie tickets and streaming.',
        type: InsightType.trend,
        category: 'Entertainment',
        changePercent: 44.6,
      ),
      Insight(
        id: 'i6',
        title: 'You Could Save ₹2,774 This Month',
        description:
            'Your total budget is ₹26,000 and you\'ve spent ₹23,226. Stay disciplined for the rest of the month!',
        type: InsightType.tip,
        changePercent: 10.6,
      ),
    ];
  }

  static List<MonthlyPrediction> getMonthlyPredictions() {
    final now = DateTime.now();
    return [
      MonthlyPrediction(
        month: DateTime(now.year, now.month - 5),
        predicted: 22000,
        actual: 21400,
      ),
      MonthlyPrediction(
        month: DateTime(now.year, now.month - 4),
        predicted: 23500,
        actual: 24100,
      ),
      MonthlyPrediction(
        month: DateTime(now.year, now.month - 3),
        predicted: 22800,
        actual: 22300,
      ),
      MonthlyPrediction(
        month: DateTime(now.year, now.month - 2),
        predicted: 25000,
        actual: 26800,
      ),
      MonthlyPrediction(
        month: DateTime(now.year, now.month - 1),
        predicted: 24500,
        actual: 23980,
      ),
      MonthlyPrediction(
        month: DateTime(now.year, now.month),
        predicted: 28500,
        actual: 23226,
      ),
      MonthlyPrediction(
        month: DateTime(now.year, now.month + 1),
        predicted: 27000,
      ),
      MonthlyPrediction(
        month: DateTime(now.year, now.month + 2),
        predicted: 26500,
      ),
    ];
  }

  static List<CategoryPrediction> getCategoryPredictions() {
    return const [
      CategoryPrediction(
        category: 'Food',
        currentSpending: 6290,
        predictedSpending: 8100,
        changePercent: 28.8,
      ),
      CategoryPrediction(
        category: 'Shopping',
        currentSpending: 7199,
        predictedSpending: 5500,
        changePercent: -23.6,
      ),
      CategoryPrediction(
        category: 'Bills',
        currentSpending: 4499,
        predictedSpending: 4800,
        changePercent: 6.7,
      ),
      CategoryPrediction(
        category: 'Entertainment',
        currentSpending: 1368,
        predictedSpending: 1800,
        changePercent: 31.6,
      ),
      CategoryPrediction(
        category: 'Travel',
        currentSpending: 1420,
        predictedSpending: 1200,
        changePercent: -15.5,
      ),
      CategoryPrediction(
        category: 'Health',
        currentSpending: 2450,
        predictedSpending: 2200,
        changePercent: -10.2,
      ),
    ];
  }

  static List<ChatMessage> getInitialMessages() {
    return [
      ChatMessage(
        id: 'init',
        content:
            'Hi! I\'m your AI Financial Copilot 🤖\n\nI can help you understand your spending, find savings opportunities, and reach your financial goals.\n\nTry asking me:\n• "Where did I spend most?"\n• "How can I save more?"\n• "Am I on track with my budget?"',
        sender: MessageSender.ai,
        timestamp: DateTime.now().subtract(const Duration(minutes: 1)),
      ),
    ];
  }

  static String getChatResponse(String query) {
    final q = query.toLowerCase().trim();

    if (_matches(q, ['where', 'most', 'highest', 'top spend', 'spent most'])) {
      return '📊 Your top spending categories this month:\n\n'
          '1. 🛍️ Shopping — ₹7,199 (31%)\n'
          '2. 🍕 Food — ₹6,290 (27%)\n'
          '3. 📋 Bills — ₹4,499 (19%)\n'
          '4. 💊 Health — ₹2,450 (11%)\n\n'
          '⚠️ Shopping is ₹2,199 over budget! That\'s the main concern.';
    }

    if (_matches(q, ['save', 'saving', 'reduce', 'cut', 'less'])) {
      return '💡 Here are 3 actionable ways to save this month:\n\n'
          '1. 🛍️ Pause shopping — you\'re already ₹2,199 over budget\n'
          '2. 🍕 Cook at home 3x a week — could save ₹1,500+\n'
          '3. 📱 Share Netflix/Spotify — save ₹400/month\n\n'
          'Following all three could save you **₹4,099** next month! 🚀';
    }

    if (_matches(q, ['budget', 'on track', 'limit'])) {
      return '📈 Your budget status for April:\n\n'
          '✅ Food: ₹6,290 / ₹8,000 (79%)\n'
          '✅ Travel: ₹1,420 / ₹3,000 (47%)\n'
          '✅ Entertainment: ₹1,368 / ₹2,000 (68%)\n'
          '🟠 Bills: ₹4,499 / ₹5,000 (90%)\n'
          '🟠 Health: ₹2,450 / ₹3,000 (82%)\n'
          '🔴 Shopping: ₹7,199 / ₹5,000 (144%)\n\n'
          'Overall: ₹23,226 / ₹26,000 spent (89%)';
    }

    if (_matches(q, ['goal', 'target', 'iphone', 'goa', 'emergency', 'trip'])) {
      return '🎯 Your savings goals summary:\n\n'
          '🛡️ Emergency Fund: ₹23,000 / ₹50,000 (46%) — 180 days left\n'
          '📱 iPhone 16: ₹35,000 / ₹80,000 (44%) — 90 days left\n'
          '🏖️ Goa Trip: ₹18,000 / ₹30,000 (60%) — 60 days left\n\n'
          'You need to save ~₹15,000/month to hit all goals on time!';
    }

    if (_matches(q, ['predict', 'forecast', 'next month', 'future'])) {
      return '🔮 Spending forecast:\n\n'
          '• This month projected: **₹28,500**\n'
          '• Next month estimate: **₹27,000**\n\n'
          'Based on your trend, food and entertainment costs are rising. Consider setting stricter weekly limits.';
    }

    if (_matches(q, ['food', 'eating', 'restaurant', 'zomato', 'swiggy'])) {
      return '🍕 Food Spending Analysis:\n\n'
          '• This month: ₹6,290 (on track — 79% of ₹8,000)\n'
          '• Last month: ₹3,720\n'
          '• Change: +69% 📈\n\n'
          'You\'re spending more on food delivery (Swiggy/Zomato). '
          'Cooking at home even 2-3 times a week could save ₹1,200-₹1,800/month!';
    }

    if (_matches(q, ['hello', 'hi', 'hey', 'hola'])) {
      return 'Hello! 👋 How can I help with your finances today?\n\n'
          'Ask me about your spending, budget, goals, or how to save more!';
    }

    if (_matches(q, ['thank', 'thanks', 'great', 'awesome', 'nice'])) {
      return 'You\'re welcome! 😊 Keep up the good work with your finances. '
          'Small consistent steps lead to big financial freedom! 💪';
    }

    return '🤔 Great question! Based on your spending data:\n\n'
        '• Monthly total: ₹23,226 (89% of budget)\n'
        '• Biggest concern: Shopping is over budget\n'
        '• Best opportunity: Reduce online shopping by ₹2,000\n\n'
        'Try asking: "How can I save more?" or "Show my budget status"';
  }

  static bool _matches(String query, List<String> keywords) {
    return keywords.any((k) => query.contains(k));
  }
}
