namespace py analysis

struct AnalyzeReadingQuestionRequest {
    1: required string filePath
    2: required string stdText
}

struct AnalyzeReadingQuestionResponse {
    1: required string feature
    2: required double qualityScore
    3: required i32 statusCode
    4: required string statusMsg
}

struct AnalyzeRetellingQuestionRequest {
    1: required string filePath
    2: required list<list<string>> keywords
    3: required list<list<list<string>>> detailwords
    4: required list<double> keyWeights
    5: required list<double> detailWeights
}

struct AnalyzeRetellingQuestionResponse {
    1: required string feature
    2: required double keyScore
    3: required double detailScore
    4: required i32 statusCode
    5: required string statusMsg
}

struct AnalyzeExpressionQuestionRequest {
    1: required string filePath
    2: required map<string, list<string>> wordbase
}

struct AnalyzeExpressionQuestionResponse {
    1: required string feature
    2: required double structureScore
    3: required double logicScore
    4: required i32 statusCode
    5: required string statusMsg
}

service AnalysisService {
    AnalyzeReadingQuestionResponse analyzeReadingQuestion(1: AnalyzeReadingQuestionRequest request)
    AnalyzeRetellingQuestionResponse analyzeRetellingQuestion(1: AnalyzeRetellingQuestionRequest request)
    AnalyzeExpressionQuestionResponse analyzeExpressionQuestion(1: AnalyzeExpressionQuestionRequest request)
}