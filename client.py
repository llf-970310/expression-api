import thriftpy2
from thriftpy2.rpc import make_client

exam_thrift = thriftpy2.load("./thrift_idl/exam.thrift", module_name="exam_thrift")
exam_client = make_client(exam_thrift.ExamService, '127.0.0.1', 9091)

user_thrift = thriftpy2.load("./thrift_idl/user.thrift", module_name="user_thrift")
user_client = make_client(user_thrift.UserService, '127.0.0.1', 9092)
