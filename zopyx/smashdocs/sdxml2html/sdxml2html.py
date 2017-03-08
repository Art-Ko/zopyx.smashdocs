# -*- coding: utf-8 -*-

################################################################
# zopyx.plone.smashdocs
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import os
import sys
import copy
import tempfile
import lxml.etree
from xml.sax.saxutils import escape

html_template = """
<html>
    <head>
    </head>
    <body>
    </body>
</html>
"""


def sdxml2html(in_name, out_name=None, css_name='styles.css', image_prefix='images', html_wrapper=False):

    with open(in_name, 'rb') as fp:
        root = lxml.etree.fromstring(fp.read())

    for node in root.xpath('//smashdoc'):
        node.tag = 'html'

    for node in root.xpath('//document'):
        node.tag = 'body'

    for node in root.xpath('//meta'):
        node.tag = 'head'

    for node in root.xpath('//heading'):
        level = node.attrib.get('level', '0')
        node.tag = 'h{}'.format(int(level) +1)

    for img in root.xpath('//image'):

        attrib = copy.copy(img.attrib)
        img_src = img.text
        if image_prefix:
            img_src = '{}/{}'.format(image_prefix, img_src)
        img_caption = attrib.get('caption')
        num_enabled = attrib.get('num-enabled')

        new_img = lxml.etree.fromstring('<img src="{0}" width="{1}"/>'.format(img_src, attrib['width']))
        img.insert(0, new_img)

        if img_caption:
            fig_caption = lxml.etree.fromstring(u'<figcaption num-enabled="{1}">{0}</figcaption>'.format(img_caption, num_enabled))
            img.append(fig_caption)
            del img.attrib['caption']
        img.tag = 'figure'
        img.text = None

    for node in root.xpath('//*[@indent]'):
        value = node.attrib['indent']
        cls = node.attrib.get('class', '')
        cls += ' indent-{}'.format(value)
        node.attrib['class'] = cls
        del node.attrib['indent']

    for node in root.xpath('//*[@alignment]'):
        value = node.attrib['alignment']
        cls = node.attrib.get('class', '')
        cls += ' align-{}'.format(value)
        node.attrib['class'] = cls
        del node.attrib['alignment']

    for node in root.xpath('//*[@text-align]'):
        value = node.attrib['text-align']
        cls = node.attrib.get('class', '')
        cls += ' text-align-{}'.format(value)
        node.attrib['class'] = cls
        del node.attrib['text-align']

    for node in root.xpath('//*[@vertical-align]'):
        value = node.attrib['vertical-align']
        cls = node.attrib.get('class', '')
        cls += ' vertical-align-{}'.format(value)
        node.attrib['class'] = cls
        del node.attrib['vertical-align']

    for node in root.xpath('//*[@size]'):
        del node.attrib['size']

    for node in root.xpath('//paragraph'):
        node.tag = 'p'

    for node in root.xpath('//column_width'):
        node.tag = 'colgroup'

    for node in root.xpath('//item'):
        node.tag = 'col'
        node.attrib['width'] = node.text
        node.text = None

    for node in root.xpath('//table'):
        num_enabled = node.attrib.get('num-enabled')
        caption = node.attrib['caption']
        if caption:
            del node.attrib['caption']
            if num_enabled:
                node.insert(0, lxml.etree.fromstring('<caption num-enabled="{1}">{0}</caption>'.format(caption, num_enabled)))
            else:
                node.insert(0, lxml.etree.fromstring('<caption>{0}</caption>'.format(caption)))

    footnotes = list()
    for num, node in enumerate(root.xpath('//footnote')):
        node.tag = 'a'
        footnote_text = node.attrib['data-content']
        footnotes.append(dict(num=num+1, text=footnote_text))
        node.attrib['class'] = 'footnote'
        node.attrib['href'] = '#fn-{}'.format(num+1)
        del node.attrib['data-content']
        node.text = None
        node.append(lxml.etree.fromstring(u'<span class="footnote-number" title="{1}">{0}</span>'.format(num+1, escape(footnote_text))))
        node.append(lxml.etree.fromstring(u'<span class="footnote-text">{}</span>'.format(footnote_text)))

    footnotes_list = []
    if footnotes:
        footnotes_list = []
        footnotes_list.append(u'<ul id="footnotes">')
        for d in footnotes:
            footnotes_list.append(u'<li class="footnote">')
            footnotes_list.append(u'<a name="fn-{0}" id="fn-{0}"></a><span class="footnote-num">{0}</span><span>{1}</span>'.format(d['num'], d['text']))
            footnotes_list.append(u'</li>')
        footnotes_list.append(u'</ul>')

    head = root.find('head')
    for name in ('language', 'subtitle', 'description', 'footer', 'creator'):
        for node in head.xpath('//{}'.format(name)):
            node.getparent().remove(node)

    body = root.find('body')
    body.insert(0, lxml.etree.fromstring('<link rel="stylesheet" type="text/css" href="{0}"/>'.format(css_name)))
    body.tag = 'div'
    body.attrib['id'] = 'sd-content'
    if footnotes_list:
        body.append(lxml.etree.fromstring(u''.join(footnotes_list)))

    for node in root.xpath('//*'):
        for name, value in node.attrib.items():
            value = value.strip()
            if value:
                node.attrib[name] = value
            else:
                del node.attrib[name]

    if not out_name:
        out_name = tempfile.mktemp(suffix='.html')

    if html_wrapper:
        import pdb; pdb.set_trace() 
        root2 = lxml.etree.fromstring(html_template)
        for link in body.xpath('//link'):
            root2.find('head').append(copy.deepcopy(link))
            link.getparent().remove(link)
        root2.find('body').insert(0, lxml.etree.fromstring(lxml.etree.tostring(body, encoding='utf-8', pretty_print=1)))

        with open(out_name, 'wb') as fp:
            fp.write(lxml.etree.tostring(root2, encoding='utf8', pretty_print=1))

    else:

        with open(out_name, 'wb') as fp:
            fp.write(lxml.etree.tostring(body, encoding='utf8', pretty_print=1))

    return out_name


def sdxml2html_data(xml_data, image_prefix='images', html_wrapper=False):

    xml_fn = tempfile.mktemp(suffix='.xml')
    with open(xml_fn, 'wb') as fp:
        fp.write(xml_data)

    out_fn = sdxml2html(xml_fn, html_wrapper=html_wrapper)
    with open(out_fn, 'rb') as fp:
        data = fp.read()
    os.unlink(out_fn)
    os.unlink(xml_fn)
    return data


if __name__ == '__main__':
    print(sdxml2html(sys.argv[-1], 'out.html', html_wrapper=True))
