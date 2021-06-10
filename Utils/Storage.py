import pickle
from Model.Data import *
from PyQt5.QtWidgets import QErrorMessage


def handleError(error):
    em = QErrorMessage.qtHandler()
    em.showMessage(str(error))


def save(filename, aiml):
    try:
        with open(filename+'.aib', 'wb') as output:
            pickle.dump(aiml, output, pickle.HIGHEST_PROTOCOL)
    except Exception as ex:
        handleError(ex)
        print("exception caught!")
        print(ex)


def restore(filename):
    try:
        with open(filename+'.aib', 'rb') as input_file:
            aiml2 = pickle.load(input_file)
        return aiml2
    except Exception as ex:
        handleError(ex)
        print("exception caught!")
        print(ex)


def exportAIML(filename, aiml):
    try:
        with open(filename+'.aiml', 'w') as output:
            output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            output.write(str(aiml))
    except Exception as ex:
        handleError(ex)
        print("exception caught!")
        print(ex)


tag_list = {"aiml": AIML,
            "topic": Topic,
            "category": Category,
            "pattern": Pattern,
            "template": Template,
            "condition": Condition,
            "li": ConditionItem,
            "random": Random,
            "set": Set,
            "think": Think,
            "that": That,
            "oob": Oob,
            "robot": Robot,
            "options": Options,
            "option": Option,
            "image": Image,
            "video": Video,
            "filename": Filename,
            "srai": Srai,
            "bot": Bot,
            "star": Star,
            "comment": Comment,
            "map": Map}


def decode_tag(tag_type):
    if tag_type in tag_list:
        return tag_list[tag_type]()
    return False

def recursive_decoding(head, tag_xml):
    try:
        for child in tag_xml:
            # print(f"Recursive_decoding. tag type: {child.tag}")
            tag_obj = decode_tag(child.tag.lower())
            if(tag_obj != False):
                if child.text:
                    if child.text.strip():
                        # print("Appending text: {}\nto: {}".format(child.text.strip(), tag_obj))
                        tag_obj.append(child.text.strip())
                        # print("tag_obj: {}".format(tag_obj))
                tag_obj.attrib = child.attrib
                try:
                    head.append(tag_obj)
                except Exception as ex:
                    print(ex)
                    parents = child.findall('..')
                    handleError('{} tag not allowed inside that parent tag. Tags placed missproperly don\'t get compiled' \
                                ' and are left out during export (Needs to be updated!) \n Exception raised - {}.'.format(tag_obj.type, ex))
                if child.tail:
                    if child.tail.strip():
                        head.append(child.tail.strip()) 
            else:
                head.append(ET.tostring(child, encoding="unicode"))
            recursive_decoding(tag_obj, child)
    except Exception as ex:
        print("Exception caught in Storage - recursive_decoding()")
        handleError(ex)
        print(ex)


def importAIML(filename, tempFile=False):
    # Use custom parser to include comments
    parser = ET.XMLParser(target=CommentedTreeBuilder())
    print("parsing file into tree")
    try:
        if tempFile:
            tree = ET.parse(filename, parser)
        else:
            tree = ET.parse(filename+".aiml", parser)
    except Exception as ex:
        print("Exception caught in Storage - importAIML()")
        print(ex)
        handleError(ex)
    try:
        print("getting root of the tree")
        root = tree.getroot()
        return decode_root(root)
    except Exception as ex:
        handleError(ex)
        print("Exception caught in Storage - importAIML()")
        print(ex)

def parse_text(contents):
    print("getting root of the tree")
    try:
        parser = ET.XMLParser(target=CommentedTreeBuilder())
        root = ET.fromstring(contents, parser)
        print(root.text)
        return decode_root(root)
    except Exception as ex:
        handleError("{} Check for a missing \'/\' or a missing closing tag.".format(ex))
        print("exception caught in trying to parse the string")
        print(ex)
        return -1
    
def decode_root(root):
    try:
        aiml3 = None
        if root.tag.lower() != "aiml":
            print("This is not an AIML file.")
            print(root.tag)
        else:
            aiml3 = AIML()
            print("decoding file")
            recursive_decoding(aiml3, root)
        return aiml3
    except Exception as ex:
        handleError(ex)
        print("exception caught trying to decode tree")
        print(ex)    

def compileToAIML(str_contents):
    try:
        aiml = parse_text(str_contents)
        if aiml == -1:
            print("error while compiling")
            return -1
        print("Successfully parsed file")
        return aiml
    except Exception as ex:
        handleError(ex)
        print("exception trying to compile project to AIML")
        print(ex)