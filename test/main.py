import sys

sys.path.append(r"D:\GIT\clovers-utils")
from clovers_utils.linecard import FontManager, linecard


text = """
[center][font size = 80,name = simfang]linecard介[font color = red]绍
[style color = green,height = 80]----
linecard 是一个简易的文字转图片的函数，使用python pillow
文字的格式控制是通过文字内嵌入的[标签]控制
下面是标签的格式介绍
[font size = 50]横线
如果本行文字是 {----}（四个短线）那么这一行会被渲染为横线
[font size = 50]原样输出
需要原样输出的文字要被包裹在大括号{{}}里。
大括号内的内容可以嵌套，但是不会出现不嵌套的两个封闭大括号
例下面高光部分为提取原样文本
[font name=simsun,highlight=#CCCCCC]他们{{}[font highlight=yellow]从{{}充满[font highlight=#CCCCCC]{}}迷雾的{{}[font highlight=yellow]远方{}}策马缓缓而来[font highlight=#CCCCCC ]{}}，口中{{}[font highlight = yellow]重复{{}哼着一段{}}单调动听[font highlight=#CCCCCC ]{}}的旋律。
[font size = 50]字体控制标签
[font size=50,name=simsun,color=blue,highlight=yellow]{[font size=50,name=simsun,color=blue,highlight=yellow]}
[font size = 50]对齐标签
[left]{[left]}左对齐
[center]{[center]}居中对齐
[right]{[right]}右对齐
[pixel 100]{[pixel 100]}指定像素
[pixel 800]{[pixel 800]}指定像素
也可以不同对齐方法不换行
[left]{[left]}左对齐[right]{[right]}右对齐[center]{[center]}居中对齐
[pixel 100]{[pixel 100]}指定像素[pixel 800]{[pixel 800]}指定像素
[font size = 50]继承格式
[font name=simfang]{[font name=simfang]}渲染文字的标签效果是定义此行效果，换行后会恢复默认效果，可以在标记{[passport]}让下一行继承本行的格式[passport]{[passport]}
本段文本真正的控制标签在原样输出前[passport]{[passport]}
[font highlight=yellow]{[font highlight=yellow]}这里是第一行[passport]{[passport]}
这里是第二行[passport]{[passport]}
[font highlight=]{[font highlight=]}这里是第三行[style color = blue]{[style color = blue]}[passport]{[passport]}
----
[font size = 50]换行标签
{[autowrap]}如果本行文字太长，并且图片范围不够大，则会自动换行。
{[noautowrap]}本行文字禁止自动换行。即使会超出图片范围。
----
[font size = 50]自动换行[pixel 810]行样式标签
[nowrap][autowrap][font size = 30,highlight = yellow][style width = 790]你循声望去：那是一队骑兵，他们从充满迷雾的远方策马缓缓而来，口中重复哼着一段单调动听的旋律。[font highlight = ]你记得那首歌，但想不起来它的名字，你只知道，这是一个伟大时代的缩影；你不由得被骑兵们的声音所感染，跟着哼唱起来。你静静看着他们，看着他们的身形逐渐在眼中放大，身影逐渐清晰；你忽然发现他们的声音竟是如此的高昂，他们的神情如此乐观坚定！在一阵恍惚中，他们已经掠过了你，以破竹之势踏步前行。
[pixel 820][font size = 30]{[style]} 目前可以控制本行长宽和颜色 
[pixel 820][font size = 30]例子：{[style height = 80,width = 400, color = white]}
[pixel 820][style height = 80, color = white][font highlight = #006030,name = simfang]本行设置高度为80
[pixel 820][font highlight = #006030,name = simfang, color = white]第二行
[pixel 820][style width = 400, color = white][font highlight = #006030,name = simfang]本行设置宽度为400
[pixel 820][font highlight = #006030,name = simfang, color = white]第二个第二行
----
[font size = 50]Todo
无
""".strip(
    "\n"
)

if __name__ == "__main__":

    fm = FontManager("msyh", ["simfang"], [40])

    image = linecard(text, fm, 40, width=1600, bg_color="#FFFFFF", autowrap=True, padding=(20, 40))

    image.show()
