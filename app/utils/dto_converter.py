from app.admin.admin_config import ScoreConfig


def exam_score_convert_to_json(score) -> dict:
    return {
        "total": format(score.total, ScoreConfig.DEFAULT_NUM_FORMAT),
        "主旨": format(score.key, ScoreConfig.DEFAULT_NUM_FORMAT),
        "细节": format(score.detail, ScoreConfig.DEFAULT_NUM_FORMAT),
        "结构": format(score.structure, ScoreConfig.DEFAULT_NUM_FORMAT),
        "逻辑": format(score.logic, ScoreConfig.DEFAULT_NUM_FORMAT),
        "音质": format(score.quality, ScoreConfig.DEFAULT_NUM_FORMAT)
    }


def exam_report_convert_to_json(report) -> dict:
    return {
        "主旨": report.key, "细节": report.detail, "结构": report.structure,
        "逻辑": report.logic, "音质": {
            "无效表达率": report.ftlRatio,
            "清晰度": report.clearRatio,
            "语速": report.speed,
            "间隔": report.interval
        }
    }


def question_info_convert_to_json(question) -> dict:
    return {
        "questionType": question.type,
        "questionDbId": question.id,
        "questionNumber": question.questionNum,
        "questionLimitTime": question.answerLimitTime,
        "lastQuestion": question.isLastQuestion,
        "readLimitTime": question.readLimitTime,
        "questionInfo": question.questionTip,
        "questionContent": question.content,
        "examLeftTime": question.examLeftTime,
        "examTime": question.examTime
    }


def user_info_convert_to_json(user_info) -> dict:
    return {
        'role': user_info.role,
        'name': user_info.nickName,
        'email': user_info.email if user_info.email is not None else user_info.phone,
        'register_time': user_info.registerTime,
        'last_login_time': user_info.lastLoginTime,
        # 'questions_history': current_user.questions_history,
        'wx_id': user_info.wechatId,
        'vip_start_time': user_info.vipStartTime,
        'vip_end_time': user_info.vipEndTime,
        'remaining_exam_num': user_info.remainingExamNum
    }
