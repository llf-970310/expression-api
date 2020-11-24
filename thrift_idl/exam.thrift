namespace py exam

enum ExamType {
    AudioTest = 1
    RealExam = 2
}

struct ExamScore {
    1: optional double total
    2: optional double quality
    3: optional double key
    4: optional double detail
    5: optional double structure
    6: optional double logic
}

struct ExamReport {
    1: optional string ftlRatio
    2: optional string clearRatio
    3: optional string speed
    4: optional string interval
    5: optional string key
    6: optional string detail
    7: optional list<string> structure
    8: optional list<string> logic
}

struct ExamRecord {
    1: optional string examStartTime  // i64 存时间戳更合适，但数据库不好改
    2: optional string templateId
    3: optional string examId
    4: optional ExamScore scoreInfo
}

struct QuestionInfo {
    1: optional string id
    2: required string content
    3: required i32 type  // 题型（0 表示音频测试题目，此时 id 为 None）
    4: optional i32 questionNum  // 第几题
    5: required i32 readLimitTime  // 读题时长，单位秒
    6: required i32 answerLimitTime  // 答题时长，单位秒
    7: optional bool isLastQuestion  // 是否最后一题
    8: required map<string, string> questionTip  // 题目要求与提示
    9: optional double examTime  // 测试总时长，单位秒
    10: optional double examLeftTime  // 测试剩余时长，单位秒
}

struct ExamTemplate {
    1: required string id
    2: required string name
    3: required string description
    4: required i32 questionCount  // 题目个数
}

struct GetExamReportRequest {
    1: required string examId
}

struct GetExamReportResponse {
    1: required ExamReport report
    2: required ExamScore score
    3: required i32 statusCode
    4: required string statusMsg
}

struct ComputeExamScoreRequest {
    1: required string examId
}

struct ComputeExamScoreResponse {
    1: required ExamScore score
    2: required i32 statusCode
    3: required string statusMsg
}

struct GetExamRecordRequest {
    1: optional string userId
    2: optional string templateId
}

struct GetExamRecordResponse {
    1: required list<ExamRecord> examList
    2: required i32 statusCode
    3: required string statusMsg
}

struct InitNewAudioTestRequest {
    1: required string userId
}

struct InitNewAudioTestResponse {
    1: required QuestionInfo question
    2: required i32 statusCode
    3: required string statusMsg
}

struct InitNewExamRequest {
    1: required string userId
    2: required string templateId
}

struct InitNewExamResponse {
    1: required string examId
    2: required i32 statusCode
    3: required string statusMsg
}

struct GetQuestionInfoRequest {
    1: required string examId
    2: required i32 questionNum  // 第几题
}

struct GetQuestionInfoResponse {
    1: required QuestionInfo question
    3: required i32 statusCode
    4: required string statusMsg
}

struct GetFileUploadPathRequest {
    1: optional string examId
    2: required string userId
    3: required ExamType type  // 1 音频测试（无需 examId） 2 正式测试
    4: optional i32 questionNum
}

struct GetFileUploadPathResponse {
    1: required string path
    3: required i32 statusCode
    4: required string statusMsg
}

struct GetPaperTemplateRequest {
    1: optional string templateId
}

struct GetPaperTemplateResponse {
    1: required list<ExamTemplate> templateList
    2: required i32 statusCode
    3: required string statusMsg
}

struct GetAudioTestResultRequest {
    1: optional string examId
}

struct GetAudioTestResultResponse {
    1: required bool canRecognize
    2: required double levenshteinRatio
    3: required i32 statusCode
    4: required string statusMsg
}

struct GetExamResultRequest {
    1: required string examId
}

struct GetExamResultResponse {
    1: required ExamReport report
    2: required ExamScore score
    3: required i32 statusCode
    4: required string statusMsg
}

service ExamService {
    // 初始化音频测试题
    InitNewAudioTestResponse initNewAudioTest(1: InitNewAudioTestRequest request)
    // 初始化正式测试题
    InitNewExamResponse initNewExam(1: InitNewExamRequest request)

    // 获取试卷模板信息
    GetPaperTemplateResponse getPaperTemplate(1: GetPaperTemplateRequest request)
    // 获取题目信息
    GetQuestionInfoResponse getQuestionInfo(1: GetQuestionInfoRequest request)
    // 获取音频文件的上传路径
    GetFileUploadPathResponse getFileUploadPath(1: GetFileUploadPathRequest request)

    // 获取音频测试（试音）结果
    GetAudioTestResultResponse getAudioTestResult(1: GetAudioTestResultRequest request)
    // 获取正式测试结果
    GetExamResultResponse getExamResult(1: GetExamResultRequest request)
    // 获取历史测试报告（分数直接取数据库）
    GetExamReportResponse getExamReport(1: GetExamReportRequest request)
    // 获取测试分数（有分数直接取，无分数会计算并保存）
    ComputeExamScoreResponse computeExamScore(1: ComputeExamScoreRequest request)
    // 获取历史考试记录
    GetExamRecordResponse getExamRecord(1: GetExamRecordRequest request)
}