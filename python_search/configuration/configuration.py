import datetime
from typing import Optional, List, Tuple, Literal

from python_search.entries_group import EntriesGroup
from python_search.features import PythonSearchFeaturesSupport
from python_search.theme import TimeBasedThemeSelector


class PythonSearchConfiguration(EntriesGroup):
    """
    The main configuration of Python Search
    Everything to customize about the application is configurable via code through this class
    """

    APPLICATION_TITLE = "PythonSearchWindow"
    commands: dict
    simple_gui_theme = "SystemDefault1"
    simple_gui_font_size = 14
    _default_tags = None
    tags_dependent_inserter_marks = None
    _initialization_time = None
    _default_text_editor = "vim"
    _fzf_theme = None
    use_webservice = False
    rerank_via_model = False
    entry_geneartion = False

    def __init__(
        self,
        *,
        entries: Optional[dict] = None,
        entries_groups: Optional[List[EntriesGroup]] = None,
        default_tags=None,
        tags_dependent_inserter_marks: Optional[dict[str, Tuple[str, str]]] = None,
        default_text_editor: Optional[str] = None,
        fzf_theme: Literal[
            "light", "dark", "dracula", "default", "automatic"
        ] = "automatic",
        custom_window_size: Optional[Tuple[int, int]] = None,
        use_webservice=False,
        rerank_via_model=False,
        collect_data: bool = False,
        entry_generation=False,
    ):
        """

        :param entries:
        :param entries_groups:
        :param default_tags:
        :param tags_dependent_inserter_marks:
        :param default_text_editor:
        :param fzf_theme: the theme to use for fzf
        :param custom_window_size: the size of the fzf window
        :param use_webservice: if True, the ranking will be generated via a webservice
        :param collect_data: if True, we will collect data about the entries you run in your machine
        """
        if entries:
            self.commands = entries

        if entries_groups:
            self.aggregate_commands(entries_groups)

        self.supported_features: PythonSearchFeaturesSupport = (
            PythonSearchFeaturesSupport.default()
        )

        if default_tags:
            self._default_tags = default_tags

        self.tags_dependent_inserter_marks = tags_dependent_inserter_marks
        self.rerank_via_model = rerank_via_model

        self._initialization_time = datetime.datetime.now()
        self._default_text_editor = default_text_editor
        self._fzf_theme = (
            fzf_theme
            if fzf_theme != "automatic"
            else TimeBasedThemeSelector().get_theme()
        )
        if custom_window_size:
            self._custom_window_size = custom_window_size

        self.use_webservice = use_webservice
        self.collect_data = collect_data
        self.entry_geneartion = entry_generation

    def get_next_item_predictor_model(self):
        """
        Return the model used by the application

        :return:
        """
        version = "v2"

        if version == "v1":
            from python_search.next_item_predictor.next_item_model_v2 import (
                NextItemModelV1,
            )

            return NextItemModelV1()
        else:
            from python_search.next_item_predictor.next_item_model_v2 import (
                NextItemBaseModelV2,
            )

            return NextItemBaseModelV2()

    def get_text_editor(self):
        return self._default_text_editor

    def get_default_tags(self):
        return self._default_tags

    def get_fzf_theme(self):
        return self._fzf_theme

    def get_window_size(self):
        if hasattr(self, "_custom_window_size"):
            return self._custom_window_size
