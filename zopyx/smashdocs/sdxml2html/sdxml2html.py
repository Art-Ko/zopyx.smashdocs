
import sys
import tempfile
import lxml.etree


MAP = {
    'alignment': 'text-align',
    'indent': ('indent-level', 'value'),
    'text-align': 'text-align',
    'vertical-align': 'vertical-align',
    'border-right': 'border-right',
    'border-bottom': 'border-bottom',
    'border-top': 'border-top',
    'border-left': 'border-left'
}


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

#    for old_attrib, new_attrib in MAP.items():
#        for node in root.xpath('//*[@{0}]'.format(old_attrib)):
#            value = node.attrib[old_attrib]
#            cls = node.attrib.get('class', '')
#            if isinstance(new_attrib, tuple):
#                new_attrib, method = new_attrib
#                cls += ' {}-{}'.format(new_attrib, value)
#            else:
#                cls += ' {}'.format(new_attrib)
#            node.attrib['class'] = cls
#            del node.attrib[old_attrib]


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

    head = root.find('head')
    head.append(lxml.etree.fromstring('<link rel="stylesheet" type="text/css" href="styles.css"/>'))
    for name in ('language', 'subtitle', 'description', 'footer', 'creator'):
        for node in head.xpath('//{}'.format(name)):
            node.getparent().remove(node)

    if not out_name:
        out_name = tempfile.mktemp(suffix='.html')
    
    with open(out_name, 'wb') as fp:
        fp.write(lxml.etree.tostring(root, encoding='utf8', pretty_print=1))
    
    return out_name


if __name__ == '__main__':
    print(sdxml2html(sys.argv[-1], 'out.html'))
