from cleek import config, task

config(prepend_to_path=True)


def _target() -> None:
    from cleeks.module import success

    success()


@task
def test() -> None:
    import multiprocessing

    proc = multiprocessing.Process(target=_target)
    proc.start()

    try:
        proc.join()
    finally:
        proc.kill()
