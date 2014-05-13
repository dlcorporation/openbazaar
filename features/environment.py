def after_scenario(context, scenario):
    if hasattr(context, 'proc'):
        for proc in context.proc:
            proc.terminate()
            proc.join()
