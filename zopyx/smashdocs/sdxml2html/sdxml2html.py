
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

    for node in root.xpath('//paragraph'):
        node.tag = 'p'
        alignment = node.attrib.get('alignment')
        if alignment:
            cls = node.attrib.get('class', '')
            cls += ' align-{}'.format(alignment)
            node.attrib['class'] = cls
        indent = node.attrib.get('indent')
        if indent:
            cls = node.attrib.get('class', '')
            cls += ' indent-{}'.format(indent)
            node.attrib['class'] = cls

    if not out_name:
        out_name = tempfile.mktemp(suffix='.html')
    
    with open(out_name, 'wb') as fp:
        fp.write(lxml.etree.tostring(root, pretty_print=1))
    
    return out_name


if __name__ == '__main__':
    print(sdxml2html(sys.argv[-1]))
