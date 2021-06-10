# CommentedTreeBuilder.py
from xml.etree import ElementTree as ET
    
class CommentedTreeBuilder(ET.TreeBuilder):
    def comment(self, data):
        self.start("comment", {})
        self.data(data)
        self.end("comment")