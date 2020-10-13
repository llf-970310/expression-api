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
