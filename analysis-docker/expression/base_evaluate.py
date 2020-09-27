#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-3

from _xf_evaluate import evl_and_save


if __name__ == '__main__':
    import io
    text = io.StringIO()
    text.write("愿你有好运气")
    evl_fp = io.StringIO()
    evl_and_save('net_test.wav', text, evl_fp, framerate=8000)
    print(evl_fp.getvalue())

    # with open(config.EVL_JSON_FILE_PATH, 'r') as f:
    #     print(f.read())
