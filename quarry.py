import random
import simulate
import math
import itertools
import simulate
import pdb

"""
creates a Quarry object. This object contains all cards/die to be used in this
Quarriors Game, and holds information about these during the round. 

options(rolled_dice,max_buy)
  the bulk of the game so far, precursor for AI implementation. 
  takes a list of rolled_dice and computes which die/monster combinations
  are possible from this roll in this Quarries current condition

add_die(name)
  increases the die_count on a Card in the Quarry by 1

get_card(name)
  returns the card of the name specified
"""  

class Quarry:
  #the quarry is where dice are drawn from and placed in to cull
  def __init__(self,monsters,spells):
    #uncomment to initialize monsters/spells through options
    basics = ["Basic Quiddity","Portal","Assisstant"] 
    self.monsters = [Card("Strong Scavenging Goblin"),Card("Mighty Warrior Of The Quay"),Card("Witching Hag")]
    self.spells = [Card("Growth Charm"),Card("Life Incantation")]
    #self.monsters = [Card(monsters[i]) for i in range(len(monsters))]
    #self.spells = [Card(spells[i]) for i in range(len(spells))]
    self.basics = [Card(basics[i]) for i in range(len(basics))]
    self.num_empty = 0
    self.all_cards = self.basics+self.spells+self.monsters
    self.all_cards.sort(key=lambda x: x.cost,reverse = False)
    self.all_cards_dict = {}
    for card in self.all_cards:
      self.all_cards_dict[card.name] = card
  
  def options(self,rolled_dice,max_buy):
    options = []
    quiddity = 0
    remove = []
    #sums up quiddity and removes them
    for die in rolled_dice:
      if isinstance(die.face_up,Quiddity):
        quiddity += die.face_up.amt
        remove.append(die)
      elif not isinstance(die.face_up,MonsterFace):
        remove.append(die)
    for die in remove:
      rolled_dice.remove(die)
      #rolled_dice now consists of only rolled monsters
    i = 0
    while self.all_cards[i].cost <= quiddity:
      i+=1
      if i == len(self.all_cards):
        break
    possible_cards = self.all_cards[:i] #we can only buy cards as expensive as the quiddity we have
    for card in possible_cards:
      new_option = simulate.Option(quiddity)
      if new_option.can_buy(card,max_buy):
        new_option.buy(card)
      if new_option not in options:
        options.append(new_option)
    if max_buy > 1:
      for option in options: 
        for card in possible_cards:
          if option.can_buy(card,max_buy):
            new_option = simulate.Option(0)
            new_option.shallow_copy(option)
            new_option.buy(card)
            options.append(new_option)
    #the buy nothing option
    options.append(simulate.Option(quiddity))
    #options now is a list of options of all permutations of dice you could buy,
    #now we need to add to each of these options the monsters one could ready
    num_perm = math.factorial(len(rolled_dice)) #number of permutations
    if len(rolled_dice) == 0:
      all_options = options
    else:
      all_options = []
      for option in options:
        for perm in itertools.permutations(rolled_dice): 
          new_option = simulate.Option(0)
          new_option.shallow_copy(option)
          for die in perm:
            new_option.ready(die)
          if new_option not in all_options:
            all_options.append(new_option)
    #all_options should now have num_perm copies of the original options,
    #each with as many monsters readied as possible quiddity permitting
    return all_options

  def add_die(self,name):
    self.all_cards_dict[name].die_count += 1

  def get_card(self,name):
    return self.all_cards_dict[name]

"""
basic 6 sided die containing the six faces

roll()
  rolls the die, setting rolled to True and making a side face_up

unroll()
  sets rolled to False, needs to be called when put in bag or if rerolling

many children classes representing different cards in the game with their
respective faces
"""
class Die:
  def __init__(self):
    self.num_sides = 6
    self.sides = [Quiddity(0),Quiddity(0),Quiddity(0),Quiddity(0),Quiddity(0),Quiddity(0)]
    self.face_up = self.sides[0]
    self.rolled = False

  def __str__(self):
    return self.name + " " + str(self.face_up)

  def roll(self):
    self.rolled = True
    self.face_up = random.choice(self.sides)

  def unroll(self):
    self.rolled = False

class BasicQuiddity(Die):
  def __init__(self):
    Die.__init__(self)
    self.name = "Basic Quiddity"
    self.sides = [Quiddity(1),Quiddity(1),Quiddity(1),Quiddity(1),Quiddity(1),Quiddity(2)]

class Assisstant(Die):
  def __init__(self):
    Die.__init__(self)
    self.name = "Assisstant"
    self.sides = [Quiddity(1),Quiddity(1),Quiddity(1),AssisstantFace(),AssisstantFace(),RerollFace(1)]

class Portal(Die):
  def __init__(self):
    Die.__init__(self)
    self.name = "Portal"
    self.sides = [Quiddity(1),DrawFace(1),DrawFace(1),DrawFace(2),DrawFace(2),DrawFace(2)]

class StrongScavengingGoblin(Die):
  def __init__(self):
    Die.__init__(self)
    self.name = "Strong Scavenging Goblin"
    self.sides = [Quiddity(1),Quiddity(1),GoblinFace(False),GoblinFace(False),GoblinFace(True),GoblinFace(True)]

class MightyWarriorOfTheQuay(Die):
  def __init__(self):
    Die.__init__(self)
    self.name = "Mighty Warrior Of The Quay"
    self.sides = [Quiddity(1),Quiddity(2),Quiddity(2),WarriorFace(1),WarriorFace(1),WarriorFace(2)]

class WitchingHag(Die):
  def __init__(self):
    Die.__init__(self)
    self.name = "Witching Hag"
    self.sides = [Quiddity(1),Quiddity(2),Quiddity(2),HagFace(1),HagFace(1),HagFace(2)]

class GrowthCharm(Die):
  def __init__(self):
    Die.__init__(self)
    self.name = "Growth Charm"
    self.sides = [Quiddity(1),Quiddity(1),SpellFace(Quiddity(3)),SpellFace(Quiddity(3)),SpellFace(Quiddity(3)),SpellFace(Quiddity(3))]

class LifeIncantation(Die):
  def __init__(self):
    Die.__init__(self)
    self.name = "Life Incantation"
    self.sides = [Quiddity(1),Quiddity(2),Quiddity(2),SpellFace(LifeIncantationFace()),SpellFace(LifeIncantationFace()),SpellFace(LifeIncantationFace())]

class SpellFace:
  def __init__(self,face):
    self.face = face
  def __str__(self):
    return "spell"

class LifeIncantationFace:
  def __init__(self):
    cast = False
  def __str__(self):
    return "reaction: cast to reduce one creatures attack to 0"

class DrawFace:
  def __init__(self,num):
    self.num = num
  def __str__(self):
    return "draw " + str(self.num)

class MonsterFace:
  def __init__(self,lvl,atk,dfns,burst):
    self.lvl = lvl
    self.atk = atk
    self.dfns = dfns
    self.burst = burst
  def __str__(self):
    return "monster"

class HagFace(MonsterFace):
  def __init__(self,lvl):
    if lvl == 1:
      MonsterFace.__init__(self,1,3,3,False)
    else:
      MonsterFace.__init__(self,2,4,5,False)
  def __str__(self):
    return 'Witching Hag, lvl:' + str(self.lvl)

class WarriorFace(MonsterFace):
  def __init__(self,lvl):
    if lvl == 1:
      MonsterFace.__init__(self,1,2,3,False)
    else:
      MonsterFace.__init__(self,2,3,4,False)
  def __str__(self):
    return 'Mighty Warrior Of The Quay, lvl:' + str(self.lvl)

class AssisstantFace(MonsterFace):
  def __init__(self):
    MonsterFace.__init__(self,1,1,2,False)

  def __str__(self):
    return 'Assisstant, lvl:' + str(self.lvl)

class GoblinFace(MonsterFace):
  def __init__(self,burst):
    MonsterFace.__init__(self,1,1,2,burst)

  def __str__(self):
    return 'Strong Scavenging Goblin, lvl:' + str(self.lvl)

class Quiddity:
  def __init__(self,amt):
    self.amt = amt

  def __str__(self):
    return str(self.amt) + ' Quiddity'

class RerollFace:
  def __init__(self,num):
    self.num = num

  def __str__(self):
    return 'Reroll ' + str(self.num) + ' die' 
 
  """
  These Card class represents the container for dice in the quarry. Players input determines
  the cards used in the game. Add new Cards by adding the amount of dice
  the card starts with (usually 5), the cost to buy it from the Wilds,
  the glory the die scores, a description, and a Die representing the 
  6 faces of the monster die.
  You must then make the new Die child class,and new faces
  """
 
class Card:
 name_dict = {"Assisstant":[2,1,1,"Basic Unit",Assisstant],\
    "Basic Quiddity":[0,0,0,"1-2 quiddity",BasicQuiddity],\
    "Portal":[5,4,0,"Cast to draw 1-2 dice",Portal],\
    #spells
    "Growth Charm":[5,5,0,"Cast this spell to gain 3 Quiddity",GrowthCharm],\
    "Life Incantation":[5,4,0,"Reaction: cast to reduce 1 creatures attack to 0 for remainder of turn",LifeIncantation],\
    #monsters
    "Strong Scavenging Goblin":[5,3,2,"*:+1 defense per monster in ready area",StrongScavengingGoblin],\
    "Witching Hag":[5,5,3,"+1 Quiddity per creature you destroy with Hag in ready area",WitchingHag],\
    "Mighty Warrior Of The Quay":[5,4,3,"When summoned, all other warriors die. 1 summon per turn",MightyWarriorOfTheQuay]} 
  
  def __init__(self,name):
    self.name = name
    #basics
    stats = self.name_dict[name]
    self.die_count = stats[0]
    self.cost = stats[1]
    self.glory = stats[2]
    self.description = stats[3]
    self.die = stats[4]

  def __str__(self):
    return self.name + ', ' + str(self.die_count) + ' left, Cost: ' + str(self.cost) + ', Glory: ' + str(self.glory) + ', ' + self.description



