
from tkinter import (
    LEFT,
    CENTER,
)
from pathlib import (
    Path,
)

import yaml

from matplotlib.colors import LinearSegmentedColormap
from keras.models import (
    load_model,
)


class ConfigGUI:

    def __init__(
            self,
    ) -> None:

        self._pre_init()

        self._strings_file = 'strings_en.yml'  # text for all visible strings

        global_font_scale = 1.0  # scales fonts and elements that scale with font size, e.g., boxes

        self.logos = [
            'unilogo.png',
            'ANT.png',
            'sponsoredbybmbf.png',
            'momentum.jpg',
            'FunKI_Logo_final_4C.png',
        ]
        self.label_img_logos_height_scale = 0.07

        self.label_title_font = ('Arial', int(global_font_scale * 60))

        self.label_user_font = ('Arial', int(global_font_scale * 25))
        self.user_images = [
            '1.png',
            '2.png',
            '3.png',
            'whambulance.png',
        ]
        self.base_station_image = 'base_station.png'

        self.label_img_user_height_scale = 0.1
        self.label_img_users_border_width = 15
        self.label_img_base_station_height_scale = 0.25

        self.channel_strength_indicator_imgs = [
            'bars_low_alt.png',
            'bars_medlow_alt.png',
            'bars_medhigh_alt.png',
            'bars_high.png',
        ]

        self.label_resource_font = ('Arial', int(global_font_scale * 50))
        self.label_resource_width = 3  # relative to font size
        self.label_resource_height = 1  # relative to font size
        self.label_resource_border_width = 2

        self.button_screen_selector_font = ('Arial', int(global_font_scale * 25))
        self.button_action_font = ('Arial', int(global_font_scale * 25))

        self.table_instant_stats_font_size = int(global_font_scale * 11)

        self.fig_lifetime_stats_font_size = int(global_font_scale * 11)
        self.fig_lifetime_stats_bar_color = self.cp3['blue3']
        self.fig_lifetime_stats_color_gradient = [self.cp3['red2'], self.cp3['blue3'], self.cp3['blue2']]

        self.label_resource_grid_title_font = ('Arial', int(global_font_scale * 15))
        self.label_resource_small_scaling: float = 0.5

        self.button_countdown_img = 'stopwatch.png'
        self.button_countdown_img_scale = 0.07

        self.countdown_reset_value_seconds: int = 10

        self.user_colors = {
            0: self.cp3['blue1'],
            1: self.cp3['blue2'],
            2: self.cp3['blue3'],
            3: self.cp3['red2'],
        }

        self.learned_agents: dict = {
            'sumrate': load_model(Path(self.models_path, 'max_sumrate', 'policy')),
            'fairness': load_model(Path(self.models_path, 'fairness', 'policy_snap_0.914')),
            'mixed': load_model(Path(self.models_path, 'mixed', 'policy_snap_1.020')),
        }

        self._post_init()

    def _pre_init(
            self,
    ) -> None:

        self.project_root_path = Path(__file__).parent.parent.parent
        self.models_path = Path(self.project_root_path, 'models')

        self._load_palettes()

    def _post_init(
            self,
    ) -> None:

        with open(Path(self.project_root_path, 'src', 'config', self._strings_file), 'r') as file:
            self.strings = yaml.safe_load(file)
        self.set_strings()

        self.button_screen_selector_config = {
            'font': self.button_screen_selector_font,
            'width': 15,
            'borderwidth': 3,
            'bg': 'white',
            'compound': CENTER,
        }

        self.button_action_config = {
            'font': self.button_action_font,
            'width': 1,  # small value for even distribution
            'borderwidth': 7,
            'bg': 'white',
            'compound': CENTER,
        }

        self.button_screen_selector_allocations_config = {
            'text': self.button_screen_selector_allocations_text,
            **self.button_screen_selector_config
        }

        self.button_screen_selector_stats_config = {
            'text': self.button_screen_selector_stats_text,
            **self.button_screen_selector_config,
        }

        self.button_countdown_config = {
            **self.button_action_config,
        }

        self.button_auto_config = {
            'text': 'Auto',
            **self.button_action_config,
        }

        self.button_reset_config = {
            'text': 'Reset',
            **self.button_action_config,
        }

        self.labels_config = {
            'font': self.label_user_font,
            'bg': 'white',
        }

        self.label_resource_config = {
            'font': self.label_resource_font,
            'width': self.label_resource_width,
            'height': self.label_resource_height,
            'relief': 'solid',
            'borderwidth': self.label_resource_border_width,
            'bg': 'white',
        }
        self.label_resource_small_config = self.label_resource_config.copy()
        self.label_resource_small_config['font'] = (self.label_resource_font[0], int(self.label_resource_small_scaling * self.label_resource_font[1]))

        self.label_user_image_config = {
            'bg': 'white',
            'highlightthickness': self.label_img_users_border_width,
        }

        self.label_resource_grid_title_config = {
            'font': self.label_resource_grid_title_font,
            'height': 2,
            'wraplength': 100,
            'bg': 'white',
        }

        self.label_user_text_config = {
            'font': self.label_user_font,
            'bg': 'white',
            'justify': LEFT,
        }

        self.label_resource_grid_text_config = {
            'text': self.label_resource_grid_text,
            'font': self.label_user_font,
            'bg': 'white',
            'justify': LEFT,
        }

        self.label_title_text_config = {
            'text': self.label_title_text,
            'font': self.label_title_font,
            'bg': 'white',
            'justify': LEFT,
        }

        self.label_results_title_config = {
            'text': self.label_results_title_text,
            **self.labels_config,
        }

        self.label_instant_stats_title_config = {
            'text': self.label_instant_stats_title_text,
            'font': self.label_user_font,
            'bg': 'white',
        }

        self.label_lifetime_stats_title_config = {
            'text': self.label_lifetime_stats_title_text,
            'font': self.label_user_font,
            'bg': 'white',
        }

        self.frames_config = {
            'bg': 'white',
            # 'relief': 'solid',
            # 'borderwidth': 2,
        }

        self.allocator_names = [self.own_allocation_display_name] + list(self.learned_agents_display_names.values())

        self.fig_instant_stats_config = {
            'column_labels': self.stat_names,
            'row_labels': self.allocator_names,
            'font_size': self.table_instant_stats_font_size,
        }

        self.fig_lifetime_stats_config = {
            'column_labels': self.allocator_names,
            'font_size': self.fig_lifetime_stats_font_size,
            'bar_color': self.fig_lifetime_stats_bar_color,
        }
        self.fig_lifetime_stats_gradient_cmap = LinearSegmentedColormap.from_list('', self.fig_lifetime_stats_color_gradient)
        self.fig_lifetime_stats_gradient_cmap_reversed = LinearSegmentedColormap.from_list('', list(reversed(self.fig_lifetime_stats_color_gradient)))

    def set_strings(
            self,
    ) -> None:

        self.button_screen_selector_allocations_text = self.strings['button_screen_selector_allocations']
        self.button_screen_selector_stats_text = self.strings['button_screen_selector_stats']

        self.label_title_text = self.strings['label_title']
        self.label_resource_grid_text = self.strings['label_resource_grid']
        self.label_instant_stats_title_text = self.strings['label_instant_stats_title']
        self.label_lifetime_stats_title_text = self.strings['label_lifetime_stats_title']
        self.stat_names = self.strings['stats']
        self.own_allocation_display_name = self.strings['label_own_display_name']
        self.learned_agents_display_names = self.strings['label_learned_display_names']
        self.label_results_title_text = self.strings['label_results_title']

        self.string_wants = self.strings['wants']
        self.string_resources = self.strings['resources']
        self.string_channel = self.strings['channel']

    def _load_palettes(
            self,
    ) -> None:

        self.cp3: dict[str: str] = {  # uni branding
            'red1': '#9d2246',
            'red2': '#d50c2f',
            'red3': '#f39ca9',
            'blue1': '#00326d',
            'blue2': '#0068b4',
            'blue3': '#89b4e1',
            'purple1': '#3b296a',
            'purple2': '#8681b1',
            'purple3': '#c7c1e1',
            'peach1': '#d45b65',
            'peach2': '#f4a198',
            'peach3': '#fbdad2',
            'orange1': '#f7a600',
            'orange2': '#fece43',
            'orange3': '#ffe7b6',
            'green1': '#008878',
            'green2': '#8acbb7',
            'green3': '#d6ebe1',
            'yellow1': '#dedc00',
            'yellow2': '#f6e945',
            'yellow3': '#fff8bd',
            'white': '#ffffff',
            'black': '#000000',
        }
