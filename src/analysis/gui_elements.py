
import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import src
from src.utils.get_width_rescale_constant_aspect_ratio import (
    get_width_rescale_constant_aspect_ratio,
)


class Scenario(tk.Frame):
    """
    Left hand side of the screen, holds logos, users, their wants, the primary resource grid.
    """

    def __init__(
            self,
            window_width: int,
            window_height: int,
            config_gui: 'src.config.config_gui.ConfigGUI',
            logo_paths: list[Path],
            user_image_paths: list[Path],
            base_station_image_path: Path,
            button_callbacks: list,
            num_total_resource_slots: int,
            **kwargs,
    ) -> None:

        super().__init__(width=0.7 * window_width, height=1.0 * window_height, **kwargs)

        self.logo_img_height = int(config_gui.label_img_logos_height_scale * window_height)
        self.user_img_height = int(config_gui.label_img_user_height_scale * window_height)
        self.base_station_img_height = int(config_gui.label_img_base_station_height_scale * window_height)

        # Logo Bar
        self.frame_logos = tk.Frame(master=self, **config_gui.frames_config)
        self._logo_setup(logo_paths=logo_paths, label_user_text_config=config_gui.label_user_text_config)

        # Title Line
        self.label_title = tk.Label(self, **config_gui.label_title_text_config)

        # Scenario Objects
        self.frame_base_station = BaseStationFrame(
            master=self,
            base_station_image_path=base_station_image_path,
            base_station_img_height=self.base_station_img_height,
            **config_gui.frames_config,
        )
        self.frames_users = [
            UserFrame(
                master=self,
                button_callback=button_callbacks[user_id],
                user_image_path=user_image_paths[user_id],
                user_img_height=self.user_img_height,
                user_color=config_gui.user_colors[user_id],
                label_user_img_config=config_gui.label_user_image_config,
                label_user_text_config=config_gui.label_user_text_config,
                **config_gui.frames_config
            )
            for user_id in range(len(config_gui.user_images))
        ]

        # Primary Resource Grid
        self.frame_resource_grid = tk.Frame(master=self, width=.15 * window_width, height=0.9 * window_height, **config_gui.frames_config)
        self.subframe_resource_grid = tk.Frame(master=self.frame_resource_grid, **config_gui.frames_config)

        self.label_text_resource_grid = tk.Label(self.subframe_resource_grid, **config_gui.label_resource_grid_text_config)
        self.resource_grid = ResourceGrid(self.subframe_resource_grid, config_gui.label_resource_config, num_total_resource_slots)

        self._place_items()

    def _logo_setup(
            self,
            logo_paths: list[Path],
            label_user_text_config: dict,
    ) -> None:

        self.images_logos = [
            Image.open(logo_path)
            for logo_path in logo_paths
        ]

        self.tk_image_logos = [
            ImageTk.PhotoImage(image_logo.resize((
                get_width_rescale_constant_aspect_ratio(image_logo, self.logo_img_height),
                self.logo_img_height,
            )))
            for image_logo in self.images_logos
        ]

        self.labels_img_logos = [
            tk.Label(self.frame_logos, image=tk_image_logo, **label_user_text_config)
            for tk_image_logo in self.tk_image_logos
        ]

    def _place_items(
            self,
    ) -> None:

        self.frame_logos.place(relx=0.0, rely=0.0)
        for label_img_logo in self.labels_img_logos:
            label_img_logo.pack(side=tk.LEFT, padx=10, pady=10)

        self.label_title.place(relx=0.02, rely=0.12)

        self.frames_users[0].place(relx=0.1, rely=0.25)
        self.frames_users[1].place(relx=0.5, rely=0.2)
        self.frames_users[2].place(relx=0.2, rely=0.7)
        self.frames_users[3].place(relx=0.45, rely=0.6)

        self.frame_base_station.place(relx=0.01, rely=0.55)

        self.frame_resource_grid.place(relx=0.8, rely=0.1)
        self.frame_resource_grid.pack_propagate(False)

        self.subframe_resource_grid.pack(expand=True)
        self.label_text_resource_grid.pack(side=tk.TOP, pady=10)
        self.resource_grid.place()


class UserFrame(tk.Frame):
    """
    Frame for a user with an image and text.
    """

    def __init__(
            self,
            button_callback,
            user_image_path: Path,
            user_img_height: int,
            user_color: str,
            label_user_img_config: dict,
            label_user_text_config: dict,
            **kwargs,
    ) -> None:

        super().__init__(**kwargs)

        self.user_image = Image.open(user_image_path)
        self.user_image = self.user_image.resize((
            get_width_rescale_constant_aspect_ratio(self.user_image, user_img_height),
            user_img_height,
        ))
        self.user_tk_image = ImageTk.PhotoImage(self.user_image)

        self.label_user_img = tk.Label(
            self,
            image=self.user_tk_image,
            highlightbackground=user_color,
            **label_user_img_config,
        )
        self.label_user_img.bind('<Button-1>', button_callback)

        self.label_user_text_wants = tk.Label(self, **label_user_text_config)
        self.label_user_text_channel_strength = tk.Label(self, **label_user_text_config)

        self._place_items()

    def _place_items(
            self,
    ) -> None:

        self.label_user_img.pack(pady=10)
        self.label_user_text_wants.pack()
        self.label_user_text_channel_strength.pack()


class BaseStationFrame(tk.Frame):
    """
    Frame for a base station, just an image.
    """

    def __init__(
            self,
            base_station_image_path: Path,
            base_station_img_height: int,
            **kwargs,
    ) -> None:

        super().__init__(**kwargs)

        self.base_station_image = Image.open(base_station_image_path)
        self.base_station_image = self.base_station_image.resize((
            get_width_rescale_constant_aspect_ratio(self.base_station_image, base_station_img_height),
            base_station_img_height,
        ))
        self.base_station_tk_image = ImageTk.PhotoImage(self.base_station_image)
        self.label_base_station_img = tk.Label(
            self,
            image=self.base_station_tk_image,
            bg='white',
        )

        self._place_items()

    def _place_items(
            self,
    ) -> None:

        self.label_base_station_img.pack()


class ScreenSelector(tk.Frame):
    """
    Buttons to switch what is displayed on the right hand side of the screen.
    """

    def __init__(
            self,
            config_gui: 'src.config.config_gui.ConfigGUI',
            window_width: int,
            window_height: int,
            button_commands: list,
            **kwargs,
    ) -> None:

        super().__init__(width=0.3 * window_width, height=0.1 * window_height, **kwargs)

        self.screen_selector_button_allocations = tk.Button(
            self,
            text='Allocations',
            compound=tk.CENTER,
            command=button_commands[0],
            **config_gui.button_screen_selector_config
        )
        self.screen_selector_button_stats = tk.Button(
            self,
            text='Statistics',
            compound=tk.CENTER,
            command=button_commands[1],
            **config_gui.button_screen_selector_config
        )

        self._place_items()

    def _place_items(
            self,
    ) -> None:

        self.screen_selector_button_allocations.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.screen_selector_button_stats.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)


class ScreenResults(tk.Frame):
    """
    One choice of frame for the right hand side of screen. Compares the last allocations of
    all agents (user + learned agents), and their immediate results.
    """

    def __init__(
            self,
            window_height: int,
            window_width: int,
            config_gui: 'src.config.config_gui.ConfigGUI',
            pixels_per_inch: int,
            num_total_resource_slots: int,
            **kwargs,
    ) -> None:

        super().__init__(width=.3 * window_width, height=0.9 * window_height, **kwargs)

        # Frame to hold frame title & resource grids frame
        self.frame_allocations = tk.Frame(master=self, height=0.7 * window_height, **config_gui.frames_config)

        # Frame to hold all schedulers' resource grids
        self.subframe_allocations = tk.Frame(master=self.frame_allocations, **config_gui.frames_config)

        # Title label in allocations frame
        self.label_results_title = tk.Label(self.frame_allocations, text='Last Allocations', **config_gui.labels_config)
        # Frames to hold one resource grid for each scheduler
        self.subframes_allocations = {
            allocator_name: tk.Frame(master=self.subframe_allocations, **config_gui.frames_config)
            for allocator_name in config_gui.allocator_names
        }

        # Resource Grids for each scheduler
        self.resource_grids = {
            allocator_name: ResourceGrid(
                master=allocator_subframe,
                label_config=config_gui.label_resource_small_config,
                num_total_resource_slots=num_total_resource_slots,
                )
            for allocator_name, allocator_subframe in self.subframes_allocations.items()
        }
        # Titles for each grid
        self.labels_resource_grids_title = {
            tk.Label(allocator_subframe, text=allocator_name, **config_gui.label_resource_grid_title_config)
            for allocator_name, allocator_subframe in self.subframes_allocations.items()
        }

        # Frame to hold instant statistics for the last allocation
        self.frame_instant_stats = tk.Frame(master=self, **config_gui.frames_config)

        self.label_instant_stats_title = tk.Label(self.frame_instant_stats, **config_gui.label_instant_stats_title_config)
        self.instant_stats = FigInstantStats(self.frame_instant_stats, fig_width=0.3*window_width/pixels_per_inch, table_config=config_gui.fig_instant_stats_config)

        self._place_items()

    def _place_items(
            self,
    ) -> None:

        self.frame_allocations.pack(expand=True)
        self.label_results_title.pack(expand=True, ipady=5)
        self.subframe_allocations.pack(expand=True)
        for subframe_allocation in self.subframes_allocations.values():
            subframe_allocation.pack(side=tk.LEFT, padx=20)
        self.frame_instant_stats.pack(expand=True)

        for resource_grid in self.resource_grids.values():
            resource_grid.place()
        for label_resource_grid_title in self.labels_resource_grids_title:
            label_resource_grid_title.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self.label_instant_stats_title.pack()
        self.instant_stats.place()


class ScreenStats(tk.Frame):
    """
    One choice of frame for the right hand side of screen. Holds the countdown button,
    instantaneous results of the last allocation, and the lifetime average of
    each schedulers' overall performance.
    """

    def __init__(
            self,
            window_width: int,
            window_height: int,
            config_gui: 'src.config.config_gui.ConfigGUI',
            pixels_per_inch: int,
            button_timer_image_path: Path,
            button_timer_callback,
            **kwargs,
    ) -> None:

        super().__init__(width=.3 * window_width, height=0.9 * window_height, **kwargs)

        button_timer_image_height = int(config_gui.label_img_user_height_scale * window_height)

        # Frames
        self.frame_countdown_button = tk.Frame(master=self, **config_gui.frames_config)
        self.frame_lifetime_stats = tk.Frame(master=self, **config_gui.frames_config)
        self.frame_instant_stats = tk.Frame(master=self, **config_gui.frames_config)

        # Button Timer
        self.image_stopwatch = Image.open(button_timer_image_path)
        self.image_stopwatch = self.image_stopwatch.resize((
            get_width_rescale_constant_aspect_ratio(self.image_stopwatch, button_timer_image_height),
            button_timer_image_height,
        ))
        self.tk_image_stopwatch = ImageTk.PhotoImage(self.image_stopwatch)
        self.pixel = tk.PhotoImage(width=1, height=1)  # workaround so button doesn't resize on click

        self.button_timer = tk.Button(
            self.frame_countdown_button,
            text='',
            image=self.tk_image_stopwatch,
            compound=tk.CENTER,
            command=button_timer_callback,
            **config_gui.button_panic_config,
        )

        # Fig Lifetime Stats
        self.label_lifetime_stats_title = tk.Label(self.frame_lifetime_stats, **config_gui.label_lifetime_stats_title_config)
        self.lifetime_stats = FigLifetimeStats(master=self.frame_lifetime_stats, fig_width=0.3*window_width/pixels_per_inch, **config_gui.fig_lifetime_stats_config)

        # Fig Instant Stats
        self.label_instant_stats_title = tk.Label(self.frame_instant_stats, **config_gui.label_instant_stats_title_config)
        self.instant_stats = FigInstantStats(self.frame_instant_stats, fig_width=0.3*window_width/pixels_per_inch, table_config=config_gui.fig_instant_stats_config)

        self._place_items()

    def _place_items(
            self,
    ) -> None:

        self.frame_countdown_button.pack(expand=True)
        self.frame_lifetime_stats.pack(expand=True)
        self.frame_instant_stats.pack(expand=True)

        self.button_timer.pack(side=tk.TOP, fill=tk.BOTH)

        self.label_lifetime_stats_title.pack()
        self.lifetime_stats.place()

        self.label_instant_stats_title.pack()
        self.instant_stats.place()


class ResourceGrid:
    """
    A resource grid made from vertically stacked boxes that can be colored.
    """

    def __init__(
            self,
            master: tk.Frame,
            label_config: dict,
            num_total_resource_slots: int,
    ) -> None:

        self.pointer: int = 0

        self.labels = [
            tk.Label(master, text='', **label_config)
            for _ in range(num_total_resource_slots)
        ]

    def place(
            self,
    ) -> None:

        for label in self.labels:
            label.pack(side=tk.TOP)

    def allocate(
            self,
            color,
    ) -> int:
        """
        Color the resource succeeding the last accessed resource.
        :param color: Which color
        :return: Index of the colored resource.
        """

        self.labels[self.pointer].config(bg=color)
        self.pointer += 1

        return self.pointer

    def fill(
            self,
            allocation: dict,
            color_dict: dict,
    ) -> None:
        """
        Fill the entire grid with colors according to a given allocation.
        :param allocation: dict[user_id: num_resources]
        :param color_dict:  dict[user_id: color]
        """

        self.clear()

        for user_id, number_of_resources in allocation.items():
            for _ in range(int(number_of_resources)):
                self.allocate(color=color_dict[user_id])

    def clear(
            self,
    ) -> None:
        """
        Color the entire grid white. Reset starting index.
        """

        for label in self.labels:
            label.config(bg='white')

        self.pointer = 0


class FigInstantStats:
    """
    Figure that holds a table to display metrics of the most recent allocation.
    """

    def __init__(
            self,
            master: tk.Frame,
            fig_width: float,
            table_config: dict,
    ) -> None:

        self.fig = plt.Figure(figsize=(fig_width, 0.25*fig_width))
        self.ax = self.fig.add_subplot()
        self.ax.axis('tight')
        self.ax.axis('off')

        self.canvas = FigureCanvasTkAgg(self.fig, master=master)

        data = np.array([[0] * 4] * 4)
        self.fig.tight_layout()
        self.draw_instant_stats_table(data=data, **table_config)
        self.fig.tight_layout()

    def place(
            self,
    ) -> None:

        self.canvas.get_tk_widget().pack(expand=True)

    def clear(
            self,
    ) -> None:

        self.ax.tables[0].remove()

    def draw_instant_stats_table(
            self,
            data: np.ndarray,
            column_labels: list[str],
            row_labels: list[str],
            font_size: int,
            colors: list = None,
    ) -> None:

        if not colors:
            colors = [['white']*4]*4

        table_instant_stats = self.ax.table(
            cellText=data,
            cellColours=colors,
            colLabels=column_labels,
            rowLabels=row_labels,
            rowLoc='right',
            loc='center',
        )
        table_instant_stats.auto_set_font_size(False)
        table_instant_stats.set_fontsize(font_size)
        table_instant_stats.scale(xscale=1.1, yscale=1.5)  # scale cell boundaries

        self.canvas.draw()


class FigLifetimeStats:
    """
    Bar chart of the average overall performance of each allocator.
    """

    def __init__(
            self,
            master: tk.Frame,
            fig_width: float,
            column_labels: list[str],
            font_size: int,
            bar_color: str,
    ) -> None:

        self.maximum_value: float = 0.1  # initialize arbitrarily

        fig = plt.Figure(figsize=(fig_width, 0.4*fig_width))
        self.ax = fig.add_subplot()
        t = range(4)
        self.bars_primary = self.ax.barh(
            t,
            width=[0, 0, 0, 0],
            height=0.8,
            color=bar_color,
            edgecolor='black',
        )
        self.ax.set_xlim([0, 40])
        self.ax.set_yticks(range(len(t)), reversed(column_labels), fontsize=font_size)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.set_xticks([])
        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=master)
        self.canvas.draw()

    def place(
            self,
    ) -> None:

        self.canvas.get_tk_widget().pack(side=tk.TOP)

    def update(
            self,
            values: list,
    ) -> None:

        # Rescale y axis
        for value in values:
            if value > self.maximum_value:
                self.maximum_value = value
        self.ax.set_xlim([0, self.maximum_value * 1.05])

        # Update bars
        for bar, value in zip(reversed(self.bars_primary), values):
            bar.set_width(value)

        self.canvas.draw()