import codecs

#Спарсить xml документ
def parse_xml_doc(src):

    #Отрезать первую строку, ограниченную символом bracket1 слева и bracket2 справа, возвращает кортеж (вырезенная строка, оставшееся часть)
    def cut_str_in_brackets(string, bracket1, bracket2):
        start = -1
        end = -1
        for i in range(len(string)):
            if string[i] == bracket1 and start == -1:
                start = i
            elif string[i] == bracket2 and not start == -1:
                end = i
                break
        return string[start+1:end], string[end+1:len(string)]

    #Спарсить строку в ковычках, возвращает кортеж (строка, оставшееся часть)
    def parse_str(src):
        return cut_str_in_brackets(src, '"', '"')

    #Спарсить имя атрибута, возвращает кортеж (имя атрибута, оставшееся часть)
    def parse_attribute_name(src):
        for i in range(len(src)):
            if src[i].isalpha():
                for j in range(i+1, len(src)):
                    if not src[j].isalpha():
                        return src[i:j], src[j:len(src)]

    #Спарсить значение атрибута, если он есть, то возвращает кортеж (имя атрибута, оставшаяся часть)
    def parse_attribute_value(src):
        for i in range(len(src)):
            if src[i] == '=':
                return parse_str(src[i:len(src)])

    #Спарсить атрибут целиком, возвращает картеж ((имя атрибута, значение атребута), оставшаяся часть)
    def parse_attribute(src):
        parsed_name = parse_attribute_name(src)
        attribute = parsed_name[0]
        parsed_val = parse_attribute_value(parsed_name[1])
        return ( (attribute, parsed_val[0]), parsed_val[1] )

    #Можно ли спарсить атрибуты из строки
    def can_parse_attribute(src):
        for i in range(len(src)):
            if src[i].isalpha():
                return True
        return False

    #Можно ли спарсить xml-элемент из строки
    def can_parse_element(src):
        for i in range(len(src)-1):
            if src[i] == '<' and src[i+1] != '/':
                return True
        return False

    #Получить все внутренности тега, возвращает кортеж (вырезанный тег и оставшаяся строка)
    def get_inner(src, tag):
        coef = 0 #соотношение открытых и закрытых тегов, контроль вложенных одинаковых тегов
        open_tag = "<"+tag
        close_tag = "</"+tag
        for i in range(len(src) - len(close_tag)):
            if src[i: i+len(close_tag)] == close_tag:
                if coef == 0:
                    return ( src[0:i], src[i+len(close_tag)+1:len(src)] )
                else:
                    coef -= 1
            elif src[i: i+len(open_tag)] == open_tag:
                coef += 1

    #Спарсить один xml-элемент вместе с атребутами, возвращает картеж (спарсенная сущность, осташаяся строка) 
    def parse_element(src):
        #получаем название очередного тега
        element_with_attributes = cut_str_in_brackets(src, '<', '>')
        element_name = element_with_attributes[0].split(' ')[0]

        #получаем атребуты этого тега
        element_attributes = []
        attributes = element_with_attributes[0][len(element_name):len(element_with_attributes[0])]
        while can_parse_attribute(attributes):
            parsed = parse_attribute(attributes)
            element_attributes.append(parsed[0])
            attributes = parsed[1]

        #если тег однолинейный, то заканчиваем
        if element_with_attributes[0][len(element_with_attributes[0]) - 1] == '/':
            return( (element_name, element_attributes), element_with_attributes[1] )

        #парсим один тег внутри
        inner = get_inner(element_with_attributes[1], element_name)
        element_attributes.append(parse_element_list(inner[0]))
        return( (element_name, element_attributes), inner[1])

    #Спарсить несколько строк xml-элементов
    def parse_element_list(src):
        elements = []
        while can_parse_element(src):
            parsed = parse_element(src)
            src = parsed[1]
            elements.append(parsed[0])
        return elements
    
    return parse_element_list(src)

#Получить json-строку, спарсенной сущности
def entity_in_json(ent):
    json_string = ""
    def print_json(entity):
        nonlocal json_string
        if type(entity) == str and len(entity) != 0:
            json_string += '"' + entity + '"'

        elif type(entity) == list and len(entity) != 0:
            for i in range(len(entity)):
                print_json(entity[i])
                if i != len(entity) - 1:
                    json_string += ","
        elif type(entity) == tuple and len(entity) != 0:
            print_json(entity[0])
            json_string += ":"
            if type(entity[1]) == str:
                json_string +=  '"' + entity[1] + '"'
            else:
                json_string += "{"
                print_json(entity[1])
                json_string += "}"

    print_json(ent)
    return "{"+ json_string + "}"

#читаем xml-файл
xml_path = r"E:\Programming\GitRepositories\xml-parser\wednesday.xml"
f = open(xml_path, 'r', encoding="utf-8")
xml_text = ' '.join(f.readlines())
f.close()

#Почему-то приписывается в начале файла "\ufeff", пофикшу
start_utf = "\ufeff"
sec = xml_text[0:len(start_utf)]
if start_utf == xml_text[0:len(start_utf)]:
    xml_text = xml_text[len(start_utf):len(xml_text)]

#Парсю XML, сохраняю в json
parsed_entities = parse_xml_doc(xml_text)
json_text = entity_in_json(parsed_entities)

#Вывожу в json-файл
json_path = r"E:\Programming\GitRepositories\xml-parser\wednesday.json"
f = open(json_path, 'w', encoding="utf-8")
f.write(json_text)
f.close()