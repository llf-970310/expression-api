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

struct GetExamReportRequest {
    1: required string examId
}

struct GetExamReportResponse {
    1: required ExamReport report
    2: required ExamScore score
    3: required i32 statusCode
    4: required string statusMsg
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
}