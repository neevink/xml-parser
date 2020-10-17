import codecs

#отрезать первую строку, ограниченную символом bracket1 слева и bracket2 справа, возвращает кортеж (вырезенная строка, оставшееся часть)
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

#получить все внутренности тега, возвращает кортеж (вырезанный тег и оставшаяся строка)
def get_inner(src, tag):
    coef = 0 #соотношение открытых и закрытых тегов, контроль вложенных одинаковых тегов
    open_tag = "<"+tag
    close_tag = "</"+tag
    for i in range(len(src) - len(close_tag)):
        #print(src[i: i+len(close_tag)] + "   " + str(coef))
        if src[i: i+len(close_tag)] == close_tag:
            if coef == 0:
                return ( src[0:i], src[i+len(close_tag)+1:len(src)] )
            else:
                coef -= 1
        elif src[i: i+len(open_tag)] == open_tag:
            coef += 1

##Спарсить элемент xml-документа
#def parse_element(src):
#    if not can_parse_element(src):
#        return ()
#
#    element_with_attributes = cut_str_in_brackets(src, '<', '>')
#    if not(len(attributes) > 0 and attributes[len(attributes)-1] == '/'):
#        element_attributes.append(parse_element(get_inner(element_with_attributes[1], element_name)))
#
#    element_name = element_with_attributes[0].split(' ')[0] 
#    element_attributes = [] 
#    attributes = element_with_attributes[0][len(element_name):len(element_with_attributes[0])]
#
#    while can_parse_attribute(attributes):
#        parsed = parse_attribute(attributes)
#        element_attributes.append(parsed[0])
#        attributes = parsed[1]
#
#    if not(len(attributes) > 0 and attributes[len(attributes)-1] == '/'):
#        inner = parse_element(get_inner(element_with_attributes[1], element_name)) #парсим оставшуюся строку
#        element_attributes.append(inner)
#
#    return (element_name, element_attributes)

#Возвращает картеж (спарсенная сущность, осташаяся строка) 
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

    inner = get_inner(element_with_attributes[1], element_name)
    element_attributes.append(parse_element_list(inner[0]))
    #while can_parse_element(inner[0]):
    #    parse_element_list(inner[0])
    
    return( (element_name, element_attributes), inner[1])

def parse_element_list(src):
    elements = []
    while can_parse_element(src):
        parsed = parse_element(src)
        src = parsed[1]
        elements.append(parsed[0])
    return elements

path = "E:\Programming\Python\informatics-lab3\wednesday.xml"
xmlText = open(path, 'r', encoding="utf-8").readlines()

#xmlText = '<lesson name="Дискретная математика"><time time="10:00-11:30" evenweek="false" /> <place audience="2202" building="ул.Ломоносова, д.9, лит. А"/> <teacher name="Поляков Владимир Иванович" /><format format="Очно - дистанционный"/></lesson>'
parsed_entities = parse_element_list(xmlText)
#print(parsed_entities)

def print_json(entity):
    if type(entity) == str and len(entity) != 0:
        print('"' + entity + '"')
    elif type(entity) == list and len(entity) != 0:
        for i in range(len(entity)):
            print_json(entity[i])
            if i != len(entity) - 1:
                print(",")
    elif type(entity) == tuple and len(entity) != 0:
        print_json(entity[0])
        print(":")
        if type(entity[1]) == str:
            print( '"' + entity[1] + '"')
        else:
            print("{")
            print_json(entity[1])
            print("}")
    else:
        return ""


print_json(parsed_entities)
 