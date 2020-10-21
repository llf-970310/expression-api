namespace py user

struct UserInfo {
    1: required string role,
    2: optional string nickName,
    3: optional string email,
    4: optional string phone,
    5: optional string wechatId,
    6: optional i32 remainingExamNum,
    7: optional string registerTime,
    8: optional string lastLoginTime,
    9: optional string vipStartTime,
    10: optional string vipEndTime,
    11: optional list<string> questionHistory
}

struct InvitationCode {
    1: required string code
    2: optional string creator
    3: optional string createTime
    4: optional i32 availableTimes
    5: optional string vipStartTime
    6: optional string vipEndTime
    7: optional i32 remainingExamNum
    8: optional i32 remainingExerciseNum
    9: optional list<string> activateUsers
}

struct AuthenticateRequest {
    1: required string username
    2: required string password
}

struct AuthenticateResponse {
    1: optional string token
    2: required i32 statusCode
    3: required string statusMsg
}

struct AuthenticateWechatUserRequest {
    1: required string code
    2: optional string nickName
}

struct AuthenticateWechatUserResponse {
    1: optional string token
    2: required i32 statusCode
    3: required string statusMsg
}

struct CreateUserRequest {
    1: required string username
    2: required string password
    3: required string name
    4: optional string invitationCode
}

struct CreateUserResponse {
    1: required i32 statusCode
    2: required string statusMsg
}

struct GetUserInfoRequest {
    1: required string userId
}

struct GetUserInfoResponse {
    1: required UserInfo userInfo
    2: required i32 statusCode
    3: required string statusMsg
}

struct UpdateUserInfoRequest {
    1: required string userId
    2: optional string invitationCode
}

struct UpdateUserInfoResponse {
    1: required i32 statusCode
    2: required string statusMsg
}

struct CheckExamPermissionRequest {
    1: required string userId
}

struct CheckExamPermissionResponse {
    1: required i32 statusCode
    2: required string statusMsg
}

struct CreateInvitationCodeRequest {
    1: required string creator
    2: optional i32 availableTimes
    3: optional string vipStartTime
    4: optional string vipEndTime
    5: optional i32 remainingExamNum
    6: optional i32 remainingExerciseNum
    7: required i32 codeNum
}

struct CreateInvitationCodeResponse {
    1: required list<string> codeList
    2: required i32 statusCode
    3: required string statusMsg
}

struct GetInvitationCodeRequest {
    1: optional string invitationCode
    2: optional string createTimeFrom
    3: optional string createTimeTo
    4: optional string availableTimes
    5: required i32 page
    6: required i32 pageSize
}

struct GetInvitationCodeResponse {
    1: required list<InvitationCode> invitationCodeList
    2: required i32 total
    3: required i32 statusCode
    4: required string statusMsg
}

service UserService {
    // 认证相关
    AuthenticateResponse authenticate(1: AuthenticateRequest request)
    AuthenticateWechatUserResponse authenticateWechatUser(1: AuthenticateWechatUserRequest request)

    // 用户信息相关
    CreateUserResponse createUser(1: CreateUserRequest request)
    GetUserInfoResponse getUserInfo(1: GetUserInfoRequest request)
    UpdateUserInfoResponse updateUserInfo(1: UpdateUserInfoRequest request)

    // 判断是否有考试权限
    CheckExamPermissionResponse checkExamPermission(1: CheckExamPermissionRequest request)

    // 邀请码
    GetInvitationCodeResponse getInvitationCode(1: GetInvitationCodeRequest request)
    CreateInvitationCodeResponse createInvitationCode(1: CreateInvitationCodeRequest request)
}