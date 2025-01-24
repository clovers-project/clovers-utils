import re
from linecard_parsing import parse_str
from main import text as rawtext


def raw_text(text: str):
    for i, char in enumerate(text):
        if char == "{":
            break
    else:
        return []
    raw_list = []
    raw_end_flag = False
    l: int = 0
    tmp_r: int
    new_text = text[i:]
    return_text = text[:i]
    new_textl = 0
    for i, char in enumerate(new_text):
        if char == "}":
            tmp_r = i
            raw_end_flag = True
        elif raw_end_flag and char == "{":
            raw_list.append(new_text[l : tmp_r + 1])
            return_text += new_text[new_textl : l + 1]
            new_textl = tmp_r
            raw_end_flag = False
            l = i
    else:
        if raw_end_flag:
            raw_list.append(new_text[l : tmp_r + 1])
            return_text += new_text[new_textl : l + 1]
            new_textl = tmp_r
        return_text += new_text[new_textl:]

    return raw_list, return_text


class linecard_pattern:
    align = re.compile(r"\[left\]|\[right\]|\[center\]|\[pixel\s([^]]*)\]")
    font = re.compile(r"\[font\s*([^]]*)\]")
    style = re.compile(r"\[style\s*([^]]*)\]")
    passport = re.compile(r"\[passport\]")
    nowrap = re.compile(r"\[nowrap\]")
    autowrap = re.compile(r"\[autowrap\]")
    noautowrap = re.compile(r"\[noautowrap\]")
    raw = re.compile(r"\{([^}]*)\}")


def preprocess_text(text: str):
    text = linecard_pattern.raw.sub("{}", text)
    # all_rawtext, text = raw_text(text)
    text = linecard_pattern.align.sub("{}", text)
    text = linecard_pattern.font.sub("{}", text)
    text = linecard_pattern.style.sub("{}", text)
    text = linecard_pattern.nowrap.sub("{}", text)
    text = linecard_pattern.autowrap.sub("{}", text)
    text = linecard_pattern.noautowrap.sub("{}", text)
    text = linecard_pattern.passport.sub("{}", text)

    return text


text1 = preprocess_text(rawtext)
text2, args = parse_str(rawtext)

print(text1 == text2)

import timeit

print(timeit.timeit(lambda: preprocess_text(rawtext), number=10000))
print(timeit.timeit(lambda: parse_str(rawtext), number=10000))
