#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-3

import _xf_recognise
import _bd_recognise


def rcg_and_save(wave_file, rcg_fp, segments=0, timeout=600, stop_on_failure=True,
                 x_appid=None, api_key=None,
                 bd_appid=None, bd_api_key=None, bd_secret_key=None,
                 rcg_interface='baidu',use_pro_api=True):
    if rcg_interface == 'xunfei':
        return _xf_recognise.rcg_and_save(wave_file, rcg_fp, segments, timeout, stop_on_failure=stop_on_failure,
                                          x_appid=x_appid, api_key=api_key)
    else:
        return _bd_recognise.rcg_and_save(wave_file, rcg_fp, segments, timeout, stop_on_failure=stop_on_failure,
                                          bd_appid=bd_appid, bd_api_key=bd_api_key, bd_secret_key=bd_secret_key,
                                          use_pro_api=use_pro_api)


if __name__ == '__main__':
    import io
    import utils
    import logging

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s:\t%(message)s')

    # result = rcg(config.WAV_FILE_PATH, segments=1, timeout=100)
    # rcg(config.WAV_FILE_PATH, timeout=10, segments=3)
    # print(isinstance(result, str))
    # print(isinstance(result, dict))

    wave_file_processed = io.BytesIO()
    interval_list = utils.find_and_remove_intervals('net_test.wav', wave_file_processed)

    rcg_fp = io.StringIO()
    rcg_and_save(wave_file_processed, rcg_fp, segments=3, timeout=10, stop_on_failure=True)

    print(utils.read(rcg_fp))
