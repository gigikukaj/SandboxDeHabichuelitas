import arcade
from random import randint

from utils.constants import *
from utils.object_tags import *
from entities.Player import Player
from entities.PickableItem import PickableItem


def load_texture_pair(filename):
    """
    Load a texture pair, with mirror image as second one
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


def normal_or_boosted_speed(is_powered, item_picked):
    if is_powered:
        if item_picked == DEFAULT_CONSUMABLE:
            return MOVEMENT_SPEED_REDUCTION
        return MOVEMENT_SPEED_POWERUP
    else:
        return MOVEMENT_SPEED


class MyGame(arcade.Window):
    """Custom window class"""

    def __init__(self, w, h, title):
        super().__init__(w, h, title)
        # Set bg color
        arcade.set_background_color(arcade.csscolor.WHITE)

        # Game scene
        self.scene = None

        # Set up the player info
        self.player_list = None
        self.player_sprite = None

        # Pick up object
        self.pickup_object_list = None

        # Draw text while game playing
        self.can_draw_text = False

        # Power up timer state variables
        self.powerup_countdown = 0
        self.total_time = 0.0

        self.pickup_object_sprite = None

        self.hability_icon = None

    def setup(self):
        # Creating scene
        self.scene = arcade.Scene()

        # Set up the player
        self.player_list = arcade.SpriteList()
        self.player_sprite = Player()

        # Player initial position
        self.player_sprite.center_x = SCREEN_WIDTH // 2
        self.player_sprite.center_y = SCREEN_HEIGHT // 2

        self.player_list.append(self.player_sprite)

        self.pickup_object_list = arcade.SpriteList()

        self.pickup_object_sprite = PickableItem("assets/food_items/blue_potion.png", randint(0, SCREEN_WIDTH),
                                                 randint(0, SCREEN_HEIGHT - 100), sprite_scaling=1.25,
                                                 tag=DEFAULT_CONSUMABLE)
        self.pickup_object_list.append(self.pickup_object_sprite)
        self.pickup_object_sprite = PickableItem("assets/food_items/pink_potion.png", randint(0, SCREEN_WIDTH),
                                                 randint(0, SCREEN_HEIGHT - 100), sprite_scaling=1.25,
                                                 tag=PINK_CONSUMABLE)
        self.pickup_object_list.append(self.pickup_object_sprite)
        self.pickup_object_sprite = PickableItem("assets/food_items/yellow_potion.png", randint(0, SCREEN_WIDTH),
                                                 randint(0, SCREEN_HEIGHT - 100), sprite_scaling=1.25,
                                                 tag=DEFAULT_CONSUMABLE)
        self.pickup_object_list.append(self.pickup_object_sprite)
        self.pickup_object_sprite = PickableItem("assets/food_items/green_potion.png", randint(0, SCREEN_WIDTH),
                                                 randint(0, SCREEN_HEIGHT - 100), sprite_scaling=1.25,
                                                 tag=DEFAULT_CONSUMABLE)
        self.pickup_object_list.append(self.pickup_object_sprite)

        for pickable_object in self.pickup_object_list:
            self.scene.add_sprite('Pick-able object', pickable_object)

        self.scene.add_sprite('Player', self.player_sprite)

    def on_draw(self):
        arcade.start_render()

        # Draw all the sprites.
        self.scene.draw()

        arcade.draw_text('Arrow keys to move, hold X to attack, C to pick up or cancel on power up mode', 5,
                         SCREEN_HEIGHT - 21,
                         arcade.color.BLACK, 12)

        if self.can_draw_text:
            arcade.draw_text('C to pick up', SCREEN_WIDTH - 111, 21,
                             arcade.color.BLUEBERRY,
                             12, bold=True)

        arcade.draw_text(f'Power Up Countdown: {self.powerup_countdown} / {POWERUP_AVAILABLE_TIME}', 5, SCREEN_HEIGHT - 42, arcade.color.BLACK)

        if self.hability_icon is not None:
            self.hability_icon.draw()

    def on_update(self, delta_time):
        # Move the player
        self.player_list.update()
        self.player_list.update_animation()

        power_up_items_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.pickup_object_list)

        for power_up_item in power_up_items_hit_list:
            self.pickup_object_sprite = power_up_item
            if self.player_sprite.picking == PICKING:
                power_up_item.remove_from_sprite_lists()

        if len(power_up_items_hit_list) != 0 and self.player_sprite.power_up == POWERUP_DISABLED:
            self.player_sprite.can_pick_up = True
            self.can_draw_text = True
        else:
            self.player_sprite.can_pick_up = False
            self.can_draw_text = False

        # Enable power up for x amount of seconds and display counter on screen
        if self.player_sprite.power_up == POWERUP_ENABLED:
            if self.powerup_countdown == POWERUP_AVAILABLE_TIME:
                self.player_sprite.power_up = POWERUP_DISABLED
                self.powerup_countdown = 0
                self.total_time = 0.0
                self.hability_icon = None
            else:
                self.total_time += delta_time
                seconds = int(self.total_time) % 60
                self.powerup_countdown = seconds

        if self.player_sprite.power_up == POWERUP_ENABLED:
            icon_pos = [SCREEN_WIDTH - 32, SCREEN_HEIGHT - 32]
            if self.player_sprite.item_picked == DEFAULT_CONSUMABLE:
                self.hability_icon = arcade.Sprite('./assets/habilities_icons/blue_hability.png', 2, center_x=icon_pos[0], center_y=icon_pos[1])
            if self.player_sprite.item_picked == PINK_CONSUMABLE:
                self.hability_icon = arcade.Sprite('./assets/habilities_icons/pink_hability.png', 2, center_x=icon_pos[0], center_y=icon_pos[1])

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            if self.player_sprite.picking == WAITING_PICKING:
                self.player_sprite.face_direction = FACING_TOP
                self.player_sprite.change_y = normal_or_boosted_speed(self.player_sprite.power_up, self.player_sprite.item_picked)
        elif key == arcade.key.DOWN:
            if self.player_sprite.picking == WAITING_PICKING:
                self.player_sprite.face_direction = FACING_BOTTOM
                self.player_sprite.change_y = -normal_or_boosted_speed(self.player_sprite.power_up, self.player_sprite.item_picked)
        elif key == arcade.key.LEFT:
            if self.player_sprite.picking == WAITING_PICKING:
                self.player_sprite.face_direction = FACING_LEFT
                self.player_sprite.change_x = -normal_or_boosted_speed(self.player_sprite.power_up, self.player_sprite.item_picked)
        elif key == arcade.key.RIGHT:
            if self.player_sprite.picking == WAITING_PICKING:
                self.player_sprite.face_direction = FACING_RIGHT
                self.player_sprite.change_x = normal_or_boosted_speed(self.player_sprite.power_up, self.player_sprite.item_picked)
        elif key == arcade.key.X:
            if self.player_sprite.picking == WAITING_PICKING:
                self.player_sprite.attack = ATTACK

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0
        elif key == arcade.key.X:
            self.player_sprite.attack = WAITING_ATTACK
        elif key == arcade.key.C:
            if self.player_sprite.power_up == POWERUP_ENABLED:
                self.player_sprite.power_up = POWERUP_DISABLED
                self.powerup_countdown = 0
                self.total_time = 0.0
                self.hability_icon = None
            elif self.player_sprite.can_pick_up:
                self.player_sprite.picking = PICKING
                self.player_sprite.power_up = POWERUP_ENABLED
                self.player_sprite.item_picked = self.pickup_object_sprite.tag


def main():
    """Main method"""
    wn = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    wn.setup()
    arcade.run()


if __name__ == '__main__':
    main()
