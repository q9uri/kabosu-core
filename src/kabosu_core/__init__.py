from kabosu_core.language.ja.g2p import pyopenjtalk
from kabosu_core.types import NjdObject, ExtractedJpObject

class JaExtract ():
    """
    JaExtract  
    self.text: str | None = None  
    self.njd_object: list[NjdObject] | None = None  
    self.fullcontext_label: list[str] | None = None  
    self.after_g2p_lst: list[str] | None  
    """
    def __init__ (self):
        self.text: str | None = None
        self.njd_object: list[NjdObject] | None = None
        self.fullcontext_label: list[str] | None = None
        self.after_g2p_lst: list[str] | None
    
    def nomalize_text (self, text:str):
        """

        """
        text
        
    
    def extract_all(self,
                    text: str | None = None,
                    njd_object: list[NjdObject] | None = None,
                    fullcontext_label: list[str] | None = None
                    ) -> ExtractedJpObject:
        """

        """
        
        if text == None:
            text = self.text

        if njd_object == None:
            njd_object = self.njd_object

        if fullcontext_label == None:
            fullcontext_label = self.fullcontext_label


    
    def extract_fullcontext(self,
                            text: str | None = None
                            ) -> list[str]:
        """

        """
        if text == None:
            text = self.text
        
        self.njd_object =  pyopenjtalk.extract_fullcontext(text)
        return self.njd_object
        
    def run_frontend(self,
                    text: str | None = None
                    ) -> list[NjdObject]:
        """

        """
        if text == None:
            text = self.text
        
        self.fullcontext_label = pyopenjtalk.run_frontend(text)
        return self.fullcontext_label
    
    def make_label(self,
                   njd_object: list[NjdObject] | None = None
                   ) -> list[str]:
        """

        """
        if njd_object == None:
            njd_object = self.njd_object

        self.fullcontext_label = pyopenjtalk.make_label(njd_object)
        return self.fullcontext_label

    def g2p_jp(self,
               text: str | None = None
               ) -> list[str]:
        """

        """
        if text == None:
            text = self.text
        
        self.after_g2p_lst = pyopenjtalk.g2p(text)
        return self.after_g2p_lst