namespace py question

struct RetellingQuestion {
    1: required i32 questionIndex  // 题号
    2: required string rawText
    3: required list<list<string>> keywords
    4: required list<list<list<string>>> detailwords
//    5: optional bool inOptimize
//    6: optional string lastOptimizeDate
//    7: optional bool optimized
    5: optional i32 feedbackUpCount
    6: optional i32 feedbackDownCount
    7: optional i32 usedTimes
}

struct GetRetellingQuestionRequest {
    1: optional i32 questionIndex  // 题号
    2: optional i32 page
    3: optional i32 pageSize
}

struct GetRetellingQuestionResponse {
    1: required list<RetellingQuestion> questions
    2: required i32 total
    3: required i32 statusCode
    4: required string statusMsg
}

struct GenerateWordbaseRequest {
    1: required string text
}

struct GenerateWordbaseResponse {
    1: required list<list<string>> keywords
    2: required list<list<list<string>>> detailwords
    3: required i32 statusCode
    4: required string statusMsg
}

service QuestionService {
    // 获取转述题信息
    GetRetellingQuestionResponse getRetellingQuestion(1: GetRetellingQuestionRequest request)
    // 根据文本生成关键词和细节词
    GenerateWordbaseResponse generateWordbase(1: GenerateWordbaseRequest request)
}