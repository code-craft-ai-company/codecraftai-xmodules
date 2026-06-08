
class SWAPPABLE_HOOKS:
    # We capture references to sys.stdout and sys.stderr here so we can
    # swap out the file descriptor used by logging for testing purposes
    HOOK_SYS_STDOUT = None
    HOOK_SYS_STDERR = None