namespace py exam

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

//struct GetQuestionInfoRequest {
//    1: required string examId
//    2: required i32 questionNum
//}
//
//struct GetQuestionInfoResponse {
//    1: required ExamReport report
//    3: required i32 statusCode
//    4: required string statusMsg
//}

service ExamService {
    GetExamReportResponse getExamReport(1: GetExamReportRequest request)
    ComputeExamScoreResponse computeExamScore(1: ComputeExamScoreRequest request)

    GetExamRecordResponse getExamRecord(1: GetExamRecordRequest request)
}