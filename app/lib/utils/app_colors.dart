import 'package:flutter/material.dart';

class AppColors {
  // Backgrounds
  static const Color bg = Color(0xFF0A0E21);
  static const Color surface = Color(0xFF1C1F35);
  static const Color surfaceLight = Color(0xFF252848);
  static const Color border = Color(0xFF2E3358);

  // Brand
  static const Color primary = Color(0xFF6C5CE7);
  static const Color primaryLight = Color(0xFF8B7FF0);
  static const Color cyan = Color(0xFF00CEC9);
  static const Color pink = Color(0xFFFD79A8);

  // Semantic
  static const Color success = Color(0xFF00B894);
  static const Color warning = Color(0xFFFFD93D);
  static const Color error = Color(0xFFFF6B6B);
  static const Color info = Color(0xFF74B9FF);

  // Text
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSecondary = Color(0xFFB2BEC3);
  static const Color textDisabled = Color(0xFF636E72);

  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF6C5CE7), Color(0xFF00CEC9)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient purplePinkGradient = LinearGradient(
    colors: [Color(0xFF6C5CE7), Color(0xFFFD79A8)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient cardGradient = LinearGradient(
    colors: [Color(0xFF1C1F35), Color(0xFF252848)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient greenGradient = LinearGradient(
    colors: [Color(0xFF00B894), Color(0xFF00CEC9)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}
