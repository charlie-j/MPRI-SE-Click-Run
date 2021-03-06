from entity import MovingEntity
from enum import Enum
from ressources import load_image
import pygame as pg

CONST_JUMP = 18
CONST_DOUBLE_JUMP = 18
CONST_ASCEND_TIME = 12


class Action(Enum):
    """
    The class which represent the different state in which the player can be.
    """
    RUNNING = 1
    JUMPING = 2
    ASCEND = 3


class Player(MovingEntity):
    """
    The class for the main character
    """

    def __init__(self, x0, y0, vx0, vy0, sprite_name, jump_key):
        """
        @param x0: The x-axis position of the object.
        @type x0: int
        @param y0: The y-axis position of the object.
        @type y0: int
        @param vx0: The speed of the object on the x-axis.
        @type vx0: int
        @param vy0: The speed of the object on the y-axis.
        @type vy0: int
        @rtype: None
        """
        MovingEntity.__init__(self, x0, y0, vx0, vy0, (50, 50))
        self.jump_key = jump_key
        self.action = Action.JUMPING
        # This variable takes trace of number of frame since player jumped in order to stop the ascending phase
        self.frame_since_last_jump = 0
        # TODO -> lecture automatique des sprite à dic
        # The sprite are stored in a dict
        self.sprite = self.load_sprite(sprite_name)
        self.time_of_a_sprite = 5
        self.current_time = -1
        self.double_jump_available = False
        self.running_sprite_number = 0  # The number of the sprite for running
        self.anterior_running_sprite_number = 1  # The anterior sprite for running
        self.is_dead = False
        self.poison = -1

        self.mod_difficulty = 0

        self.font = pg.font.Font(None, 24)

        self.nb_frame = 0
        self.old_hit_box = []

    def load_sprite(self, sprite_name):
        """
        Function to load the sprite of a player
        @param sprite_name: the name of the sprite
        @type sprite_name: str
        @return: dict(str, sprite)
        """
        return {"JUMP": load_image("player/%s/big/jump.png" % sprite_name, self.hitbox),
                "RUN0": load_image("player/%s/big/run0.png" % sprite_name, self.hitbox),
                "RUN1": load_image("player/%s/big/run1.png" % sprite_name, self.hitbox),
                "RUN2": load_image("player/%s/big/run2.png" % sprite_name, self.hitbox),
                "ASCEND": load_image("player/%s/big/ascend.png" % sprite_name, self.hitbox)}

    def switch_hit_box(self, hit_box):
        """
        Function to switch the hit_box of a player
        @param hit_box: the new hit_box
        @return: None
        """
        self.old_hit_box = [self.hitbox] + self.old_hit_box
        self.hitbox = hit_box
        for sprite in self.sprite:
            self.sprite[sprite] = pg.transform.scale(self.sprite[sprite], self.hitbox)

    def update(self, game_map, difficulty, acceleration_y, max_speed):
        """
        Function to update a player
        @param game_map: the map the player is on
        @param difficulty: the difficulty of the game
        @param acceleration_y: the acceleration
        @param max_speed: the maximal speed the player can reach
        @return: None
        """
        if self.is_dead:
            return

        self.frame_since_last_jump += 1

        is_the_game_over, (x, y) = game_map.move_test(self.pos_x,
                                                      self.pos_y,
                                                      self.hitbox,
                                                      int(self.v_x * difficulty),
                                                      int(self.v_y * difficulty))
        self.pos_y = y

        self.is_dead = is_the_game_over

        if game_map.object_on_the_ground(self) and self.action != Action.ASCEND:
            self.action = Action.RUNNING
            self.v_y = min(self.v_y, 0)
            self.double_jump_available = True
        elif self.action in [Action.JUMPING, Action.RUNNING] or \
                (self.action == Action.ASCEND and self.frame_since_last_jump > CONST_ASCEND_TIME):
            # Either is the player in jump state, or he stopped his ascension
            self.action = Action.JUMPING
            self.v_y = max(min(self.v_y + difficulty*acceleration_y*self.gravity, max_speed), -max_speed)
        elif self.action == Action.ASCEND:  # In that case, the player continues his ascension
            self.v_y = max(min(self.v_y + difficulty*acceleration_y/2*self.gravity, max_speed), -max_speed)

        if self.poison == 0:
            self.is_dead = True
            
        if self.poison != -1:
            self.poison -=1

    def get_event(self, event, game_map):
        """
        Function to thread the event on the player
        @param event: the event on the player
        @type event: pg.event
        @param game_map: the map the player is on
        @type game_map: Map
        @return: None
        """
        if self.is_dead:
            return

        if event.type == pg.KEYDOWN:
            # Let's try to make the player jump by modifiying its velocity after checking if it's on the ground
            if event.key == self.jump_key:
                if game_map.object_on_the_ground(self):
                    self.v_y = min(-CONST_JUMP, self.v_y)
                    # Player get an ascending phase that lasts some frame where he can still gain some vertical velocity
                    self.action = Action.ASCEND
                    self.frame_since_last_jump = 0
                elif self.action == Action.JUMPING and self.double_jump_available:
                    self.double_jump_available = False
                    self.v_y = - CONST_DOUBLE_JUMP
                    self.action = Action.JUMPING
        if event.type == pg.KEYUP:
            if event.key == self.jump_key:
                if self.action == Action.ASCEND:
                    self.action = Action.JUMPING

    def choose_sprite(self):
        """
        This function choose the good sprite and returns it.
        @return: The surface of the corresponding sprite.
        @rtype: pygame.Surface
        """
        if self.is_dead:
            return pg.Surface((0, 0))

        if self.action == Action.JUMPING:
            return self.sprite["JUMP"]
        elif self.action == Action.RUNNING:
            self.current_time = (self.current_time + 1) % self.time_of_a_sprite
            if self.current_time != 0:
                return self.sprite["RUN%d" % self.running_sprite_number]
            max_running_sprite = 2
            min_running_sprite = 0
            tmp = self.running_sprite_number
            if self.running_sprite_number == max_running_sprite or self.running_sprite_number == min_running_sprite:
                self.running_sprite_number = self.anterior_running_sprite_number
            else:
                self.running_sprite_number += self.running_sprite_number - self.anterior_running_sprite_number
            self.anterior_running_sprite_number = tmp
            return self.sprite["RUN%d" % self.running_sprite_number]
        elif self.action == Action.ASCEND:
            return self.sprite["ASCEND"]

    def draw(self, surface):
        """
        Display the player on the surface.
        @param surface: The surface to display the player on.
        @type surface: pygame.Surface
        @rtype: None
        """
        surface.blit(self.choose_sprite(), (self.pos_x, self.pos_y))
        if self.poison != -1:
            surface.blit(self.font.render(str(self.poison),1, (0,0,0)), (self.pos_x - 25, self.pos_y - 25))
