import os


def send_notification(message: str):
    """
    Sends a system notification and sanitizes in case of special chars
    """
    from python_search.environment import is_mac

    clean = message.replace("'", "").replace('"', "")

    cmd = f"notify-send '{clean}'"
    if is_mac():
        cmd = f"""osascript -e 'display notification "{clean}"'"""

    os.system(cmd)


def main():
    import fire

    fire.Fire(send_notification)


if __name__ == "__main__":
    main()
