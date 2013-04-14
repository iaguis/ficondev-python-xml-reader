# -*- coding: utf-8 -*-
import re
from sets import Set

banned_list = ["<comment>", "</comment>", "<when>", "</when>", "<quality>", "</quality>", "<up>", "</up>", "<down>",
               "</down>"]
banned_tags = Set(banned_list)
tag_stack = []


class Torrent:
    def __init__(self, id, title, magnet, size, seeders, leechers, quality, uploaded, comments):
        self.id = id
        self.title = title
        self.magnet = magnet
        self.size = size
        self.seeders = seeders
        self.leechers = leechers
        self.quality = quality
        self.uploaded = uploaded
        self.comments = comments

    def __str__(self):
        return "{id:" + str(self.id) + ", title:" + self.title + '}'

    def __repr__(self):
        return self.title


def parse_line_content(line):

    regex = re.compile("<[a-zA-Z]+>([^<>]+)</[a-zA-Z]+>")
    try:
        result = regex.search(line).groups()[0]
        return result
    except:
        return None


def get_line_tag(line):
    try:
        if '/torrent' in line:
            regex = re.compile("(</[a-zA-Z]+>)")
            return regex.search(line).groups()[0]
        regex = re.compile("(<[a-zA-Z]+>)|")

        return regex.search(line).groups()[0]
    except:
        return None


def build_object(data):
    try:
        id = data['id']
        title = data['title']
        magnet = data['magnet']
        size = data['size']
        seeders = data['seeders']
        leechers = data['leechers']
        uploaded = data['uploaded']
        return Torrent(id, title, magnet, size, seeders, leechers, None, uploaded, None)
    except:
        return None


def remove_trash(line):
    line = line.replace('\n', '')
    if len(line) == 0:
        return ""
    line = line.replace('&gt;', '>')
    line = line.replace('&lt;', '<')
    line = line.replace('<br />', '')
    return line


def parse(filename):
    result = []
    data = None
    xml_file = open(filename)
    for line in xml_file:
        line = remove_trash(line)
        if len(line) == 0:
            continue
        if not line.endswith('>'):
            tag_stack.append(line)
            continue
        else:
            if len(tag_stack) > 0:
                while len(tag_stack) > 0:
                    line += tag_stack.pop()
            key = get_line_tag(line)

            if key is None or key in banned_tags:
                continue
            if '/' in key:
                if key == "</torrent>":
                    object = build_object(data)
                    if object is not None:
                        result.append(object)
                else:
                    continue

            if key == "<torrent>":
                data = {}
            value = parse_line_content(line)

            if value is not None:
                if key == "comment":
                    data.setdefault(key[1:-1], []).append(value)
                else:
                    data[key[1:-1]] = parse_line_content(line)

    return result


def search(items, title='', minsize=0, maxsize=9999999999999, minseeders=0, maxleechers=99999999):
    result = []
    for item in items:
        if title in item.title and minsize <= int(item.size) and minseeders <= int(item.seeders) and maxsize >= int(
                item.size) and maxleechers >= int(item.leechers):
            result.append(item)

    return result


def delete(items, id=-1, title=None):
    result = []
    for item in items:
        if id <> int(item.id) and (title is None or title not in item.title):
            result.append(item)
    return result


def create(items, id, title, magnet, size, seeders, leechers, quality, uploaded, comments):
    items.append(Torrent(id, title, magnet, size, seeders, leechers, quality, uploaded, comments))


def update(items, torrent):
    for i in range(len(items)):
        if int(items[i].id) == int(torrent.id):
            items[i] = torrent


def searchTorrent(items):
    title = raw_input("Filtro título contiene:")
    minsize = raw_input("Filtro tamaño mínimo ('' si no se quiere): ")
    if minsize == '':
        minsize = 0
    maxsize = raw_input("Filtro tamaño máximo ('' si no se quiere): ")
    if maxsize == '':
        maxsize = 9999999999999
    minseeders = raw_input("Filtro número mínimo de seeders ('' si no se quiere): ")
    if minseeders == '':
        minseeders = 0
    maxleechers = raw_input("Filtro número máximo de leechers ('' si no se quiere): ")
    if maxleechers == '':
        maxleechers = 9999999999999
    print("BUSCANDO...")
    try:
        filtered_items = search(items, title, minsize, maxsize, minseeders, maxleechers)
    except:
        filtered_items = []
    print("\nRESULTADO\n------")
    if filtered_items is not None:
        for item in filtered_items:
            print(item.__str__())


def createTorrent(items):
    try:
        id = int(raw_input("Id: "))
        title = raw_input("Título: ")
        magnet = raw_input("Magnet: ")
        size = int(raw_input("Tamaño: "))
        seeders = int(raw_input("Seeders: "))
        leechers = int(raw_input("Leechers: "))
        quality = raw_input("Quality: ")
        uploaded = raw_input("Uploaded: ")
        comments = raw_input("Comments: ")
        create(items, id, title, magnet, size, seeders, leechers, quality, uploaded, comments)
    except:
        print("Parametros invalidos :(")
        createTorrent(items)


def deleteTorrent(items):
    id = raw_input("Id: ('' si no interesa): ")
    if id == '':
        id = -1
    title = raw_input("Título ('' si no interesa): ")
    if title == '':
        title = None
    delete(items, id, title)


def updateTorrent(items):
    id = int(raw_input("Id: "))
    title = raw_input("Título: ")
    magnet = raw_input("Magnet: ")
    size = raw_input("Tamaño: ")
    seeders = raw_input("Seeders: ")
    leechers = raw_input("Leechers: ")
    quality = raw_input("Quality: ")
    uploaded = raw_input("Uploaded: ")
    comments = raw_input("Comments: ")
    update(items, Torrent(id, title, magnet, size, seeders, leechers, quality, uploaded, comments, ))


def menu(items):
    print("1. Buscar un torrent")
    print("2. Crear un torrent")
    print("3. Eliminar un torrent")
    print("4. Actualizar un torrent")
    print("\n--------------------")
    print("0. Bye bye")
    option = int(raw_input('Opción: '))
    if option == 1:
        searchTorrent(items)
        menu(items)
    elif option == 2:
        createTorrent(items)
        menu(items)
    elif option == 3:
        items = deleteTorrent(items)
        menu(items)
    elif option == 4:
        updateTorrent(items)
        menu(items)
    else:
        exit()



items = parse('rich.xml')
menu(items)

