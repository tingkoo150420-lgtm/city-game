from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()
window.title = "Python GTA Ultimate Prototype"


# ---------------- PLAYER ----------------

player = FirstPersonController()
player.speed = 5
player.health = 100
player.money = 500

in_car = False
current_car = None
wanted = 0


health_text = Text(text="HP:100", position=(-0.85,0.45), scale=2)
wanted_text = Text(text="Wanted:0", position=(-0.85,0.40), scale=2)
money_text = Text(text="Money:500", position=(0.7,0.45), scale=2)


# ---------------- MAP ----------------

ground = Entity(model='plane', scale=300, collider='box', color=color.gray)

# buildings
for i in range(80):
    h=random.randint(5,20)
    Entity(
        model='cube',
        scale=(4,h,4),
        position=(random.randint(-120,120),h/2,random.randint(-120,120)),
        color=color.random_color()
    )


# ---------------- NPC ----------------

npcs=[]

class NPC(Entity):

    def __init__(self,type,pos):

        super().__init__(
            model='cube',
            scale=(1,2,1),
            position=pos
        )

        self.type=type
        self.health=100
        self.speed=1

        if type=="police":
            self.color=color.blue
            label="POLICE"
        else:
            self.color=color.orange
            label="CIVILIAN"

        Text(text=label,parent=self,y=1.5,scale=3,color=color.azure)

        self.move_timer=random.uniform(1,3)

        npcs.append(self)


for i in range(12):
    NPC("civilian",(random.randint(-80,80),1,random.randint(-80,80)))

for i in range(6):
    NPC("police",(random.randint(-80,80),1,random.randint(-80,80)))


# ---------------- CARS ----------------

cars=[]

class Car(Entity):

    def __init__(self,pos,police=False):

        super().__init__(
            model='cube',
            scale=(2,1,4),
            position=pos
        )

        self.police=police
        self.speed=12

        if police:
            self.color=color.blue
        else:
            self.color=color.red

        cars.append(self)


for i in range(10):
    Car((random.randint(-80,80),0.5,random.randint(-80,80)))

for i in range(3):
    Car((random.randint(-80,80),0.5,random.randint(-80,80)),police=True)


# ---------------- HELICOPTER ----------------

helicopter = Entity(
    model='cube',
    color=color.black,
    scale=(3,1,3),
    position=(0,30,0)
)


# ---------------- GUN ----------------

bullets=[]

def shoot():

    bullet = Entity(
        model='sphere',
        scale=0.1,
        color=color.yellow,
        position=camera.world_position
    )

    bullet.direction = camera.forward
    bullet.life = 2

    bullets.append(bullet)


# ---------------- SHOP ----------------

shop_ui = WindowPanel(
title='Weapon Shop',
content=(
Button(text='Buy Rifle - $200',on_click=lambda: buy("rifle")),
Button(text='Buy Shotgun - $300',on_click=lambda: buy("shotgun")),
Button(text='Buy Sniper - $400',on_click=lambda: buy("sniper")),
),
enabled=False
)

def buy(item):

    if player.money>=200:

        player.money-=200
        money_text.text="Money:"+str(player.money)


# ---------------- INPUT ----------------

def input(key):

    global in_car
    global current_car

    if key=="left mouse down" and not in_car:
        shoot()

    if key=="p":
        shop_ui.enabled = not shop_ui.enabled


    if key=="e":

        if not in_car:

            for car in cars:

                if distance(player.position,car.position)<3:

                    in_car=True
                    current_car=car

                    player.disable()
                    player.visible=False

                    break

        else:

            in_car=False

            player.enable()
            player.visible=True

            player.position=current_car.position+Vec3(2,0,0)

            current_car=None


# ---------------- RESPAWN ----------------

respawn_timer=0

def respawn():

    player.health=100
    player.position=(0,2,0)


# ---------------- UPDATE ----------------

def update():

    global respawn_timer

    health_text.text="HP:"+str(int(player.health))
    wanted_text.text="Wanted:"+str(wanted)

    # bullets
    for b in bullets[:]:

        b.position += b.direction*40*time.dt
        b.life -= time.dt

        if b.life<=0:

            destroy(b)
            bullets.remove(b)
            continue


        for npc in npcs[:]:

            if distance(b.position,npc.position)<1:

                npc.health-=30

                destroy(b)
                bullets.remove(b)

                if npc.health<=0:

                    destroy(npc)
                    npcs.remove(npc)

                break


    # civilian AI
    for npc in npcs:

        if npc.type=="civilian":

            npc.move_timer-=time.dt

            if npc.move_timer<=0:

                npc.rotation_y=random.randint(0,360)
                npc.move_timer=random.uniform(1,3)

            npc.position+=npc.forward*0.5*time.dt


    # police AI
    for npc in npcs:

        if npc.type=="police" and wanted>0:

            npc.look_at(player)
            npc.position+=npc.forward*2*time.dt

            if distance(player.position,npc.position)<2:

                player.health-=10*time.dt


    # police car chase
    for car in cars:

        if car.police and wanted>=2:

            car.look_at(player)
            car.position+=car.forward*car.speed*time.dt


    # helicopter attack
    if wanted>=4:

        helicopter.look_at(player)
        helicopter.position+=helicopter.forward*10*time.dt


    # car control
    if in_car and current_car:

        if held_keys["w"]:
            current_car.position+=current_car.forward*current_car.speed*time.dt

        if held_keys["s"]:
            current_car.position-=current_car.forward*current_car.speed*time.dt

        if held_keys["a"]:
            current_car.rotation_y-=60*time.dt

        if held_keys["d"]:
            current_car.rotation_y+=60*time.dt

        camera.position=current_car.position+Vec3(0,3,-6)
        camera.look_at(current_car)


    # death
    if player.health<=0:

        respawn_timer+=time.dt

        if respawn_timer>5:

            respawn()
            respawn_timer=0


app.run()