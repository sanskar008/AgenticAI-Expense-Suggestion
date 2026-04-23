import 'package:flutter/material.dart';
import '../models/expense.dart';

class CategoryIcon extends StatelessWidget {
  final ExpenseCategory category;
  final double size;
  final bool showLabel;

  const CategoryIcon({
    super.key,
    required this.category,
    this.size = 44,
    this.showLabel = false,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            color: category.color.withOpacity(0.15),
            borderRadius: BorderRadius.circular(size * 0.3),
          ),
          child: Icon(
            category.icon,
            color: category.color,
            size: size * 0.52,
          ),
        ),
        if (showLabel) ...[
          const SizedBox(height: 4),
          Text(
            category.displayName,
            style: TextStyle(
              fontSize: 10,
              color: category.color,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ],
    );
  }
}
