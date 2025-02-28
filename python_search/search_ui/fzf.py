import os
import sys

from python_search.configuration.configuration import PythonSearchConfiguration
from python_search.environment import is_mac


class Fzf:
    PREVIEW_PERCENTAGE_SIZE = 50
    RANK_TIE_BREAK: str = "index"

    def __init__(self, configuration: PythonSearchConfiguration):
        self.configuration = configuration
        self.preview_cmd = f"python_search _preview_entry {{}} "

    def run(self):
        cmd = self.get_cmd()

        os.system(cmd)

    def get_cmd(self):
        cmd = f"""bash -c 'export SHELL=bash ; {self._get_rankging_generate_cmd()} | \
        {self.get_fzf_cmd()} \
        --tiebreak={Fzf.RANK_TIE_BREAK} \
        --extended \
        --reverse \
        --info=inline \
        --cycle \
        --no-hscroll \
        --preview "{self.preview_cmd}" \
        --preview-window=right,{Fzf.PREVIEW_PERCENTAGE_SIZE}%,wrap,border-left \
        --ellipsis='' \
        --hscroll-off=0 \
        -i \
        --border=none \
        --margin=0% \
        --padding=0% \
        {self._run_key("enter")} \
        {self._run_key("ctrl-t", wrap_in_terminal=True)} \
        {self._run_key("double-click")} \
        {self._edit_key('ctrl-e')} \
        {self._edit_key('right-click')} \
        --bind "ctrl-l:clear-query" \
        --bind "ctrl-l:+clear-screen" \
        --bind "ctrl-l:+first" \
        --bind "ctrl-f:first" \
        --bind "ctrl-j:down" \
        --bind "ctrl-k:up" \
        --bind "ctrl-c:execute-silent:(nohup python_search _copy_entry_content {{}})" \
        --bind "ctrl-n:execute-silent:(nohup register_new launch_from_fzf {{}} & )" \
        --bind "ctrl-g:execute-silent:(google_it search {{q}})" \
        --bind "ctrl-y:execute-silent:(python_search _copy_key_only {{}})" \
        --bind "ctrl-p:reload-sync:(ps_search --inline_print=True --predict_next_text=True)" \
        --bind "ctrl-r:reload-sync:(ps_search --inline_print=True)" \
        --bind "ctrl-s:execute-silent:(nohup share_entry share_key {{}})" \
        --bind "ctrl-v:reload-sync:(ps_search --inline_print=True --ignore_recent=True --query {{q}})" \
        --bind "change:reload-sync:(entry_generator generate_for_fzf {{q}}  & {self._get_rankging_generate_cmd()} )" \
        --bind "shift-up:first" \
        --bind "esc:execute-silent:(ps_fzf hide_current_focused_window)" \
        --bind "esc:+clear-query" \
        --bind "ctrl-k:abort" \
        --bind "ctrl-d:abort"  \
        {self._get_fzf_theme()} ; exit 0
        '
        """
        if "ONLY_PRINT" in os.environ:
            print(cmd)
            sys.exit(0)

        return cmd

    def get_fzf_cmd(self):
        if is_mac():
            return "/usr/local/bin/fzf"

        return "fzf"

    def _run_key(self, shortcut: str, wrap_in_terminal=False) -> str:
        wrap_in_terminal_expr = ""
        if wrap_in_terminal:
            wrap_in_terminal_expr = " --wrap_in_terminal=True "

        return f"""--bind "{shortcut}:execute-silent:(nohup run_key {{}}  --query_used {{q}} {wrap_in_terminal_expr} {{}} &)" \
        --bind "{shortcut}:+reload-sync:(sleep 3 && {self._get_rankging_generate_cmd()})" \
        --bind "{shortcut}:+first" \
        --bind "{shortcut}:+clear-screen" """

    def _edit_key(self, shortcut) -> str:
        return f' --bind "{shortcut}:execute-silent:(entries_editor edit_key {{}} & disown )" '

    def _get_fzf_theme(self):
        if self.configuration.get_fzf_theme() == "light":
            return "--color=bg+:#ffffff,bg:#ffffff,hl:#719872,fg:#616161,header:#719872,info:#727100,pointer:#E12672,marker:#E17899,fg+:#616161,preview-bg:#ffffff,prompt:#0099BD,hl+:#719899"

        if self.configuration.get_fzf_theme() in ["dark", "dracula"]:
            return ' --color="fg:#f8f8f2,bg:#282a36,hl:#bd93f9,fg+:#f8f8f2,bg+:#44475a,hl+:#bd93f9,info:#ffb86c,prompt:#50fa7b,pointer:#ff79c6,marker:#ff79c6,spinner:#ffb86c,header:#6272a4" '

        return " "

    def _get_rankging_generate_cmd(self):
        # in mac we need tensorflow to be installed via conda
        return f"ps_search --inline_print=True"


def hide_current_focused_window():
    """Used by fzf to hide the current focused window when pressing esc"""
    os.system(
        """osascript -e 'tell application "System Events" to keystroke "h" using {command down}'"""
    )


def main():
    import fire

    fire.Fire()


if __name__ == "__main__":
    main()
