from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage
import json

class TravelMemory(ConversationBufferWindowMemory):
    def __init__(self, k=10):
        super().__init__(k=k, return_messages=True)
        self.user_preferences = {}
        
    def save_context(self, inputs, outputs):
        """Sauvegarde le contexte et extrait les préférences"""
        super().save_context(inputs, outputs)
        
        # Extrait et sauvegarde les préférences mentionnées
        user_input = inputs.get('input', '')
        self._extract_and_save_preferences(user_input)
    
    def _extract_and_save_preferences(self, user_input):
        """Extrait les préférences du texte utilisateur"""
        # Logique d'extraction des préférences
        # (déjà implémentée dans la classe principale)
        pass
    
    def get_preferences_summary(self):
        """Retourne un résumé des préférences collectées"""
        return self.user_preferences