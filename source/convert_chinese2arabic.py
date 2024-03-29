#!/usr/bin/env python
# -*- coding: utf-8 -*-

chs_arabic_map = {u'零':0, u'一':1, u'二':2, u'三':3, u'四':4,
        u'五':5, u'六':6, u'七':7, u'八':8, u'九':9,
        u'十':10, u'百':100, u'千':10 ** 3, u'万':10 ** 4,
        u'〇':0, u'壹':1, u'贰':2, u'叁':3, u'肆':4,
        u'伍':5, u'陆':6, u'柒':7, u'捌':8, u'玖':9,
        u'拾':10, u'佰':100, u'仟':10 ** 3, u'萬':10 ** 4,
        u'亿':10 ** 8, u'億':10 ** 8, u'幺': 1,
        u'０':0, u'１':1, u'２':2, u'３':3, u'４':4,
        u'５':5, u'６':6, u'７':7, u'８':8, u'９':9}

def convertChineseDigitsToArabic (chinese_digits, encoding="utf-8"):
    result  = 0
    tmp     = 0
    hnd_mln = 0
    if chinese_digits == None:
        return -1
    for count in range(len(chinese_digits)):
        curr_char  = chinese_digits[count]
        curr_digit = chs_arabic_map.get(curr_char, None)
        if curr_digit == None:
            continue
        # meet 「亿」 or 「億」
        if curr_digit == 10 ** 8:
            result  = result + tmp
            result  = result * curr_digit
            # get result before 「亿」 and store it into hnd_mln
            # reset `result`
            hnd_mln = hnd_mln * 10 ** 8 + result
            result  = 0
            tmp     = 0
        # meet 「万」 or 「萬」
        elif curr_digit == 10 ** 4:
            result = result + tmp
            result = result * curr_digit
            tmp    = 0
        # meet 「十」, 「百」, 「千」 or their traditional version
        elif curr_digit >= 10:
            tmp    = 1 if tmp == 0 else tmp
            result = result + curr_digit * tmp
            tmp    = 0
        # meet single digit
        elif curr_digit is not None:
            tmp = tmp * 10 + curr_digit
        else:
            return result
    result = result + tmp
    result = result + hnd_mln
    return result

if __name__ == "__main__":
    test_map = {
    '三千五百二十三' : 3523,
    '七十五亿八百零七万九千二百零八':7508079208,
    '四万三千五百二十一':43521,
    '三千五百二十一':3521,
    '三千五百零八':3508,
    '三五六零':3560,
    '一万零三十':10030,
    '' : 0,
    #1 digit 个
    '零' : 0,
    '一' : 1,
    '二' : 2,
    '三' : 3,
    '四' : 4,
    '五' : 5,
    '六' : 6,
    '七' : 7,
    '八' : 8,
    '九' : 9,
    #2 digits 十
    '十' : 10,
    '十一' : 11,
    '二十' : 20,
    '二十一' : 21,
    #3 digits 百
    '一百' : 100,
    '一百零一' : 101,
    '一百一十' : 110,
    '一百二十三' : 123,
    #4 digits 千
    '一千' : 1000,
    '一千零一' : 1001,
    '一千零一十' : 1010,
    '一千一百' : 1100,
    '一千零二十三' : 1023,
    '一千二百零三' : 1203,
    '一千二百三十' : 1230,
    #5 digits 万
    '一万' : 10000,
    '一万零一' : 10001,
    '一万零一十' : 10010,
    '一万零一百' : 10100,
    '一万一千' : 11000,
    '一万零一十一' : 10011,
    '一万零一百零一' : 10101,
    '一万一千零一' : 11001,
    '一万零一百一十' : 10110,
    '一万一千零一十' : 11010,
    '一万一千一百' : 11100,
    '一万一千一百一十' : 11110,
    '一万一千一百零一' : 11101,
    '一万一千零一十一' : 11011,
    '一万零一百一十一' : 10111,
    '一万一千一百一十一' : 11111,
    #6 digits 十万
    '十万零二千三百四十五' : 102345,
    '十二万三千四百五十六' : 123456,
    '十万零三百五十六' : 100356,
    '十万零三千六百零九' : 103609,
    #7 digits 百万
    '一百二十三万四千五百六十七' : 1234567,
    '一百零一万零一百零一' : 1010101,
    '一百万零一' : 1000001,
    #8 digits 千万
    '一千一百二十三万四千五百六十七' : 11234567,
    '一千零一十一万零一百零一' : 10110101,
    '一千万零一' : 10000001,
    #9 digits 亿
    '一亿一千一百二十三万四千五百六十七' : 111234567,
    '一亿零一百零一万零一百零一' : 101010101,
    '一亿零一' : 100000001,
    #10 digits 十亿
    '十一亿一千一百二十三万四千五百六十七' : 1111234567,
    #11 digits 百亿
    '一百一十一亿一千一百二十三万四千五百六十七' : 11111234567,
    #12 digits 千亿
    '一千一百一十一亿一千一百二十三万四千五百六十七' : 111111234567,
    #13 digits 万亿
    '一万一千一百一十一亿一千一百二十三万四千五百六十七' : 1111111234567,
    #14 digits 十万亿
    '十一万一千一百一十一亿一千一百二十三万四千五百六十七' : 11111111234567,
    #17 digits 亿亿
    '一亿一千一百一十一万一千一百一十一亿一千一百二十三万四千五百六十七' : 11111111111234567,
    'hah': 0,
    '一百哈哈': 100
    }

    for each in test_map:
        try:
            assert(test_map[each] == convertChineseDigitsToArabic(each))
        except:
            print(each, test_map[each], convertChineseDigitsToArabic(each))