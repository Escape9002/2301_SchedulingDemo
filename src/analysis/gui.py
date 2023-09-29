
from pathlib import Path
from sys import path as sys_path

project_root_path = Path(Path(__file__).parent, '..', '..')
sys_path.append(str(project_root_path.resolve()))

import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image

from numpy import (
    array,
    newaxis,
    mean,
    round as np_round,
)
import numpy as np

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
)
from matplotlib.figure import (
    Figure,
)
from matplotlib import (
    colormaps,
)

from src.config.config import (
    Config,
)
from src.config.config_gui import (
    ConfigGUI,
)
from src.data.scheduling_data import (
    SchedulingData,
)


def get_width_rescale_constant_aspect_ratio(
        image: Image,
        new_height_px,
) -> int:
    new_width_px = int(new_height_px / image.height * image.width)
    return new_width_px


class App(tk.Tk):

    def __init__(
            self,
    ) -> None:

        super().__init__()
        self.configure(bg='white')
        self.attributes('-fullscreen', True)

        self.config = Config()
        self.config_gui = ConfigGUI()

        self.window_width = self.winfo_screenwidth()
        self.window_height = self.winfo_screenheight()

        self.countdown_toggle = False
        self.countdown_value = 0

        # SIMS
        self.sim_main = SchedulingData(config=self.config)
        self.secondary_simulations = {
            learner_name: SchedulingData(config=self.config)
            for learner_name in self.config_gui.learned_agents.keys()
        }
        self.update_secondary_simulations()

        self.current_resource_pointer = 0
        self.resources_per_user = {
            user_id: 0
            for user_id in range(4)
        }

        # LIFETIME STATS
        self.lifetime_stats = {
            'self': {
                'sumrate': [],
                'fairness': [],
                'timeouts': [],
                'overall': [],
            }
        }
        for learner_name in self.config_gui.learned_agents.keys():
            self.lifetime_stats[learner_name] = {
                'sumrate': [],
                'fairness': [],
                'timeouts': [],
                'overall': [],
            }
        self.maximum_reward_achieved = 0.1

        # ARITHMETIC
        self.channel_img_height = int(self.config_gui.label_user_font[1]*1.2)
        self.label_img_height = int(self.config_gui.label_img_users_height_scale * self.window_height)
        self.logo_img_height = int(self.config_gui.label_img_logos_height_scale * self.window_height)
        self.label_base_station_height = int(self.config_gui.label_img_base_station_height_scale * self.window_height)

        self._gui_setup()

    def _gui_setup(
            self,
    ) -> None:

        # Frames
        self.frame_scenario = tk.Frame(master=self, width=0.7 * self.window_width, height=1.0 * self.window_height,
                                       **self.config_gui.frames_config)
        self.frame_scenario.place(relx=0.0)

        self.frame_resource_grid = tk.Frame(master=self.frame_scenario, width=.15 * self.window_width, height=1.0 * self.window_height,
                                            **self.config_gui.frames_config)
        self.frame_resource_grid.place(relx=0.8)
        self.frame_resource_grid.pack_propagate(False)

        self.frame_screen_selector = tk.Frame(master=self, width=0.3 * self.window_width, height=0.1 * self.window_height, **self.config_gui.frames_config)
        self.frame_screen_selector.place(relx=.7)
        self.frame_screen_selector.pack_propagate(False)

        # make a subframe that holds all the resources, easier to center
        self.subframe_resource_grid = tk.Frame(master=self.frame_resource_grid,
                                               **self.config_gui.frames_config)
        self.subframe_resource_grid.pack(expand=True)

        # subframe results allocation, rhs of screen, swaps with stats subframe
        self.frame_results = tk.Frame(master=self, width=.3 * self.window_width, height=0.9 * self.window_height,
                                      **self.config_gui.frames_config)
        self.frame_results.place(relx=.7, rely=.1)
        self.frame_results.pack_propagate(False)
        self.subframe_allocations_results = tk.Frame(master=self.frame_results, height=0.7 * self.window_height, **self.config_gui.frames_config)
        self.subframe_instant_stats_results = tk.Frame(master=self.frame_results, **self.config_gui.frames_config)
        self.separator_after_allocations = ttk.Separator(self.frame_results, orient='horizontal')
        self.subframe_allocations_results.pack(expand=True)
        self.separator_after_allocations.pack(fill=tk.X)
        self.subframe_instant_stats_results.pack()

        self.label_results_title = tk.Label(self.subframe_allocations_results, text='Last Allocations', **self.config_gui.labels_config)
        self.label_results_title.pack(expand=True, ipady=5)
        self.subframe_allocations = tk.Frame(master=self.subframe_allocations_results, **self.config_gui.frames_config)
        self.subframe_allocations.pack(expand=True)

        self.subframes_allocations = {
            allocator_name: tk.Frame(master=self.subframe_allocations, **self.config_gui.frames_config)
            for allocator_name in self.config_gui.allocator_names
        }
        for subframe_allocation in self.subframes_allocations.values():
            subframe_allocation.pack(side=tk.LEFT, padx=20)

        # subframe stats, rhs of screen, swaps with subframe allocation results
        self.frame_stats = tk.Frame(master=self, width=.3 * self.window_width, height=0.9 * self.window_height,
                                    **self.config_gui.frames_config)
        self.frame_stats.place(relx=.7, rely=0.1)
        self.frame_stats.pack_propagate(False)
        self.subframe_countdown_button = tk.Frame(master=self.frame_stats, **self.config_gui.frames_config)
        self.subframe_instant_stats = tk.Frame(master=self.frame_stats, **self.config_gui.frames_config)
        self.subframe_lifetime_stats = tk.Frame(master=self.frame_stats, **self.config_gui.frames_config)
        self.separator_after_countdown = ttk.Separator(self.frame_stats, orient='horizontal')
        self.separator_after_instant_stats = ttk.Separator(self.frame_stats, orient='horizontal')
        self.subframe_countdown_button.pack(expand=True)
        self.separator_after_countdown.pack(fill=tk.X, expand=True)
        self.subframe_lifetime_stats.pack(expand=True)
        self.separator_after_instant_stats.pack(fill=tk.X, expand=True)
        self.subframe_instant_stats.pack()

        self.selectable_frames = {
            'AllocationResults': self.frame_stats,
            'Stats': self.frame_results,
        }

        self.subframe_logos = tk.Frame(master=self.frame_scenario, **self.config_gui.frames_config)
        self.subframe_logos.place(relx=0.0, rely=0.0)

        self.subframes_users = [
            tk.Frame(master=self.frame_scenario, **self.config_gui.frames_config)
            for _ in range(4)
        ]
        self.subframes_users[0].place(relx=0.1, rely=0.25)
        self.subframes_users[1].place(relx=0.5, rely=0.2)
        self.subframes_users[2].place(relx=0.2, rely=0.7)
        self.subframes_users[3].place(relx=0.45, rely=0.6)

        self.subframe_base_station = tk.Frame(master=self.frame_scenario, **self.config_gui.frames_config)
        self.subframe_base_station.place(relx=0.01, rely=0.55)

        # screen change buttons
        self.selected_value_radio_buttons = ''
        self.screen_selector_button_allocations = tk.Button(
            self.frame_screen_selector,
            text='Allocations',
            compound=tk.CENTER,
            command=self.change_to_frame_allocations,
            **self.config_gui.button_screen_selector_config
        )
        self.screen_selector_button_stats = tk.Button(
            self.frame_screen_selector,
            text='Statistics',
            compound=tk.CENTER,
            command=self.change_to_frame_stats,
            **self.config_gui.button_screen_selector_config
        )
        self.screen_selector_button_allocations.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.screen_selector_button_stats.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Logos
        self.images_logos = [
            Image.open(Path(project_root_path, 'src', 'analysis', 'unilogo.png')),
            Image.open(Path(project_root_path, 'src', 'analysis', 'ANT.png')),
            Image.open(Path(project_root_path, 'src', 'analysis', 'sponsoredbybmbf.png')),
            Image.open(Path(project_root_path, 'src', 'analysis', 'momentum.jpg')),
            Image.open(Path(project_root_path, 'src', 'analysis', 'FunKI_Logo_final_4C.png')),
        ]

        self.tk_image_logos = [
            ImageTk.PhotoImage(image_logo.resize((
                get_width_rescale_constant_aspect_ratio(image_logo, self.logo_img_height),
                self.logo_img_height,
            )))
            for image_logo in self.images_logos
        ]

        self.labels_img_logos = [
            tk.Label(self.subframe_logos, image=tk_image_logo, **self.config_gui.label_user_text_config)
            for tk_image_logo in self.tk_image_logos
        ]

        for label_img_logo in self.labels_img_logos:
            label_img_logo.pack(side=tk.LEFT, padx=10, pady=10)

        # Title Line
        self.label_title = tk.Label(self.frame_scenario, text='Play vs. AI!', **self.config_gui.label_title_text_config)
        self.label_title.place(relx=0.02, rely=0.12)

        # Users
        self.images_channelstrength = [
            Image.open(Path(project_root_path, 'src', 'analysis', 'low.png')),
            Image.open(Path(project_root_path, 'src', 'analysis', 'medlow.png')),
            Image.open(Path(project_root_path, 'src', 'analysis', 'medhigh.png')),
            Image.open(Path(project_root_path, 'src', 'analysis', 'high.png')),
        ]
        self.tk_images_channel_strength = [
            ImageTk.PhotoImage(image_channel_strength.resize((
                get_width_rescale_constant_aspect_ratio(image_channel_strength, self.channel_img_height),
                self.channel_img_height,
            )))
            for image_channel_strength in self.images_channelstrength
        ]

        self.image_base_station = Image.open(Path(project_root_path, 'src', 'analysis', 'base_station.png'))
        self.tk_image_base_station = ImageTk.PhotoImage(self.image_base_station.resize((
            get_width_rescale_constant_aspect_ratio(self.image_base_station, self.label_base_station_height),
            self.label_base_station_height,
        )))
        self.label_image_base_station = tk.Label(
            self.subframe_base_station,
            image=self.tk_image_base_station,
            bg='white',
        )
        self.label_image_base_station.pack()

        self.images_users = [
            Image.open(Path(project_root_path, 'src', 'analysis', '1.png')),
            Image.open(Path(project_root_path, 'src', 'analysis', '2.png')),
            Image.open(Path(project_root_path, 'src', 'analysis', '3.png')),
            Image.open(Path(project_root_path, 'src', 'analysis', 'whambulance.png')),
        ]

        self.tk_images_users = [
            ImageTk.PhotoImage(image_user.resize((
                get_width_rescale_constant_aspect_ratio(image_user, self.label_img_height),
                self.label_img_height,
            )))
            for image_user in self.images_users
        ]

        self.labels_img_users = [
            tk.Label(self.subframes_users[user_id],
                     image=self.tk_images_users[user_id],
                     highlightbackground=self.config_gui.user_colors[user_id],
                     **self.config_gui.label_user_image_config)
            for user_id in range(4)
        ]
        # Bind callbacks to the user images
        for label, callback in zip(
                self.labels_img_users,
                [
                    self.callback_button_user_0,
                    self.callback_button_user_1,
                    self.callback_button_user_2,
                    self.callback_button_user_ambulance,

                ]):
            label.bind('<Button-1>', callback)

        for label_img_user in self.labels_img_users:
            label_img_user.pack(pady=10)

        self.labels_text_users_wants = [
            tk.Label(subframe_user, **self.config_gui.label_user_text_config)
            for subframe_user in self.subframes_users
        ]
        self.labels_text_users_channel_strength = [
            tk.Label(subframe_user, **self.config_gui.label_user_text_config)
            for subframe_user in self.subframes_users
        ]

        self.update_user_text_labels()

        for label_text_user in self.labels_text_users_wants:
            label_text_user.pack()
        for label_text_user in self.labels_text_users_channel_strength:
            label_text_user.pack()

        # Resource Grid main
        self.label_text_resource_grid = tk.Label(self.subframe_resource_grid,
                                                 text='Resources',
                                                 **self.config_gui.label_user_text_config)
        self.label_text_resource_grid.pack(side=tk.TOP, pady=10)

        self.labels_resource_grid = [
            tk.Label(self.subframe_resource_grid, text='', **self.config_gui.label_resource_config)
            for _ in range(self.config.num_total_resource_slots)
        ]

        for label_resource_grid_id in range(len(self.labels_resource_grid)):
            self.labels_resource_grid[label_resource_grid_id].pack(side=tk.TOP)

        # Separator Vertical
        self.separator_vertical = ttk.Separator(self, orient='vertical')
        self.separator_vertical.place(relx=0.7, rely=0, relwidth=0.0, relheight=1)

        # Countdown Button
        self.image_stopwatch = Image.open(Path(project_root_path, 'src', 'analysis', 'stopwatch.png'))
        self.tk_image_stopwatch = ImageTk.PhotoImage(self.image_stopwatch.resize((
                get_width_rescale_constant_aspect_ratio(self.image_stopwatch, self.label_img_height),
                self.label_img_height,
            )))
        self.pixel = tk.PhotoImage(width=1, height=1)  # workaround so button doesn't resize on click

        self.button_timer = tk.Button(
            self.subframe_countdown_button,
            text='',
            image=self.tk_image_stopwatch,
            compound=tk.CENTER,
            command=self.callback_button_timer,
            borderwidth=30,
            **self.config_gui.button_panic_config
        )
        self.button_timer.pack(side=tk.TOP, fill=tk.BOTH)

        # Instant Stats
        self.label_instant_stats = tk.Label(self.subframe_instant_stats, text='Scores', **self.config_gui.labels_config)
        self.label_instant_stats.pack()

        self.fig_instant_stats = Figure(figsize=(5.5, 1.8))
        self.ax_instant_stats = self.fig_instant_stats.add_subplot()
        self.ax_instant_stats.axis('tight')
        self.ax_instant_stats.axis('off')

        data = array([[0]*4]*4)
        self.draw_instant_stats_table(data=data, ax=self.ax_instant_stats)
        self.fig_instant_stats.tight_layout()

        self.canvas_instant_stats = FigureCanvasTkAgg(self.fig_instant_stats, master=self.subframe_instant_stats)
        self.canvas_instant_stats.draw()

        self.canvas_instant_stats.get_tk_widget().pack(expand=True)

        # FIG lifetime stats
        self.label_lifetime_stats = tk.Label(self.subframe_lifetime_stats,
                                             text='Overall Performance Since Start',
                                             **self.config_gui.labels_config)
        self.label_lifetime_stats.pack(side=tk.TOP)

        fig = Figure(figsize=(5.5, 2.5), dpi=100)
        self.ax = fig.add_subplot()
        t = range(4)
        self.bars_primary = self.ax.barh(
            t,
            width=[0, 0, 0, 0],
            height=0.8,
            color=self.config_gui.cp3['blue3'],
            edgecolor='black',
        )
        self.ax.set_xlim([0, 40])
        self.ax.set_yticks([0, 1, 2, 3], reversed(self.config_gui.allocator_names), fontsize=11)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.set_xticks([])
        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self.subframe_lifetime_stats)  # A tk.DrawingArea.
        self.canvas.draw()

        self.canvas.get_tk_widget().pack(side=tk.TOP)

        # Allocation Resource Grids
        self.labels_allocation_resource_grids = {
            allocator_name: [
                tk.Label(allocator_subframe, text='', **self.config_gui.label_resource_small_config)
                for _ in range(self.config.num_total_resource_slots)
            ]
            for allocator_name, allocator_subframe in self.subframes_allocations.items()
        }
        self.labels_allocation_title = {
            tk.Label(allocator_subframe, text=allocator_name, **self.config_gui.label_allocations_titles_config)
            for allocator_name, allocator_subframe in self.subframes_allocations.items()
        }
        for label_allocation_resource_grid in self.labels_allocation_resource_grids.values():
            for label_resource_grid_id in range(len(label_allocation_resource_grid)):
                label_allocation_resource_grid[label_resource_grid_id].pack(side=tk.TOP)
        for label_allocation_title in self.labels_allocation_title:
            label_allocation_title.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        # Instant Stats allocation
        self.label_instant_stats_results = tk.Label(self.subframe_instant_stats_results, text='Scores',
                                                    **self.config_gui.labels_config)
        self.label_instant_stats_results.pack()

        self.fig_instant_stats_results = Figure(figsize=(5.5, 1.8))
        self.ax_instant_stats_results = self.fig_instant_stats_results.add_subplot()
        self.ax_instant_stats_results.axis('tight')
        self.ax_instant_stats_results.axis('off')

        data = array([[0] * 4] * 4)
        self.draw_instant_stats_table(data=data, ax=self.ax_instant_stats_results)
        self.fig_instant_stats_results.tight_layout()

        self.canvas_instant_stats_results = FigureCanvasTkAgg(self.fig_instant_stats_results, master=self.subframe_instant_stats_results)
        self.canvas_instant_stats_results.draw()

        self.canvas_instant_stats_results.get_tk_widget().pack(expand=True)

    def check_loop(
            self,
    ) -> None:

        if self.countdown_toggle:
            if self.countdown_value == 0:
                self.evaluate_allocation()
                self.countdown_value = self.config_gui.countdown_reset_value_seconds

            self.countdown_value -= 1
            self.button_timer.configure(text=f'{self.countdown_value}', image=self.pixel)  # workaround so button doesn't resize on click
            self.after(1000, self.check_loop)

    def change_to_frame_allocations(
            self,
    ) -> None:

        for frame in self.selectable_frames.values():
            self.frame_results.tkraise(aboveThis=frame)

    def change_to_frame_stats(
            self,
    ) -> None:

        for frame in self.selectable_frames.values():
            self.frame_stats.tkraise(aboveThis=frame)


    def callback_button_timer(
            self,
    ) -> None:

        self.countdown_toggle = not self.countdown_toggle
        if self.countdown_toggle:
            self.countdown_value = self.config_gui.countdown_reset_value_seconds
            self.after(1000, self.check_loop)

        if not self.countdown_toggle:
            self.button_timer.configure(text='', image=self.tk_image_stopwatch)

    def callback_button_user_0(
            self,
            event,
    ) -> None:
        self.allocate_resource(user_id=0)

    def callback_button_user_1(
            self,
            event,
    ) -> None:
        self.allocate_resource(user_id=1)

    def callback_button_user_2(
            self,
            event,
    ) -> None:
        self.allocate_resource(user_id=2)

    def callback_button_user_ambulance(
            self,
            event,
    ) -> None:
        self.allocate_resource(user_id=3)

    def allocate_resource(
            self,
            user_id,
    ) -> None:

        self.labels_resource_grid[self.current_resource_pointer].config(bg=self.config_gui.user_colors[user_id])
        self.current_resource_pointer = self.current_resource_pointer + 1
        self.resources_per_user[user_id] += 1
        if self.current_resource_pointer == self.config.num_total_resource_slots:
            self.after(100, self.evaluate_allocation)

    def fill_resource_grid(
            self,
            resource_grid: list,
            allocation: dict,
    ) -> None:

        for resource_id in range(self.config.num_total_resource_slots):
            resource_grid[resource_id].config(bg='white')

        resource_pointer = 0
        for user_id, number_of_resources in allocation.items():
            for resource_number in range(int(number_of_resources)):
                resource_grid[resource_pointer].config(bg=self.config_gui.user_colors[user_id])
                resource_pointer += 1


    def evaluate_allocation(
            self,
    ) -> None:

        # get own action
        action = array(list(self.resources_per_user.values())) / self.config.num_total_resource_slots
        action = action.astype('float32')
        self.fill_resource_grid(resource_grid=self.labels_allocation_resource_grids[self.config_gui.allocator_names[0]],
                                allocation=self.get_allocated_slots(percentage_allocation_solution=action,
                                                                    sim=self.sim_main))
        reward, reward_components = self.sim_main.step(percentage_allocation_solution=action)

        instant_stats = [[
            reward_components['sum rate'],
            reward_components['fairness score'],
            reward_components['prio jobs missed'],
            reward
        ]]

        self.lifetime_stats['self']['sumrate'].append(reward_components['sum rate'])
        self.lifetime_stats['self']['fairness'].append(reward_components['fairness score'])
        self.lifetime_stats['self']['timeouts'].append(reward_components['prio jobs missed'])
        self.lifetime_stats['self']['overall'].append(reward)

        # get learner actions
        for learner_name, learner in self.config_gui.learned_agents.items():
            action = learner.call(self.secondary_simulations[learner_name].get_state()[newaxis]).numpy().squeeze()
            self.fill_resource_grid(resource_grid=self.labels_allocation_resource_grids[self.config_gui.learned_agents_display_names[learner_name]],
                                    allocation=self.get_allocated_slots(percentage_allocation_solution=action,
                                                                        sim=self.secondary_simulations[learner_name]))

            reward, reward_components = self.secondary_simulations[learner_name].step(percentage_allocation_solution=action)

            instant_stats.append(
                [
                    reward_components['sum rate'],
                    reward_components['fairness score'],
                    reward_components['prio jobs missed'],
                    reward
                ]
            )

            self.lifetime_stats[learner_name]['sumrate'].append(reward_components['sum rate'])
            self.lifetime_stats[learner_name]['fairness'].append(reward_components['fairness score'])
            self.lifetime_stats[learner_name]['timeouts'].append(reward_components['prio jobs missed'])
            self.lifetime_stats[learner_name]['overall'].append(reward)

        self.update_user_text_labels()

        mean_rewards = [mean(self.lifetime_stats[member]['overall']) for member in self.lifetime_stats.keys()]
        for mean_reward in mean_rewards:
            if mean_reward > self.maximum_reward_achieved:
                self.maximum_reward_achieved = mean_reward
        self.ax.set_xlim([0, self.maximum_reward_achieved * 1.05])
        for bar, value in zip(reversed(self.bars_primary), mean_rewards):
            bar.set_width(value)

        self.canvas.draw()

        # reset resources
        self.current_resource_pointer = 0
        self.resources_per_user = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
        }
        for label_resource in self.labels_resource_grid:
            label_resource.config(bg='white')

        self.countdown_value = self.config_gui.countdown_reset_value_seconds
        self.update_secondary_simulations()

        self.ax_instant_stats.tables[0].remove()
        self.ax_instant_stats_results.tables[0].remove()
        instant_stats = np_round(array(instant_stats), 1)

        from matplotlib.colors import LinearSegmentedColormap
        colormap = LinearSegmentedColormap.from_list('', [self.config_gui.cp3['red2'], self.config_gui.cp3['blue3'], self.config_gui.cp3['blue2']])
        colormap_reversed = LinearSegmentedColormap.from_list('', [self.config_gui.cp3['blue2'], self.config_gui.cp3['blue3'], self.config_gui.cp3['red2']])

        cmaps = [colormap, colormap, colormap_reversed, colormap]
        colors = [[[0, 0, 0, 0] for _ in range(4)] for _ in range(4)]
        for column_index, cmap in enumerate(cmaps):

            column_stats = instant_stats[:, column_index].copy()
            column_stats += min(column_stats)  # transform to positive space
            if max(column_stats) > 0:
                column_stats = column_stats / max(column_stats)  # transform to [0, 1]

            # set color map
            column_colors = cmap(column_stats)

            for column_color_id, column_color in enumerate(column_colors):
                colors[column_color_id][column_index] = list(column_color)

        self.draw_instant_stats_table(data=instant_stats, ax=self.ax_instant_stats, colors=colors)
        self.draw_instant_stats_table(data=instant_stats, ax=self.ax_instant_stats_results, colors=colors)
        self.canvas_instant_stats.draw()
        self.canvas_instant_stats_results.draw()

    def draw_instant_stats_table(
            self,
            data,
            ax,
            colors=None,
    ) -> None:

        if not colors:
            colors = [['white']*4]*4

        column_labels = ['Transmit', 'Fairness', 'Deaths', 'Overall']
        row_labels = self.config_gui.allocator_names
        table_instant_stats = ax.table(
            cellText=data,
            cellColours=colors,
            colLabels=column_labels,
            rowLabels=row_labels,
            rowLoc='right',
            loc='center',
        )
        table_instant_stats.auto_set_font_size(False)
        table_instant_stats.set_fontsize(self.config_gui.table_instant_stats_font_size)
        table_instant_stats.scale(xscale=1.1, yscale=1.5)  # scale cell boundaries

    def get_channel_strength_image(
            self,
            channel_strength,
    ) -> tk.PhotoImage:

        if channel_strength >= 16:
            return self.tk_images_channel_strength[3]
        elif channel_strength >= 9:
            return self.tk_images_channel_strength[2]
        elif channel_strength >= 3:
            return self.tk_images_channel_strength[1]
        elif channel_strength >= 1:
            return self.tk_images_channel_strength[0]
        else:
            raise Exception('Unexpected channel strength')

    def update_user_text_labels(
            self,
    ) -> None:
        # Resource Wants
        for label_text_user_id, label_text_user in enumerate(self.labels_text_users_wants):
            if self.sim_main.users[label_text_user_id].job:
                resources = self.sim_main.users[label_text_user_id].job.size_resource_slots
            else:
                resources = 0
            text = f'Wants: {resources} Resources'
            label_text_user.configure(text=text)
        # Channel Strength                          )
        for label_text_user_id, label_text_user in enumerate(self.labels_text_users_channel_strength):
            channel_strength = self.sim_main.users[label_text_user_id].power_gain
            text = 'Channel: '
            label_text_user.configure(text=text,
                                      image=self.get_channel_strength_image(channel_strength),
                                      compound=tk.RIGHT
                                      )

    def update_secondary_simulations(
            self,
    ) -> None:

        for sec_sim in self.secondary_simulations.values():
            sec_sim.import_state(state=self.sim_main.export_state())

    def get_allocated_slots(
            self,
            percentage_allocation_solution: np.ndarray,
            sim,
    ):
        requested_slots_per_ue = [
            sim.users[ue_id].job.size_resource_slots if sim.users[ue_id].job else 0
            for ue_id in range(len(sim.users))
        ]

        slot_allocation_solution = [
            np.minimum(
                np_round(percentage_allocation_solution[ue_id] * self.config.num_total_resource_slots),
                requested_slots_per_ue[ue_id],
                dtype='float32'
            )
            for ue_id in range(len(sim.users))
        ]

        # grant at most one additional resource if there was rounding down
        if sum(slot_allocation_solution) == sim.resource_grid.total_resource_slots - 1:
            remainders = [
                percentage_allocation_solution[ue_id] * sim.resource_grid.total_resource_slots - slot_allocation_solution[ue_id]
                for ue_id in range(len(sim.users))
            ]
            for ue_id in range(len(sim.users)):
                if remainders[ue_id] > 0:
                    if requested_slots_per_ue[ue_id] > slot_allocation_solution[ue_id]:
                        slot_allocation_solution[ue_id] += 1
                        break

        # Check if the rounding has resulted in more resources distributed than available
        if sum(slot_allocation_solution) > sim.resource_grid.total_resource_slots:
            # if so, remove one resource from a random user
            while sum(slot_allocation_solution) > sim.resource_grid.total_resource_slots:
                random_user_id = self.config.rng.integers(0, len(sim.users))
                if slot_allocation_solution[random_user_id] > 0:
                    slot_allocation_solution[random_user_id] -= 1

        # prepare the allocated slots per ue for metrics calculation
        allocated_slots_per_ue: dict = {
                ue_id: slot_allocation_solution[ue_id]
                for ue_id in range(len(sim.users))
        }

        return allocated_slots_per_ue


if __name__ == '__main__':
    app = App()
    app.mainloop()
