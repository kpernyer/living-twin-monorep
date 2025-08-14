import 'personalization_service.dart';

class PersonalizationLayer implements PersonalizationService {
  @override
  Future<List<String>> getSampleQuestions() async {
    // In the future, this will fetch personalized questions.
    return [
      "What are the latest updates on the project?",
      "Can you summarize the last meeting?",
      "What are my priorities for today?",
    ];
  }

  @override
  Future<List<String>> getTodoItems() async {
    // In the future, this will fetch personalized to-do items.
    return [
      'Review Q3 Financial Projections',
      'Approve Marketing Campaign Budget',
      'Finalize hiring decision for Senior Engineer',
    ];
  }
}
