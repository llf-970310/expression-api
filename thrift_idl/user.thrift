namespace py user

struct UserInfo {
    1: optional string role,
    2: optional string nickName,
    3: optional string email,
    4: optional string phone,
    5: optional string wechatId,
    6: optional i32 remainingExamNum,
    7: optional i64 registerTime,
    8: optional i64 lastLoginTime,
    9: optional i64 vipStartTime,
    10: optional i64 vipEndTime,
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

struct CreateUserRequest {
    1: required UserInfo userInfo
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
    1: required UserInfo userInfo
}

struct UpdateUserInfoResponse {
    1: required i32 statusCode
    2: required string statusMsg
}

service UserService {
    AuthenticateResponse authenticate(1: AuthenticateRequest request)
    CreateUserResponse createUser(1: CreateUserRequest request)
    GetUserInfoResponse getUserInfo(1: GetUserInfoRequest request)
    UpdateUserInfoResponse updateUserInfo(1: UpdateUserInfoRequest request)
}