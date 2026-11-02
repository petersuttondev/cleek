from cleek import task


class Foo:
    pass


@task
def foo(a: Foo) -> None:
    pass
