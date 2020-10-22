import thriftpy2
from thriftpy2.rpc import make_client

exam_thrift = thriftpy2.load("./thrift_idl/exam.thrift", module_name="exam_thrift")
exam_client = make_client(exam_thrift.ExamService, '127.0.0.1', 9091)

user_thrift = thriftpy2.load("./thrift_idl/user.thrift", module_name="user_thrift")
user_client = make_client(user_thrift.UserService, '127.0.0.1', 9092)

analysis_thrift = thriftpy2.load("./thrift_idl/analysis.thrift", module_name="analysis_thrift")
analysis_client = make_client(analysis_thrift.AnalysisService, '127.0.0.1', 9093, timeout=10000)

question_thrift = thriftpy2.load("./thrift_idl/question.thrift", module_name="question_thrift")
question_client = make_client(question_thrift.QuestionService, '127.0.0.1', 9094)
