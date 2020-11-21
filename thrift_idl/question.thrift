namespace py question

struct RetellingQuestion {
    1: optional i32 questionIndex  // 题号
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

struct DelQuestionRequest {
    1: required i32 questionIndex  // 题号
}

struct DelQuestionResponse {
    1: required i32 statusCode
    2: required string statusMsg
}

struct DelOriginalQuestionRequest {
    1: required i32 id  // 对应数据库中 q_id 字段
}

struct DelOriginalQuestionResponse {
    1: required i32 statusCode
    2: required string statusMsg
}

struct SaveRetellingQuestionRequest {
    1: required RetellingQuestion newQuestion
}

struct SaveRetellingQuestionResponse {
    1: required i32 statusCode
    2: required string statusMsg
}

struct SaveQuestionFeedbackRequest {
    1: required string questionId
    2: optional i32 upChange  // +1 or -1
    3: optional i32 downChange  // +1 or -1
    4: optional i32 likeChange  // +1 or -1
    5: required string userId
}

struct SaveQuestionFeedbackResponse {
    1: required i32 statusCode
    2: required string statusMsg
}

service QuestionService {
    // 获取转述题信息
    GetRetellingQuestionResponse getRetellingQuestion(1: GetRetellingQuestionRequest request)
    // 新增（修改）转述题信息
    SaveRetellingQuestionResponse saveRetellingQuestion(1: SaveRetellingQuestionRequest request)
    // 点赞、点踩、收藏题目
    SaveQuestionFeedbackResponse saveQuestionFeedback(1: SaveQuestionFeedbackRequest request)

    // 删除题目
    DelQuestionResponse delQuestion(1: DelQuestionRequest request)
    // 从原始题库删除题目
    DelOriginalQuestionResponse delOriginalQuestion(1: DelOriginalQuestionRequest request)

    // 根据文本生成关键词和细节词
    GenerateWordbaseResponse generateWordbase(1: GenerateWordbaseRequest request)
}