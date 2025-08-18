import 'package:freezed_annotation/freezed_annotation.dart';

part 'goal_model.freezed.dart';
part 'goal_model.g.dart';

/// Goal Status enum
enum GoalStatus { draft, active, completed, archived }

/// Goal Priority enum
enum GoalPriority { low, medium, high, critical }

/// Immutable Goal model with freezed
/// 
/// This demonstrates how freezed handles:
/// - Complex nested data structures
/// - Enums with automatic serialization
/// - Collections (Lists) that are automatically immutable
/// - Nullable fields with proper null safety
@freezed
class GoalModel with _$GoalModel {
  const factory GoalModel({
    required String id,
    required String tenantId,
    required String title,
    required DateTime createdAt,
    required DateTime updatedAt,
    @Default(GoalStatus.draft) GoalStatus goalStatus,
    @Default(GoalPriority.medium) GoalPriority priority,
    @Default('active') String status,
    @Default([]) List<String> tags,
    String? description,
    String? createdBy,
    DateTime? dueDate,
    DateTime? completionDate,
    double? progressPercentage,
    String? teamId,
    String? parentGoalId,
    Map<String, dynamic>? metadata,
  }) = _GoalModel;

  factory GoalModel.fromJson(Map<String, dynamic> json) =>
      _$GoalModelFromJson(json);
}

/// State management example with immutable goals
@freezed
class GoalsState with _$GoalsState {
  const factory GoalsState.initial() = _Initial;
  const factory GoalsState.loading() = _Loading;
  const factory GoalsState.loaded({
    required List<GoalModel> goals,
    GoalModel? selectedGoal,
  }) = _Loaded;
  const factory GoalsState.error(String message) = _Error;
}

/// Example showing benefits of immutable goal management:
/// ```dart
/// class GoalsBloc {
///   // State is immutable - no accidental mutations
///   GoalsState _state = const GoalsState.initial();
///   
///   void updateGoalProgress(String goalId, double progress) {
///     // Pattern matching on state
///     _state = switch(_state) {
///       GoalsState.loaded(:final goals) => GoalsState.loaded(
///         goals: goals.map((goal) => 
///           goal.id == goalId 
///             ? goal.copyWith(
///                 progressPercentage: progress,
///                 updatedAt: DateTime.now(),
///                 goalStatus: progress >= 100 
///                   ? GoalStatus.completed 
///                   : goal.goalStatus,
///               )
///             : goal
///         ).toList(),
///       ),
///       _ => _state, // No change for other states
///     };
///   }
///   
///   void addTag(String goalId, String tag) {
///     _state = switch(_state) {
///       GoalsState.loaded(:final goals) => GoalsState.loaded(
///         goals: goals.map((goal) =>
///           goal.id == goalId
///             ? goal.copyWith(
///                 tags: [...goal.tags, tag], // Immutable list update
///                 updatedAt: DateTime.now(),
///               )
///             : goal
///         ).toList(),
///       ),
///       _ => _state,
///     };
///   }
/// }
/// 
/// // Benefits:
/// // 1. No defensive copying needed - goals are immutable
/// // 2. Time-travel debugging - can store state history
/// // 3. Thread-safe - can pass goals between isolates
/// // 4. Predictable - state changes only through explicit copyWith
/// // 5. Testable - easy to create test data with specific fields
