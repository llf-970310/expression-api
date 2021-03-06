from celery import Celery
from flask_login import current_user

from app.async_tasks import celery_config
from celery.result import AsyncResult
from flask import current_app
from app_config import redis_client

pw = 'ise_expression'
celery_broker = 'amqp://admin:%s@rabbitmq-server.expression.hosts:5672/' % pw
celery_backend = 'redis://:%s@redis-server.expression.hosts:6379/7' % pw

app = Celery('tasks', broker=celery_broker, backend=celery_backend)
app.config_from_object(celery_config)


class MyCelery(object):
    @staticmethod
    def put_task(q_type, test_id: str = None, q_num=None, std_text=None, file_path=None, use_lock=True):
        """
        创建异步评分任务
        :param file_path: 录音文件路径（for pretest）
        :param std_text: 原始文本（for pretest）
        :param q_type: 在(pretest, 1, 2, 3)中选择
        :param test_id: string
        :param q_num: 需分析的题号，pretest时留空，其他情况不可留空
        :param use_lock: 是否使用redis锁
        :return: task_id, exception
        """
        try:
            if use_lock:
                if q_type == "pretest":
                    key = 'celery_lock:%s-%s' % (q_type, current_user.id)
                else:
                    key = 'celery_lock:%s-%s-%s' % (q_type, test_id, q_num)
                val = ''
                lock = redis_client.set(key, val, ex=5, nx=True)
                if not lock:
                    raise Exception('Failed to get redis lock')
            if q_type == 'pretest':
                # 此处名称应与 worker 端的 task_name 保持一致
                # 不建议在此指定 queue，在 config 中使用 CELERY_ROUTES 配置
                nick_name = current_user.name
                ret = app.send_task('analysis_audio_test', args=(std_text, file_path, nick_name), priority=20)
            elif q_type in [3, '3']:
                ret = app.send_task('analysis_3', args=(str(test_id), str(q_num)), priority=10)
            elif q_type in [1, 2, 5, 6, '1', '2', '5', '6', 7, '7']:
                ret = app.send_task('analysis_12', args=(str(test_id), str(q_num)), priority=2)
            else:
                raise Exception('Unknown q_type')
            current_app.logger.info("AsyncResult id: %s" % ret.id)
            return ret.id, None
        except Exception as e:
            return None, e

    @staticmethod
    def is_task_finished(task_id: str):
        task = AsyncResult(task_id)
        return task.ready()
