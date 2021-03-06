#generic response to handle with commands not was able to understand

import re
import time

#PRODUCTION
from .mockup_conversation import *
from . import whastapp_api
from .DI import (ENV, handlerJson, geocoding)

#DEVELOP
# from mockup_conversation import *
# import whastapp_api
# from DI import (ENV, handlerJson, geocoding)

def isCached(data):
  '''
  :rtype: True = it's cached
          False = it's not cached
  '''
  time_min = time.gmtime().tm_min
  diff_time_min = abs(int(data["time_min"]) - time_min)
  
  #minutes scale
  if(diff_time_min > 2):
    return False

  return True

class PhasesConversation:
  def __init__(self, name, phone, text):
    self.phone = phone
    self.name = name
    self.text = text
    self.address = "Avenida Paulista, São Paulo"
    self.data_to_cache = {
      "namePerson": self.name,
      "phonePerson": self.phone,
      "phaseStagePerson": 0,
      "address": self.address
    }
    self.phase_stage = 0
    self.commands = f'''
        1) Recomendação
        2) Próximos
      '''

  def _updateStage(self, level):
    self.phase_stage = level
    self.data_to_cache["phaseStagePerson"] = self.phase_stage
    self.data_to_cache["address"] = self.address
    
    #must to ben run at root folder project
    handlerJson.writeToJSONFile(self.data_to_cache, "./temp/", self.phone)

  def phase_0(self):
    self._updateStage(1)
    return stage_0(self.name)

  def phase_1(self):
    pattern = re.compile(".*((?P<number>1|2)|(?P<command>ajuda|comer))", re.I | re.M)
    #set to not take duplicate of the same word
    regex_result = pattern.match(self.text)
    
    self.commands = f'''
      1) Ajuda
      2) Comer
    '''

    if(regex_result == None):
      unknow_response(self.commands)
      return -1

    #taking the result obtained from regex_result, which will only one command that not was None
    action = [item for item in regex_result.groupdict().values() if item != None][0].lower()
    if((action == "2") or (action == "comer")):
      self._updateStage(2)

    return stage_1(action)

  def phase_2(self):
    self.address = self.text
    self._updateStage(3)
    return stage_2()

  def phase_3(self):
    pattern = re.compile(".*((?P<number>1|2|3)|(?P<command>recomendação|próximos))", re.I | re.M)
    #set to not take duplicate of the same word
    regex_result = pattern.match(self.text)
    
    self.commands = f'''
      1) Recomendação
      2) Próximos
    '''

    if(regex_result == None):
      return unknow_response(self.commands)

    #taking the result obtained from regex_result, which will only one command that not was None
    action = [item for item in regex_result.groupdict().values() if item != None][0].lower()
    possibles_commands_list = [["1", "recomendação"], ["2", "próximos"]]

    if(action in possibles_commands_list[1]):
      whastapp_api.response_to(stage_3(action), self.phone)
      # print(stage_3(action))

      self._updateStage(6)
      return self.phase_6()
    elif(action in possibles_commands_list[0]):
      whastapp_api.response_to(stage_3(action), self.phone)
      # print(stage_3(action))

      #TODO: Query here to see if number already is in our DB
      is_client = False
      if(is_client):
        self._updateStage(6)
        return self.phase_6()    
      
      self._updateStage(4)
      return stage_4_01()
    else:
      return unknow_response(self.commands)
      
  def phase_4(self):
    pattern = re.compile(".*((?P<number>1|2)|(?P<command>Sim|Não))", re.I | re.M)
    #set to not take duplicate of the same word
    regex_result = pattern.match(self.text)
    
    self.commands = f'''
      1) Sim
      2) Não
    '''

    if(regex_result == None):
      unknow_response(self.commands)
      return -1

    #taking the result obtained from regex_result, which will only one command that not was None
    action = [item for item in regex_result.groupdict().values() if item != None][0].lower()
    possibles_commands_list = [["1", "sim"], ["2", "não"]]

    if(action in possibles_commands_list[1]):
      whastapp_api.response_to(stage_4_99(), self.phone)
      # print(stage_4_99())

      self._updateStage(6)
      return self.phase_6()
    elif(action in possibles_commands_list[0]):
      self._updateStage(4.1)
      return stage_4_02()

    else:
      return unknow_response(self.commands)

  def phase_4_01(self):
    pattern = re.compile(".*((?P<number>1|2|3|4|5|6)|(?P<command>Calmo|Badalado|Retro|Moderno|Simples|Sotisficado))", re.I | re.M)
    #set to not take duplicate of the same word
    regex_result = pattern.match(self.text)
    
    self.commands = f'''
      1) Calmo
      2) Badalado
      3) Retro
      4) Moderno
      5) Simples
      6) Sotisficado 
    '''

    if(regex_result == None):
      unknow_response(self.commands)
      return -1

    #TODO: validation here equal above and save data
    self._updateStage(4.2)
    return stage_4_03()

  def phase_4_02(self):
    pattern = re.compile(".*((?P<number>1|2|3|4|5|6)|(?P<command>Vegana|Churrasco|Japonesa|Chinesa|Nordestina|Italiana))", re.I | re.M)
    #set to not take duplicate of the same word
    regex_result = pattern.match(self.text)
    
    self.commands = f'''
      1) Vegana
      2) Churrasco
      3) Japonesa
      4) Chinesa
      5) Nordestina
      6) Italina
    '''

    if(regex_result == None):
      unknow_response(self.commands)
      return -1

    #TODO: validation here equal above, save data, and trace perfil
    whastapp_api.response_to(stage_4_04(), self.phone)
    # print(stage_4_04())

    self._updateStage(6)
    return self.phase_6()

  def phase_6(self):
    utensilMaps = geocoding.UtensilMaps(ENV.GMAPS_API_TWO)
    restaurantsFound = utensilMaps.topFiveNearbyFoodPlace(self.address)

    self._updateStage(7)
    whastapp_api.response_to(stage_6_01(restaurantsFound), self.phone)
    # print(stage_6_01(restaurantsFound))

    return stage_6_02()

  def phase_7(self):

    pattern = re.compile(".*(?P<number>1|2|3|4|5)", re.I | re.M)
    #set to not take duplicate of the same word
    regex_result = pattern.match(self.text)

    self.commands = f'''
      Selecione um numero de 1 a 5 dos possíveis restaurantes acima
    '''

    #taking the result obtained from regex_result, which will only one command that not was None
    action = [item for item in regex_result.groupdict().values() if item != None][0].lower()
    possibles_commands_list = ["1", "2", "3", "4", "5"]

    if(not (action in possibles_commands_list)):
      unknow_response(self.commands)
      return -1    

class HandlerConversation(PhasesConversation):
  def __init__(self, name, phone, text):
    super().__init__(name, phone, text)
    self.name = name
    self.phone = phone
    self.text = text

  def run(self):
    #must to ben run at root folder project
    data_cached = handlerJson.loadJson("./temp/", self.phone)
    if(data_cached):
      #if it overcome the limit of the 2 min without update, reset the stage
      if(not isCached(data_cached)):
        self._updateStage(0)
        self.phase_stage = 0
      else:
        self.phase_stage = data_cached["phaseStagePerson"]
      #putting address to the class base manipulate
      if("address" in data_cached):
        self.address = data_cached["address"]

    phases = {
      0: self.phase_0,
      1: self.phase_1,
      2: self.phase_2,
      3: self.phase_3,
      4: self.phase_4,
      4.1: self.phase_4_01,
      4.2: self.phase_4_02
    }

    try:
      return phases[self.phase_stage]()
    except Exception as e:
      return unknow_response(self.commands)

if __name__ == '__main__':

  conversation_test_one = [
    "oi",
    "Eu queor uma comer",
    "Cambuci, São Paulo",
    "Recomendação",
    "1",
    "2",
    "6"
  ]

  for text in conversation_test_one:
    handlerConversation = HandlerConversation("Amanda", "551195069324", text)
    time.sleep(1)
    print(handlerConversation.run())