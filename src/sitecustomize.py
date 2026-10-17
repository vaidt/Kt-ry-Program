"""Activate ASIG Python observation only in an explicitly opted-in child process."""
import os

if os.environ.get("ASIG_RUNTIME_OBSERVER") == "python":
    try:
        from aura_source_identity.runtime import python_observer  # noqa: F401
    except Exception as exc:
        # The parent runner will detect the missing start/module events as UNKNOWN.
        try:
            with open(os.environ.get("ASIG_RUNTIME_LOG", ""), "a", encoding="utf-8") as stream:
                stream.write('{"event":"observer_bootstrap_error","reason":' + repr(str(exc)) + '}\n')
        except OSError:
            pass
