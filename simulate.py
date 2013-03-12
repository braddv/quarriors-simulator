import argparse
import itertools
import random
import math
import pdb
import time

import quarry
"""
The Game class stores the Players and the Quarry

is_over()
  returns whether the game has ended, True/False
"""
class Game:
  def __init__(self,quarry,players):
    self.players = players
    self.quarry = quarry
    self.num_players = len(players)
    self.max_score = 0
    self.max_buy = 1
    if self.num_players == 2:
      self.winning_score = 20
    elif self.num_players == 3:
      self.winning_score = 15
    else:
      self.winning_score = 12

  def is_over(self):
    for player in self.players:
      if player.score >= self.winning_score:
        return True
    if self.quarry.num_empty >= 4:
      return True
    return False

"""
The Player class does a lot of work moving dice around between the Quarry and the
different areas in the game. The Basic flow of dice is 
  Quarry -> Player.used_pile -> dice_bag -> active_pool -> ready_area -> quarry/used_pile

move(area1,area2,i,j):
  appends the dice from index i-j in area1 into area2, merges area1 back together,
  and then returns the new area1 and area2

draw(num_dice,game):
  
is_dice_to_roll():

cull(game):

rollready(game):

choose():

attack():

capture():

"""
class Player:
  id = 0
  def __init__(self):
    self.id = Player.id
    Player.id += 1
    self.dice_bag = [quarry.BasicQuiddity() for i in range(8)]+[quarry.Assisstant() for i in range(4)]
    self.ready_area = []
    self.active_pool = []
    self.spent_pile = []
    self.used_pile = []
    self.score = 0
    self.allowed_dice = 6
    self.quiddity = 0
 
  def move(self,area1,area2,i,j):
    area2 += area1[i:j]
    area1 = area1[:i] + area1[j:]
    return area1,area2

  def draw(self,num_dice,game):
    #if you have less than 6 dice in your bag, you need to move dice from bag
    #to active pool, then shuffle your used pile into bag and grab remaining dice.
    if len(self.dice_bag) < num_dice:
      old_bag_len = len(self.dice_bag)
      self.dice_bag,self.active_pool = self.move(self.dice_bag,self.active_pool,0,len(self.dice_bag))
      self.used_pile,self.dice_bag = self.move(self.used_pile,self.dice_bag,0,len(self.used_pile))
      random.shuffle(self.dice_bag)
      self.dice_bag,self.active_pool = self.move(self.dice_bag,self.active_pool,0,num_dice-old_bag_len) 
    else:
      random.shuffle(self.dice_bag)
      self.dice_bag,self.active_pool = self.move(self.dice_bag,self.active_pool,0,num_dice)
  
  def is_die_to_roll(self):
    for die in self.active_pool:
      if not die.rolled:
        return True
    return False

  def cull(self,game):
    for die in self.ready_area:
      score = raw_input("score or save? ")
      if score == "score":
        card = game.quarry.get_card(die.name)
        card.die_count += 1
        self.score += card.glory
        print("~~Player " + str(self.id) + " now has " + str(self.score) +  " glory!~~")
      else:
        self.used_pile.append(die)
    self.ready_area = []

  def rollready(self,game):
    self.draw(6,game)
    reroll_choice = 0
    while self.is_die_to_roll():
      for die in list(self.active_pool):
        if not die.rolled:
          die.roll()
          if isinstance(die.face_up,quarry.DrawFace):
            print("drawing die")
            self.draw(die.face_up.num,game)
          if isinstance(die.face_up,quarry.RerollFace):
            die.unroll()
            reroll_choice += 1
      if reroll_choice > 0:
        i = 0
        offsets = []
        for die in self.active_pool:
          if die.rolled:
            i += 1
            print(str(i) + " " + str(die))
          else:
            offsets.append(i)
        reroll = raw_input("Choose reroll die: ")
        reroll = int(reroll)
        i = 0
        while reroll > offsets[i]:
          i += 1
          if i == len(offsets):
            break
          
        self.active_pool[reroll-1+i].unroll()
        reroll_choice -=1
    #rolled pool not being emptied...
    print("###############################")
    for die in self.active_pool:
      print(die)
    print("###############################")
    self.choose(game.quarry,game.max_buy)
    #makes a choice of option to do, through player or ai
    a,self.ready_area = self.move(self.choice.ready_list,self.ready_area,0,len(self.choice.ready_list))
    for die in self.active_pool:
      if isinstance(die.face_up,quarry.Quiddity):
        self.used_pile.append(die)
    self.active_pool = []


  def choose(self,quarry,max_buy):
    options = quarry.options(list(self.active_pool),max_buy) 
    #list of rolled die -> list of options of things to buy
    i = 0
    for option in options:
      i += 1
      print("***************** Option: " + str(i) + " ************************")
      print(option) 
    choice = raw_input("Pick an option: ")
    try:
      self.choice = options[int(choice)-1]
    except:
      choice = raw_input("try again")
      self.choice = options[int(choice)-1]
    print("Chose:")
    print("***************** Option: " + str(choice) + " ************************")
    print(self.choice)
 
  def attack(self,game):
    attack = 0
    for die in self.ready_area:
      attack += die.face_up.atk
    for player in game.players:
      pattack = attack #new attack total against each player
      defense = []
      if player is not self:
        defense = []
        for die in player.ready_area:
          defense.append(die.face_up.dfns)
        while defense and attack >= max(defense):
          i = 0
          for die in player.ready_area:
            i+=1
            print(str(i) + " " + str(die))
          choice = raw_input("Player " + str(player.id) + " choose who dies: ")
          pattack -= defense[int(choice)-1]
          defense.remove(defense[int(choice)-1])
          player.ready_area,player.used_pile = player.move(player.ready_area,player.used_pile,int(choice)-1,int(choice))
  
  def capture(self,game): 
    for card in self.choice.buy_list:
      self.used_pile.append(card.die())
      card.die_count -= 1
  
class Option:
  """An option consists of 1) Monsters to Ready, 2) Cards to Buy, 3) Dice to Used Pile"""
  def __init__(self,quiddity):
    self.num_bought = 0
    self.ready_list = []
    self.buy_list = []
    self.used_pile = []
    self.quiddity = quiddity

  def __str__(self):
    output = "Buy:\n"
    for card in self.buy_list:
      output += str(card)
      output += "\n"
    output += "Ready:\n"
    for die in self.ready_list:
      output += str(die)
      output += "\n"
    output += str(self.quiddity) 
    output += " Quiddity Left\n"
    return output
   
  def __cmp__(self,other):
    if (set(self.buy_list) == set(other.buy_list)) and (set(self.ready_list) == set(other.ready_list)) and (int(self.quiddity) == int(other.quiddity)):
      return 0
    else:
      return 1

  def shallow_copy(self,option):
    self.ready_list = list(option.ready_list)
    self.buy_list = list(option.buy_list)
    self.used_pile = list(option.used_pile)
    self.quiddity = int(option.quiddity)
    self.num_bought = int(option.num_bought)

  def can_buy(self,card,max_buy):
    if (self.num_bought < max_buy) and (self.quiddity >= card.cost) and (card.die_count > 0):
      return True
    else:
      return False

  def buy(self,card):
    if self.quiddity >= card.cost:
      self.num_bought += 1
      self.buy_list.append(card)
      self.quiddity -= card.cost

  def ready(self,die):
    if self.quiddity >= die.face_up.lvl and isinstance(die.face_up,quarry.MonsterFace):
      self.ready_list.append(die)
      self.quiddity -= die.face_up.lvl 

def simulate(monsters,spells,n,num_players):
  for i in range(n):
    print('Simulation ' + str(i) + '...')
    q = quarry.Quarry(monsters,spells)
    Player.id = 0
    players = [Player() for i in range(num_players)]
    game = Game(q,players)
    while(not game.is_over()):
      n = 0
      for player in game.players:
        print("*********** begin player " + str(player.id) + "s turn *************")
        player.cull(game)
        player.rollready(game)
        time.sleep(1)
        print("Attacking...")
        player.attack(game)
        time.sleep(1)
        print("Capture...")
        player.capture(game)
        time.sleep(1)
        print("End of player " + str(player.id) + "s turn")

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-m",nargs='+',help="seven strings representing monster cards")
  parser.add_argument("-s",nargs='+', help="three strings representing spell cards")
  parser.add_argument("-n",type=int,help="number of times to run simulation",default=1)
  parser.add_argument("-p",type=int,help="number of players, default=2",default=2)
  args = parser.parse_args()
  """print('Monsters: ')
  for monster in args.m:
  print monster
  print('Spells: ')
  for spell in args.s:
  print spell"""
  print 'Running ' + str(args.n) + ' iterations' + ' with ' + str(args.p) + ' players'
  simulate(args.m,args.s,args.n,args.p)
