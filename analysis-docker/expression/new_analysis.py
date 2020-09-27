from analysis_features import analysis2 as analysis_features
from analysis_scores import score2 as compute_score


if __name__ == '__main__':
    path = '/Users/gyue/Programs/exp-docker/expression/net_test.wav'
    wordbase = {"keywords":[["胡杨"],["抗旱","干旱"],["生命力"],["强"]],"mainwords":[["扎根"],["贮水","存水"],["盐碱"],["温差","降水量","蒸发量"],["寿命"],["沙漠","荒漠","草原"]],"detailwords":[[["10","十"],["固土","防沙","水土流失","环境保护"],["地下水","含水层","水源","雨水"]],[["储存","存储","贮存","存放","蓄水","保存"],["干旱","旱季","潮湿","缺水","干燥","寒冷","雨季"]],[["树叶","树枝","树干","叶子","枝叶","枝干"],["排出"],["盐碱"]],[["荒漠","草原","沙漠"],["41","四十"],["零下","低温"],["高温","室温","加热","高低温"],["千","寿命"],["39","三十九","80","八十"]]]}
    feature_result = analysis_features(path, wordbase, timeout=30)
    print(feature_result)
    key_weights = [26, 26.0, 26.0, 26.0, 26.0]
    detail_weights = [8, 8.14285714285714, 
            8.14285714285714, 
            8.14285714285714, 
            8.14285714285714, 
            8.14285714285714, 
            8.14285714285714, 
            8.14285714285714, 
            8.14285714285714, 
            8.14285714285714, 
            8.14285714285714, 
            8.14285714285714, 
            8.14285714285714, 
            8.14285714285714, 
            8.14285714285714
        ]
    score = compute_score(feature_result['key_hits'], feature_result['detail_hits'], key_weights, detail_weights)
    print(score)


