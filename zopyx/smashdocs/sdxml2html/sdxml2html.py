# -*- coding: utf-8 -*-

################################################################
# zopyx.plone.smashdocs
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import os
import sys
import tempfile
import lxml.etree


def sdxml2html(in_name, out_name=None):

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
        img.tag = 'img'
        img.attrib['src'] = 'images/' + img.text
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
        caption = node.attrib['caption']
        if caption:
            del node.attrib['caption']
            node.insert(0, lxml.etree.fromstring('<caption>{0}</caption>'.format(caption)))

    head = root.find('head')
    for name in ('language', 'subtitle', 'description', 'footer', 'creator'):
        for node in head.xpath('//{}'.format(name)):
            node.getparent().remove(node)

    body = root.find('body')
    body.insert(0, lxml.etree.fromstring('<link rel="stylesheet" type="text/css" href="styles.css"/>'))
    body.tag = 'div'
    body.attrib['id'] = 'sd-content'

    if not out_name:
        out_name = tempfile.mktemp(suffix='.html')

    with open(out_name, 'wb') as fp:
        fp.write(lxml.etree.tostring(body, encoding='utf8', pretty_print=1))

    return out_name


def sdxml2html_data(xml_data):

    xml_fn = tempfile.mktemp(suffix='.xml')
    with open(xml_fn, 'wb') as fp:
        fp.write(xml_data)

    out_fn = sdxml2html(xml_fn)
    with open(out_fn, 'rb') as fp:
        data = fp.read()
    os.unlink(out_fn)
    os.unlink(xml_fn)
    return data


if __name__ == '__main__':
    print(sdxml2html(sys.argv[-1], 'out.html'))
