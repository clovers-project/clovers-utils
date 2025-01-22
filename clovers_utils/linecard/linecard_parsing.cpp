#include <Python.h>
#include <vector>

static PyObject *parse_str(PyObject *self, PyObject *args);
static PyMethodDef moduleMethods[] = {
    {"parse_str", parse_str, METH_O, "parse linecard string"},
    {NULL, NULL, 0, NULL}};
static struct PyModuleDef linecard_parsing = PyModuleDef{
    PyModuleDef_HEAD_INIT,
    "linecard_parsing",
    "I hope it's faster than regular expression",
    -1,
    moduleMethods,
};

extern "C" PyMODINIT_FUNC PyInit_linecard_parsing(void)
{
    return PyModule_Create(&linecard_parsing);
}

char *substr(const char *str, long start, long end)
{
    long l = end - start;
    char *result = new char[l + 1];
    for (long i = 0; i < l; i++)
    {
        result[i] = str[start + i];
    }
    result[l] = '\0';
    return result;
}

static bool startswith(const char *str, const char *start)
{
    for (long iStr = 0, iTag = 0;; ++iStr, ++iTag)
    {
        if (start[iTag] == '\0')
        {
            return true;
        }
        if (str[iStr] == '\0')
        {
            return false;
        }
        if (str[iStr] != start[iTag])
        {
            return false;
        }
    }
}

static struct Tag
{
    const char name;
    const char *value;
    const bool dynamic = true;
};

class tagsText
{
private:
    long _len = 0;

public:
    char *text;
    std::vector<Tag> args;
    tagsText(const char *rawtext)
    {
        while (rawtext[_len++] != '\0')
            ;
        text = new char[_len];

        for (long i = 0; i < _len; i++)
        {
            text[i] = rawtext[i];
        }
        char tagName = '\0';
        long tagL;
        long tagargsL;
        for (long i = 0, rawChecked = 0; i < _len; ++i)
        {
            if (text[i] == '{' and i > rawChecked)
            {
                bool inRaw = false;
                long rawL = i;
                long rawR;
                for (long iTmp = i; iTmp < _len; iTmp++)
                {
                    if (text[iTmp] == '}')
                    {
                        rawR = iTmp;
                        inRaw = true;
                        continue;
                    }
                    if (inRaw and (text[iTmp] == '{' or text[iTmp] == '\0'))
                    {
                        i = rawR;
                        rawChecked = iTmp - 1;
                        args.push_back(Tag{'r', substr(rawtext, rawL + 1, rawR)});
                        text[rawL] = '\0';
                        text[rawR] = '\0';
                        break;
                    }
                }
            }
            else if (text[i] == '[')
            {

                if (startswith(text + i + 1, "center]"))
                {
                    args.push_back(Tag{'a', "center", false});
                    text[i] = '\0';
                    i += 7;
                    text[i] = '\0';
                }
                else if (startswith(text + i + 1, "left]"))
                {
                    args.push_back(Tag{'a', "left", false});
                    text[i] = '\0';
                    i += 5;
                    text[i] = '\0';
                }
                else if (startswith(text + i + 1, "right]"))
                {
                    args.push_back(Tag{'a', "right", false});
                    text[i] = '\0';
                    i += 6;
                    text[i] = '\0';
                }
                else if (startswith(text + i + 1, "nowrap]"))
                {
                    args.push_back(Tag{'t', "nowrap", false});
                    text[i] = '\0';
                    i += 7;
                    text[i] = '\0';
                }
                else if (startswith(text + i + 1, "autowrap]"))
                {
                    args.push_back(Tag{'t', "autowrap", false});
                    text[i] = '\0';
                    i += 9;
                    text[i] = '\0';
                }
                else if (startswith(text + i + 1, "noautowrap]"))
                {
                    args.push_back(Tag{'t', "noautowrap", false});
                    text[i] = '\0';
                    i += 11;
                    text[i] = '\0';
                }
                else if (startswith(text + i + 1, "passport]"))
                {
                    args.push_back(Tag{'p', "passport", false});
                    text[i] = '\0';
                    i += 9;
                    text[i] = '\0';
                }
                else if (startswith(text + i + 1, "pixel "))
                {
                    tagL = i;
                    i += 7;
                    tagargsL = i;
                    tagName = 'a';
                }
                else if (startswith(text + i + 1, "style "))
                {
                    tagL = i;
                    i += 7;
                    tagargsL = i;
                    tagName = 's';
                }
                else if (startswith(text + i + 1, "font "))
                {
                    tagL = i;
                    i += 6;
                    tagargsL = i;
                    tagName = 'f';
                }
            }
            else if (text[i] == ']' and tagName != '\0')
            {
                args.push_back(Tag{tagName, substr(rawtext, tagargsL, i)});
                text[tagL] = '\0';
                text[i] = '\0';
                tagName = '\0';
            }
        }
        initText();
    }
    ~tagsText()
    {
        delete[] text;
        for (auto &tag : args)
        {
            if (tag.dynamic)
            {
                delete[] tag.value;
            }
        }
    }
    void extract(const char *rawtext, long l, long r, char type)
    {
        args.push_back(Tag{type, substr(rawtext, l + 1, r)});
        text[l] = '\0';
        text[r] = '\0';
    }
    char *initText()
    {
        long j = 0;
        bool flag = true;
        for (long i = 0; i < _len; ++i)
        {
            if (text[i] == '\0')
            {
                flag = !flag;
                if (flag)
                {
                    text[j++] = '{';
                    text[j++] = '}';
                }
            }
            else if (flag)
            {
                text[j++] = text[i];
            }
        }
        text[j] = '\0';
        return text;
    }
};

static PyObject *parse_str(PyObject *self, PyObject *args)
{
    if (!PyUnicode_Check(args))
    {
        PyErr_SetString(PyExc_TypeError, "Expected a string argument");
        return NULL;
    }
    const char *input_string = PyUnicode_AsUTF8(args);
    if (input_string == NULL)
    {
        return NULL;
    }
    tagsText result = tagsText(input_string);
    PyObject *result_list = PyList_New(result.args.size());
    long i = 0;
    for (auto &tag : result.args)
    {
        PyObject *tag_tuple = PyTuple_New(2);
        PyTuple_SetItem(tag_tuple, 0, PyBytes_FromStringAndSize(&tag.name, 1));
        PyTuple_SetItem(tag_tuple, 1, PyUnicode_FromString(tag.value));
        PyList_SetItem(result_list, i++, tag_tuple);
    }
    PyObject *result_tuple = PyTuple_Pack(2, PyUnicode_FromString(result.text), result_list);
    return result_tuple;
}